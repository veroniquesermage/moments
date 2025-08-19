from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
# --- OpenTelemetry (provider+exporter) ---
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import make_asgi_app
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings

# <<< adapte l'IP de ta VM Jaeger >>>
OTEL_ENDPOINT = settings.otel_endpoint

provider = TracerProvider(resource=Resource.create({
    "service.name": "moments-api",
    "service.version": "1.0.0",
    "deployment.environment": "dev",
}))
trace.set_tracer_provider(provider)
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_ENDPOINT)))
# --- fin init OTel ---

from app.core.logger import logger
from app.database import get_db  # instrument SQLAlchemy dans ce module (voir note plus bas)
from app.router import router

# 1) Créer l'app
app = FastAPI(
    title="(Moments) API",
    description="API pour l'application (Moments)",
    version="1.0.0",
)

# 2) CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "https://moments-ep.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3) Instrumenter FastAPI (doit être APRES app = FastAPI)
FastAPIInstrumentor().instrument_app(app)

# 4) Exposer les métriques (Instrumentator + endpoint garanti)
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
app.mount("/metrics", make_asgi_app())  # ceinture + bretelles : /metrics existera toujours

# 5) Middleware DB (inchangé)
@app.middleware("http")
async def db_rollback_middleware(request: Request, call_next):
    gen = get_db()
    request.state.db = await anext(gen)
    try:
        response = await call_next(request)
        return response
    except SQLAlchemyError:
        await request.state.db.rollback()
        return JSONResponse(status_code=500, content={"detail": "Erreur interne de la base de données (rollback)."})
    finally:
        await gen.aclose()

# 6) Handlers d’exceptions (inchangé)
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.info(f"IntegrityError = {exc}")
    return JSONResponse(status_code=400, content={"detail": "Conflit en base de données : contrainte violée."})

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    logger.info(f"SQLAlchemyError = {exc}")
    return JSONResponse(status_code=500, content={"detail": "Erreur interne de la base de données."})

# 7) Routes
app.include_router(router)

@app.get("/")
async def read_root():
    return {"message": "🎁 Bienvenue sur (Moments) avec FastAPI"}
