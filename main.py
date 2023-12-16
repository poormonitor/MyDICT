from fastapi import FastAPI

from meta import meta_description, meta_tags
from routes import init_app_routes
from func import init_dictionary

init_dictionary()

app = FastAPI(
    title="MyDICT",
    version="0.1.0",
    openapi_tags=meta_tags,
    description=meta_description,
)

init_app_routes(app)
