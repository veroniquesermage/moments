from fastapi import HTTPException
from starlette import status
from opentelemetry import trace

from app.core.config import settings
from app.core.http_clients import google_client

# Tracer OpenTelemetry pour ce module
tracer = trace.get_tracer(__name__)

GOOGLE_TOKEN_ENDPOINT = settings.google_token_endpoint
GOOGLE_CLIENT_ID = settings.google_client_id
GOOGLE_CLIENT_SECRET = settings.google_client_secret
REDIRECT_URI = settings.google_redirect_uri

async def exchange_code_for_tokens(code: str, code_verifier: str) -> dict:
    with tracer.start_as_current_span("google_token_exchange") as span:
        span.set_attribute("oauth.code_length", len(code))
        span.set_attribute("oauth.code_verifier_length", len(code_verifier))
        span.set_attribute("http.url", GOOGLE_TOKEN_ENDPOINT)
        span.set_attribute("http.method", "POST")
        
        data = {
            "grant_type": "authorization_code",
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "code_verifier": code_verifier,
            "redirect_uri": REDIRECT_URI,
        }

        with tracer.start_as_current_span("google_token_post_request") as request_span:
            request_span.set_attribute("http.request_content_length", len(str(data)))
            
            response = await google_client.post(GOOGLE_TOKEN_ENDPOINT, data=data)
            
            request_span.set_attribute("http.status_code", response.status_code)
            request_span.set_attribute("http.response_content_length", len(response.content))

        if response.status_code != 200:
            span.set_attribute("oauth.exchange_failed", True)
            span.set_attribute("http.error_status", response.status_code)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Échec lors de l'échange avec Google"
            )

        span.set_attribute("oauth.exchange_success", True)
        response_data = response.json()
        span.set_attribute("oauth.has_id_token", "id_token" in response_data)
        span.set_attribute("oauth.has_access_token", "access_token" in response_data)
        
        return response_data
