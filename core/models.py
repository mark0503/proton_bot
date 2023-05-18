from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, LargeBinary, Float
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    ex_id = Column(String)
    username = Column(String)
    is_verify = Column(Boolean, default=False)
    balance = Column(Float, default=0.0)


class Captcha(Base):
    __tablename__ = "captcha"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    value = Column(String)
    image_bytes = Column(LargeBinary)


class Airdrop(Base):
    __tablename__ = "airdrop"

    id = Column(Integer, primary_key=True)
    amount = Column(Float, default=0.0)
    is_actice = Column(Boolean, default=True)
    attempts_left = Column(Integer, default=10)
