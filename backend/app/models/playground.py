"""Playground model for favorite playgrounds"""

from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry

from app.database import Base


class Playground(Base):
    """Playground model for marking favorite playgrounds"""
    
    __tablename__ = "playgrounds"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Foreign key to profile
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Playground information
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Location (PostGIS geometry column)
    # SRID 4326 is WGS84 (standard GPS coordinates)
    location: Mapped[str] = mapped_column(
        Geometry(geometry_type='POINT', srid=4326),
        nullable=False
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="playgrounds")
    
    # Indexes on location for spatial queries
    __table_args__ = (
        # Spatial index will be created by Alembic migration
    )
    
    def __repr__(self) -> str:
        return f"<Playground(id={self.id}, name={self.name}, user_id={self.user_id})>"
