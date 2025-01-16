from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import sqlalchemy as sa

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    auth0_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)
    bio = Column(String, nullable=True)

    messages = relationship("Message", back_populates="user")
    channels = relationship("Channel", secondary="user_channels", back_populates="users")
    ai_conversations = relationship("AIConversation", back_populates="user")
    ai_messages = relationship("AIMessage", back_populates="user")

class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_private = Column(Boolean, default=False)
    is_dm = Column(Boolean, default=False)

    messages = relationship("Message", back_populates="channel")
    users = relationship("User", secondary="user_channels", back_populates="channels")
    owner = relationship("User", foreign_keys=[owner_id])
    roles = relationship("ChannelRole", back_populates="channel")
    ai_conversations = relationship("AIConversation", back_populates="channel")
    ai_messages = relationship("AIMessage", back_populates="channel")

    __table_args__ = (
        sa.CheckConstraint(
            'NOT is_dm OR (is_dm AND is_private)',
            name='dm_must_be_private'
        ),
    )

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    edited_at = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    channel_id = Column(Integer, ForeignKey("channels.id"))
    parent_id = Column(Integer, ForeignKey("messages.id"), unique=True, nullable=True)
    vector_id = Column(String(36), unique=True, index=True, nullable=True)
    from_ai = Column(Boolean, default=False)

    user = relationship("User", back_populates="messages")
    channel = relationship("Channel", back_populates="messages")
    reactions = relationship("MessageReaction", back_populates="message")
    
    # Add relationships for parent/child messages
    parent = relationship("Message", remote_side=[id], backref="reply", uselist=False)
    files = relationship("FileUpload", back_populates="message")

    __table_args__ = (
        sa.UniqueConstraint('parent_id', name='unique_reply_message'),
    )

class UserChannel(Base):
    __tablename__ = "user_channels"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), primary_key=True)

class ChannelRole(Base):
    __tablename__ = "channel_roles"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    channel = relationship("Channel", back_populates="roles")
    user = relationship("User")

class Reaction(Base):
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), nullable=False, unique=True)
    is_system = Column(Boolean, default=True)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    message_reactions = relationship("MessageReaction", back_populates="reaction")

class MessageReaction(Base):
    __tablename__ = "message_reactions"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    reaction_id = Column(Integer, ForeignKey("reactions.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    message = relationship("Message", back_populates="reactions")
    reaction = relationship("Reaction", back_populates="message_reactions")
    user = relationship("User")

    __table_args__ = (
        sa.UniqueConstraint('message_id', 'reaction_id', 'user_id', name='unique_message_reaction_user'),
    )

class FileUpload(Base):
    __tablename__ = "file_uploads"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"))
    file_name = Column(String(255), nullable=False)
    s3_key = Column(String(512), nullable=False)
    content_type = Column(String(100))
    file_size = Column(Integer)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean, default=False)

    message = relationship("Message", back_populates="files")
    user = relationship("User", foreign_keys=[uploaded_by])

    __table_args__ = (
        sa.Index('idx_file_uploads_message_id', 'message_id'),
        sa.Index('idx_file_uploads_uploaded_by', 'uploaded_by'),
        sa.Index('idx_file_uploads_uploaded_at', 'uploaded_at'),
    )

class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_message = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="ai_conversations")
    channel = relationship("Channel", back_populates="ai_conversations")
    messages = relationship("AIMessage", back_populates="conversation")

class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id"))
    channel_id = Column(Integer, ForeignKey("channels.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, nullable=False)  # 'user' or 'ai'
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    parameters = Column(sa.JSON, nullable=True)

    # Relationships
    conversation = relationship("AIConversation", back_populates="messages")
    user = relationship("User", back_populates="ai_messages")
    channel = relationship("Channel", back_populates="ai_messages")

