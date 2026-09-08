from __future__ import annotations

import secrets
import mimetypes
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

from app.api.routes import router
from app.config import PROJECT_ROOT, Settings, get_settings
from app.llm.redaction import safe_error
from app.services.resources import create_resources


PUBLIC_API_PATHS = {"/api/health", "/api/config/public"}


def create_app(settings: Settings | None = None) -> FastAPI:
    runtime_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        application.state.resources = create_resources(runtime_settings)
        yield

    app = FastAPI(
        title="AGENT-O Agent Card Intake",
        version="0.1.0",
        docs_url="/api/docs" if runtime_settings.app_env == "development" else None,
        redoc_url=None,
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def security(request: Request, call_next):
        if (
            runtime_settings.app_access_token
            and request.url.path.startswith("/api/")
            and request.url.path not in PUBLIC_API_PATHS
            and request.url.path != "/api/docs"
            and not request.url.path.startswith("/api/openapi")
        ):
            authorization = request.headers.get("authorization", "")
            supplied = authorization[7:] if authorization.lower().startswith("bearer ") else request.headers.get("x-app-token", "")
            if not secrets.compare_digest(supplied, runtime_settings.app_access_token):
                return JSONResponse(status_code=401, content={"detail": "Authentication required"})
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; font-src 'self'; "
            "object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        )
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(Exception)
    async def unhandled(_request: Request, exc: Exception):
        detail = safe_error(exc) if runtime_settings.app_env == "development" else "Internal server error"
        return JSONResponse(status_code=500, content={"detail": detail})

    app.include_router(router)

    dist = PROJECT_ROOT / "frontend" / "dist"
    @app.get("/{path:path}", include_in_schema=False)
    async def frontend(path: str):
        candidate = dist / path
        if path and candidate.is_file() and dist in candidate.resolve().parents:
            media_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
            return Response(content=candidate.read_bytes(), media_type=media_type)
        index = dist / "index.html"
        if index.is_file():
            return Response(content=index.read_bytes(), media_type="text/html")
        return JSONResponse(
            status_code=503,
            content={"detail": "Frontend build is unavailable. Run `make build`."},
        )

    return app


app = create_app()
