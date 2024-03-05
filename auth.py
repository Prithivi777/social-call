from fastapi import Depends, APIRouter
from starlette import status
from models import User, Volunteer
from schemas import VolunteerFinalBase, TokenData, LoginVolunteer
from database import db_dependency
from fastapi import Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from utils import create_access_token
from dataclasses import dataclass, asdict
from typing import Annotated

templates = Jinja2Templates(directory="templates")


router = APIRouter(
    prefix = '/auth',
    tags = ['auth']
)

@dataclass
class UserIn:
    email: Annotated[str, Form()]
    password: Annotated[str, Form()]

"""This will create a normal user then it will redirect to registration form."""
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(request:Request, db:db_dependency, create_user_request: UserIn = Depends()):
    try:
        create_user_model = User(email=create_user_request.email, password=create_user_request.password)
        db.add(create_user_model)
        db.commit()
        db.refresh(create_user_model)
        return templates.TemplateResponse("register.html", {"request": request, "message": "User Created", "user": create_user_model})
    except Exception as e:
        print(e)
        return templates.TemplateResponse("signup.html", {"request": request, "error": "User already exists"})

"""Route for creating volunteer"""
@router.post("/register-volunteer", status_code=status.HTTP_201_CREATED)
async def create_volunteer(request:Request, db: db_dependency, create_volunteer_request: VolunteerFinalBase = Depends()):
    db_volunteer = db.query(Volunteer).filter(Volunteer.user_id == int(create_volunteer_request.user_id)).first()
    if not db_volunteer:            
        user = db.query(User).filter_by(id=int(create_volunteer_request.user_id)).first()
        if user is None:
            return templates.TemplateResponse("register.html", {"request": request, "error": "User not found!"})
        try:
            db_volunteer = Volunteer(user=user, full_name= create_volunteer_request.full_name, age= create_volunteer_request.age, phone= create_volunteer_request.phone, address= create_volunteer_request.address, city= create_volunteer_request.city, state= create_volunteer_request.state, zip_code= create_volunteer_request.zip_code, availability= create_volunteer_request.availability, interests= create_volunteer_request.interests, travel_pref=create_volunteer_request.travel_pref)
            db.add(db_volunteer)
            db.commit()
            db.refresh(db_volunteer)
            return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
        except Exception as e:
            return templates.TemplateResponse("register.html", {"request": request, "error": "Something went wrong", "user": user})
    for key, value in asdict(create_volunteer_request).items():
        if value is not None:
            setattr(db_volunteer, key, value)
    db.add(db_volunteer)
    db.commit() 
    db.refresh(db_volunteer)
    return RedirectResponse("/volunteers",status_code=status.HTTP_302_FOUND)


@router.post('/login', response_model=TokenData)
async def login(request: Request, db: db_dependency, form_data: LoginVolunteer = Depends()):
    user = db.query(User).filter_by(email=form_data.email).first()
    if user is None:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect email or password"})

    if form_data.password != user.password:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect email or password"})
    
    resp = templates.TemplateResponse("login.html", {"request": request, "message": "1"})
    resp.set_cookie(key="Authorization", value=f"{create_access_token(user.email)}", httponly=True)
    return resp
