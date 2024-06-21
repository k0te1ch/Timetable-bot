from database.database import db
from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, UniqueConstraint
from sqlalchemy.sql import func

# TODO: Добавить дату регистрации аккаунта
# TODO: Добавить роли: бакалавр, специалист (тоже самое, что и бакалавр), магистр, преподаватель, администратор
# TODO: Посмотреть можно ли запихнуть в модель методы модели (-service?)


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("id"),)

    id = Column(BigInteger, primary_key=True, index=True)
    course = Column(String(128), nullable=False)
    direction = Column(String(128), nullable=False)
    profile = Column(String(128), nullable=False)
    group = Column(String(128), nullable=False)
    send_notifications = Column(Boolean, nullable=False, default=True)
    registration_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
