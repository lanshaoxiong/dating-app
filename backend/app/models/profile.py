"""Profile model for user profiles"""

from datetime import datetime
from typing import Literal
from sqlalchemy import String, Integer, Text, DateTime, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry

from app.database import Base


ActivityLevel = Literal['low', 'medium', 'high']
DistanceUnit = Literal['miles', 'kilometers']


class Profile(Base):
    """User profile model with puppy information"""
    
    __tablename__ = "profiles"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Foreign key to user
    user_id: Mapped[str] = mapped_column(
        String(36), 
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Profile information
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Location (PostGIS geometry column)
    # SRID 4326 is WGS84 (standard GPS coordinates)
    location: Mapped[str] = mapped_column(
        Geometry(geometry_type='POINT', srid=4326),
        nullable=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")
    photos: Mapped[list["Photo"]] = relationship(
        "Photo",
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="Photo.order"
    )
    prompts: Mapped[list["Prompt"]] = relationship(
        "Prompt",
        back_populates="profile",
        cascade="all, delete-orphan",
        order_by="Prompt.order"
    )
    preferences: Mapped["UserPreferences"] = relationship(
        "UserPreferences",
        back_populates="profile",
        uselist=False,
        cascade="all, delete-orphan"
    )
    playgrounds: Mapped[list["Playground"]] = relationship(
        "Playground",
        back_populates="profile",
        cascade="all, delete-orphan"
    )
    
    # Indexes on location for spatial queries
    __table_args__ = (
        # Spatial index will be created by Alembic migration
    )
    
    def __repr__(self) -> str:
        return f"<Profile(id={self.id}, name={self.name}, age={self.age})>"


class Photo(Base):
    """Photo model for profile photos"""
    
    __tablename__ = "photos"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Foreign key to profile
    profile_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Photo information
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="photos")
    
    def __repr__(self) -> str:
        return f"<Photo(id={self.id}, profile_id={self.profile_id}, order={self.order})>"


class Prompt(Base):
    """Prompt model for profile prompts and answers"""
    
    __tablename__ = "prompts"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Foreign key to profile
    profile_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Prompt information
    question: Mapped[str] = mapped_column(String(500), nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="prompts")
    
    def __repr__(self) -> str:
        return f"<Prompt(id={self.id}, question={self.question[:30]}...)>"


class UserPreferences(Base):
    """User preferences for matching"""
    
    __tablename__ = "user_preferences"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Foreign key to profile
    profile_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Preference fields
    min_age: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_age: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    max_distance: Mapped[float] = mapped_column(Float, nullable=False, default=25.0)
    activity_level: Mapped[str] = mapped_column(
        SQLEnum('low', 'medium', 'high', name='activity_level_enum'),
        nullable=False,
        default='medium'
    )
    distance_unit: Mapped[str] = mapped_column(
        SQLEnum('miles', 'kilometers', name='distance_unit_enum'),
        nullable=False,
        default='miles'
    )
    
    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="preferences")
    
    def __repr__(self) -> str:
        return f"<UserPreferences(profile_id={self.profile_id}, age={self.min_age}-{self.max_age})>"
