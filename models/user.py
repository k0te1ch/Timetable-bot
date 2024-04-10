from sqlalchemy import BigInteger, Column, String

from bot import db


class User(db.Model):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    course = Column(String(128), nullable=False)
    direction = Column(String(128), nullable=False)
    profile = Column(String(128), nullable=False)
    group = Column(String(128), nullable=False)
