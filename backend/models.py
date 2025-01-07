from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    auth0_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String, nullable=True)
    picture = Column(String, nullable=True)

    messages = relationship("Message", back_populates="user")
    channels = relationship("Channel", secondary="user_channels", back_populates="users")

class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("Message", back_populates="channel")
    users = relationship("User", secondary="user_channels", back_populates="channels")
    owner = relationship("User", foreign_keys=[owner_id])

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    channel_id = Column(Integer, ForeignKey("channels.id"))

    user = relationship("User", back_populates="messages")
    channel = relationship("Channel", back_populates="messages")

class UserChannel(Base):
    __tablename__ = "user_channels"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), primary_key=True)

