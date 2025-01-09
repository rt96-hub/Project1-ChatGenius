from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
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

class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_private = Column(Boolean, default=False)
    is_dm = Column(Boolean, default=False)
    join_code = Column(String, nullable=True)

    messages = relationship("Message", back_populates="channel")
    users = relationship("User", secondary="user_channels", back_populates="channels")
    owner = relationship("User", foreign_keys=[owner_id])
    roles = relationship("ChannelRole", back_populates="channel")

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
    user_id = Column(Integer, ForeignKey("users.id"))
    channel_id = Column(Integer, ForeignKey("channels.id"))

    user = relationship("User", back_populates="messages")
    channel = relationship("Channel", back_populates="messages")
    reactions = relationship("MessageReaction", back_populates="message")

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

