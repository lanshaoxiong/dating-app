"""Messaging models for conversations and messages"""

from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.database import Base


class Conversation(Base):
    """Conversation model for chat threads between matched users"""
    
    __tablename__ = "conversations"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Foreign key to match
    match_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("matches.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Participants (denormalized for easier querying)
    user1_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user2_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
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
        nullable=False,
        index=True  # Index for ordering conversations
    )
    
    # Relationships
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )
    
    # Indexes
    __table_args__ = (
        # Index for finding conversations for a user
        Index('ix_conversations_user1_updated', 'user1_id', 'updated_at'),
        Index('ix_conversations_user2_updated', 'user2_id', 'updated_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, match_id={self.match_id})>"


class Message(Base):
    """Message model for chat messages"""
    
    __tablename__ = "messages"
    
    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    
    # Foreign key to conversation
    conversation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Sender and recipient
    sender_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    recipient_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Message content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Read status
    read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True  # Index for ordering messages
    )
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages"
    )
    
    # Indexes
    __table_args__ = (
        # Index for finding messages in a conversation
        Index('ix_messages_conversation_created', 'conversation_id', 'created_at'),
        # Index for finding unread messages for a user
        Index('ix_messages_recipient_read', 'recipient_id', 'read'),
    )
    
    def __repr__(self) -> str:
        return f"<Message(id={self.id}, sender_id={self.sender_id}, read={self.read})>"
