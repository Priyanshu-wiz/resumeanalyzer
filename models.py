from sqlalchemy import Columns,text,Integer,String,Foreign_key
from db import Base

class User(Base):
    __tablename__="users"

    id=Columns(Integer,primary_key=True)
    email=Columns(String(100),unique=True)
    password=Columns(String(100))

class Report(Base):
    _tablename="report"
    id=Columns(Integer,primary_key=True)
    user_id=Columns(Integer,Foreign_key=True)
    report=Columns(text)
    result=Columns(text)
