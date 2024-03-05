from fastapi import FastAPI, Request, Response
import models
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import engine
from database import db_dependency
from starlette import status
from auth import router as auth_router
from models import Volunteer, Announcement, User
from pydantic import BaseModel
from datetime import datetime
from utils import RequiresLoginException, decode_token

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(router=auth_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.exception_handler(RequiresLoginException)
async def exception_handler(request: Request, exc: RequiresLoginException) -> Response:
    ''' this handler allows me to route the login exception to the home page.'''
    return RedirectResponse(url='/login', status_code=status.HTTP_302_FOUND) 

@app.middleware("http")
async def create_auth_header(
    request: Request,
    call_next,):
    '''
    Check if there are cookies set for authorization. If so, construct the
    Authorization header and modify the request (unless the header already
    exists!)
    '''
    if ("Authorization" not in request.headers 
        and "Authorization" in request.cookies
        ):
        access_token = request.cookies["Authorization"]
        
        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                 f"Bearer {access_token}".encode(),
            )
        )
    elif ("Authorization" not in request.headers 
        and "Authorization" not in request.cookies
        ): 
        request.headers.__dict__["_list"].append(
            (
                "authorization".encode(),
                 f"Bearer 12345".encode(),
            )
        )
        
    
    response = await call_next(request)
    return response 

@app.get("/",  response_class=HTMLResponse)
def home_page(request: Request):
    auth_cookie = request.cookies.get("Authorization")
    if not auth_cookie:
        return templates.TemplateResponse("index.html", {"request": request})
    user_id = decode_token(auth_cookie)
    return templates.TemplateResponse("index.html", {"request": request, "userid":user_id})

@app.get("/register",  response_class=HTMLResponse)
def register(request: Request):
    auth_cookie = request.cookies.get("Authorization")
    if not auth_cookie:
        return templates.TemplateResponse("signup.html", {"request": request})
    user_id = decode_token(auth_cookie)
    return templates.TemplateResponse("signup.html", {"request": request, "userid":user_id})


@app.get("/login",  response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/volunteers",  response_class=HTMLResponse)
def volunteers(request: Request, db:db_dependency, city:str=None):
    cities = []
    announcement = db.query(Announcement).all()
    volunteers = db.query(Volunteer).all()
    for user in volunteers:
        if user.city in cities:
            pass
        else:
            cities.append(user.city)
    if city:
        volunteers = db.query(Volunteer).filter(Volunteer.city == city).all()
    auth_cookie = request.cookies.get("Authorization")
    if auth_cookie:
        user_id = decode_token(auth_cookie)
        return templates.TemplateResponse("volunteers.html", {"request": request, "users": volunteers, "userid":user_id, "cities": cities, "announcements":announcement})
    
    return templates.TemplateResponse("volunteers.html", {"request": request, "users": volunteers, "cities": cities, "announcements": announcement})

@app.get("/logout")
async def logout(request:Request, response: Response):
    resp = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    resp.set_cookie("Authorization", "")
    return resp

@app.get("/my-profile")
def my_profile(request: Request, db:db_dependency):
    auth_cookie = request.cookies.get("Authorization")
    if auth_cookie:
        user_id = decode_token(auth_cookie)
        user = db.query(User).filter(User.email == user_id).first().id
        user = db.query(Volunteer).filter(Volunteer.user_id == user).first()
        return templates.TemplateResponse("my-profile.html", {"request": request, "user": user})
    raise RequiresLoginException

class AnnouncementCreateRequest(BaseModel):
    title: str
    content: str

@app.post("/announcements")
async def create_announcement(db:db_dependency, announcement: AnnouncementCreateRequest):
    new_announcement = Announcement(
        title=announcement.title,
        content=announcement.content,
        created_at=str(datetime.utcnow()),
    )

    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)
    return {"message" :"Created"}


@app.get("/announcements")
async def get_announcements(request: Request, db: db_dependency):
    announcements = db.query(Announcement).all()
    return announcements
