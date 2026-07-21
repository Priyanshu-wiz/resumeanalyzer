from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

sqlite_path = os.path.join(os.path.dirname(__file__), "app.db")
engine = create_engine(
    f"sqlite:///{sqlite_path}",
    connect_args={"check_same_thread": False},
)

Sessionlocal = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()
