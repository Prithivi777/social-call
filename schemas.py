from pydantic import BaseModel
from typing import Annotated
from fastapi import Form
from dataclasses import dataclass

@dataclass
class VolunteerBase:
    user_id: Annotated[str, Form()]
    full_name: Annotated[str, Form()]
    age: Annotated[str, Form()]
    phone: Annotated[str, Form()]
    address: Annotated[str, Form()]
    city: Annotated[str, Form()]
    state: Annotated[str, Form()]
    zip_code: Annotated[str, Form()]
    availability: Annotated[str, Form()]
    travel_pref: Annotated[str, Form()]
    interests: Annotated[str, Form()]

@dataclass
class LoginVolunteer:
    email: Annotated[str, Form()]
    password:Annotated[str, Form()]

@dataclass
class VolunteerFinalBase(VolunteerBase):
    activities: Annotated[str | None, Form()] = None


class VolunteerInDBBase(VolunteerBase):
    id: int

    class Config:
        from_attributes = True

class VolunteerInDB(VolunteerInDBBase):
    password:str


class TokenData(BaseModel):
    email: str

class Token(BaseModel):
    access_token:str
    token_type: str