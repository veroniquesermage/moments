import time
from typing import Optional, Tuple

from jose import jwt
from fastapi import HTTPException
from starlette import status
from opentelemetry import trace

from app.core.config import settings
from app.core.http_clients import google_client
from app.core.logger import logger

# Tracer OpenTelemetry pour cette module
tracer = trace.get_tracer(__name__)

GOOGLE_JWK_URL = settings.jwk_uri

# Cache global JWK : (jwks_data, timestamp)
_jwks_cache: Optional[Tuple[dict, float]] = None
CACHE_TTL = 86400  # 24 heures en secondes


async def get_cached_jwks() -> dict:
    """
    Récupère les clés JWK Google avec cache en mémoire (TTL 24 heures).
    Équivalent Java : Cache<String, Object> avec expireAfterWrite(24, HOURS)
    """
    with tracer.start_as_current_span("google_jwks_cache_check") as span:
        global _jwks_cache

        now = time.time()

        # Cache miss ou cache expiré ?
        if _jwks_cache is None or (now - _jwks_cache[1]) > CACHE_TTL:
            span.set_attribute("jwks.cache_status", "miss")
            logger.info("Cache JWK miss - Fetch depuis Google")

            # Fetch depuis Google (appel réseau) avec trace
            with tracer.start_as_current_span("google_jwks_fetch") as fetch_span:
                fetch_span.set_attribute("http.url", GOOGLE_JWK_URL)
                fetch_span.set_attribute("http.method", "GET")

                jwks = (await google_client.get(GOOGLE_JWK_URL)).json()

                fetch_span.set_attribute("jwks.keys_count", len(jwks.get("keys", [])))

            # Stockage en cache avec timestamp
            _jwks_cache = (jwks, now)

            return jwks
        else:
            span.set_attribute("jwks.cache_status", "hit")
            span.set_attribute("jwks.cache_age_seconds", int(now - _jwks_cache[1]))
            logger.info("Cache JWK hit - Utilisation du cache")
            return _jwks_cache[0]


async def force_refresh_jwks() -> dict:
    """
    Force le refresh du cache JWK (utilisé en cas d'échec de décodage).
    Ignore le TTL et fetch immédiatement depuis Google.
    """
    with tracer.start_as_current_span("google_jwks_force_refresh") as span:
        global _jwks_cache

        span.set_attribute("jwks.refresh_reason", "jwt_decode_failure")
        logger.info("Force refresh du cache JWK")

        # Fetch depuis Google sans vérifier le cache
        with tracer.start_as_current_span("google_jwks_fetch") as fetch_span:
            fetch_span.set_attribute("http.url", GOOGLE_JWK_URL)
            fetch_span.set_attribute("http.method", "GET")
            fetch_span.set_attribute("jwks.forced_refresh", True)

            jwks = (await google_client.get(GOOGLE_JWK_URL)).json()

            fetch_span.set_attribute("jwks.keys_count", len(jwks.get("keys", [])))

        # Mise à jour du cache avec nouvelles clés
        _jwks_cache = (jwks, time.time())

        return jwks


async def verify_google_id_token(id_token: str) -> dict:
    with tracer.start_as_current_span("google_jwt_verification") as span:
        span.set_attribute("jwt.token_length", len(id_token))
        span.set_attribute("jwt.audience", settings.google_client_id)

        jwks = await get_cached_jwks()

        try:
            with tracer.start_as_current_span("jwt_decode") as decode_span:
                decode_span.set_attribute("jwt.attempt", 1)

                payload = jwt.decode(
                    token=id_token,
                    key=jwks,
                    algorithms=["RS256"],
                    audience=settings.google_client_id,
                    options={
                        "verify_iss": False,  # désactive la vérif d'issuer
                        "verify_at_hash": False
                    } # pour simplifier
                )

                decode_span.set_attribute("jwt.decode_success", True)
                decode_span.set_attribute("jwt.user_id", payload.get("sub", "unknown"))

            return payload

        except Exception as e:
            span.set_attribute("jwt.first_attempt_failed", True)
            span.set_attribute("jwt.error_message", str(e))
            logger.warning(f"Échec décodage JWT avec cache - Tentative refresh: {str(e)}")

            # Fallback : force refresh du cache et réessaie UNE fois
            try:
                jwks_fresh = await force_refresh_jwks()

                with tracer.start_as_current_span("jwt_decode_retry") as retry_span:
                    retry_span.set_attribute("jwt.attempt", 2)
                    retry_span.set_attribute("jwt.fallback_after_cache_refresh", True)

                    payload = jwt.decode(
                        token=id_token,
                        key=jwks_fresh,
                        algorithms=["RS256"],
                        audience=settings.google_client_id,
                        options={
                            "verify_iss": False,
                            "verify_at_hash": False
                        }
                    )

                    retry_span.set_attribute("jwt.decode_success", True)
                    retry_span.set_attribute("jwt.user_id", payload.get("sub", "unknown"))

                logger.info("Décodage JWT réussi après refresh du cache JWK")
                span.set_attribute("jwt.fallback_success", True)
                return payload

            except Exception as final_error:
                span.set_attribute("jwt.fallback_failed", True)
                span.set_attribute("jwt.final_error", str(final_error))
                logger.error("Échec décodage JWT même après refresh - Token réellement invalide")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="id_token Google invalide"
                )
