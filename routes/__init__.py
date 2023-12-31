import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


def init_app_routes(app: FastAPI):
    from .query import router as query_router

    app.include_router(query_router, prefix="/api")

    @app.get("/")
    def index():
        return FileResponse(path="view/dist/index.html")

    static_app = FastAPI()
    static_app.mount("/", StaticFiles(directory="view/dist"), name="index")

    @static_app.middleware("http")
    async def add_cache_control_static(request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "public, max-age=2592000"
        return response

    app.mount("/", static_app, name="static")

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time * 1000)
        return response

    @app.middleware("http")
    async def add_cache_control(request: Request, call_next):
        response = await call_next(request)
        if "Cache-Control" not in response.headers:
            if response.headers.get("Content-Type", "") == "application/json":
                # do not apply to route /dicts
                if request.url.path == "/api/dicts":
                    response.headers["Cache-Control"] = "no-store"
                else:
                    response.headers["Cache-Control"] = "public, max-age=300"
            else:
                for tp in ["image", "font", "css", "javascript"]:
                    if tp in response.headers.get("Content-Type", ""):
                        response.headers["Cache-Control"] = "public, max-age=2592000"
                        break
                else:
                    response.headers["Cache-Control"] = "no-store"
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins="*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
