from sqlalchemy import Column, Integer, String, Text, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    volunteer = relationship("Volunteer", uselist=False, back_populates="user")

class Volunteer(Base):
    __tablename__ = "volunteers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    availability = Column(String, nullable=False)
    interests = Column(Text, nullable=False)
    travel_pref = Column(Text, nullable= False)
    activities = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="volunteer")


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(String, nullable=False, default=str(datetime.utcnow))