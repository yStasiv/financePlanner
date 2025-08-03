from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import models
from .database import engine
from .routers import users, finances

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(users.router, tags=["users"])
app.include_router(finances.router, prefix="/finances" ,tags=["finances"],)

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/stats")
async def read_stats(request: Request):
    return templates.TemplateResponse("stats.html", {"request": request})

@app.get("/rating")
async def read_rating(request: Request):
    return templates.TemplateResponse("rating.html", {"request": request})

@app.get("/categories")
async def read_categories_page(request: Request):
    return templates.TemplateResponse("categories.html", {"request": request})

@app.get("/investments")
async def read_categories_page(request: Request):
    return templates.TemplateResponse("investments.html", {"request": request})

@app.get("/advices")
async def read_categories_page(request: Request):
    return templates.TemplateResponse("advices.html", {"request": request})

@app.get("/login")
async def read_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def read_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})