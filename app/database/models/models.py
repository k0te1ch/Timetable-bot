from database.database import db
from database.models.mixins import TimestampMixin
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_serializer import SerializerMixin


class User(TimestampMixin, SerializerMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, nullable=False)
    vk_id: Mapped[int] = mapped_column(Integer, nullable=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    middle_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=True)
    settings_id: Mapped[int] = mapped_column(ForeignKey("settings.id"), nullable=False)

    role: Mapped["Role"] = relationship("Role", back_populates="users")
    group: Mapped["Group"] = relationship("Group", back_populates="users")
    settings: Mapped["Settings"] = relationship("Settings", back_populates="user")


class Direction(SerializerMixin, db.Model):
    __tablename__ = "directions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    course: Mapped["Course"] = relationship("Course", back_populates="directions")
    profiles: Mapped[list["Profile"]] = relationship("Profile", back_populates="direction")


class Role(SerializerMixin, db.Model):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    users: Mapped[list["User"]] = relationship("User", back_populates="role")


class Profile(SerializerMixin, db.Model):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    direction_id: Mapped[int] = mapped_column(ForeignKey("directions.id"), nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    direction: Mapped["Direction"] = relationship("Direction", back_populates="profiles")
    groups: Mapped[list["Group"]] = relationship("Group", back_populates="profile")


class Group(SerializerMixin, db.Model):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    year_of_study: Mapped[int] = mapped_column(Integer, nullable=False)

    profile: Mapped["Profile"] = relationship("Profile", back_populates="groups")
    users: Mapped[list["User"]] = relationship("User", back_populates="group")


class Faculty(SerializerMixin, db.Model):
    __tablename__ = "faculties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    has_rating_system_access: Mapped[bool] = mapped_column(Boolean, default=False)
    timetable_url: Mapped[str] = mapped_column(String, nullable=False)

    courses: Mapped[list["Course"]] = relationship("Course", back_populates="faculty")


class Course(SerializerMixin, db.Model):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculties.id"), nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    faculty: Mapped["Faculty"] = relationship("Faculty", back_populates="courses")
    directions: Mapped[list["Direction"]] = relationship("Direction", back_populates="course")


class Settings(SerializerMixin, db.Model):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    notifications: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship("User", back_populates="settings")
