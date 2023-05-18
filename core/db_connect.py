from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from config import DATABASE_URL


def connect_db():
    engine = create_engine(DATABASE_URL, connect_args=[])
    session = Session(bind=engine.connect())
    return session
