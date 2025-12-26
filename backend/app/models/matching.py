"""Matching models for likes, passes, and matches"""

from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class Like(Base):
    """Like model for user likes"""
    
    __tablename__ = "likes"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # User who liked
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # User who was liked
    target_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Constraints
    __table_args__ = (
        # Ensure a user can only like another user once
        UniqueConstraint('user_id', 'target_id', name='uq_like_user_target'),
        # Index for finding mutual likes
        Index('ix_likes_target_user', 'target_id', 'user_id'),
    )
    
    def __repr__(self) -> str:
        return f"<Like(user_id={self.user_id}, target_id={self.target_id})>"


class Pass(Base):
    """Pass model for user passes"""
    
    __tablename__ = "passes"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # User who passed
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # User who was passed
    target_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Constraints
    __table_args__ = (
        # Ensure a user can only pass another user once
        UniqueConstraint('user_id', 'target_id', name='uq_pass_user_target'),
    )
    
    def __repr__(self) -> str:
        return f"<Pass(user_id={self.user_id}, target_id={self.target_id})>"


class Match(Base):
    """Match model for mutual likes"""
    
    __tablename__ = "matches"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # First user in the match
    user1_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Second user in the match
    user2_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True  # Index for ordering by most recent
    )
    
    # Constraints
    __table_args__ = (
        # Ensure only one match between two users
        # We'll enforce user1_id < user2_id in application logic
        UniqueConstraint('user1_id', 'user2_id', name='uq_match_users'),
        # Index for finding matches for a user
        Index('ix_matches_user1_created', 'user1_id', 'created_at'),
        Index('ix_matches_user2_created', 'user2_id', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Match(id={self.id}, user1_id={self.user1_id}, user2_id={self.user2_id})>"
