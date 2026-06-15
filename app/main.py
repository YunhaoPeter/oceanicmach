from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base
import app.models  # noqa: ensure all model tables are created on startup
from app.routers import products
from app.routers import entities

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

app.include_router(products.router)
app.include_router(entities.router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def home():
    from fastapi.responses import HTMLResponse
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(settings.TEMPLATES_DIR))
    template = env.get_template("index.html")
    return HTMLResponse(template.render())

@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}
