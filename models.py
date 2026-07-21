from sqlalchemy import Column, Text, Integer, String, ForeignKey
from db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    password = Column(String(100))

class Report(Base):
    __tablename__ = "report"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    report = Column(Text)
    result = Column(Text)
