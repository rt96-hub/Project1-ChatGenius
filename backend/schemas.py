from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, ForwardRef
from pydantic import EmailStr

# Forward references for circular dependencies
Message = ForwardRef('Message')
MessageReaction = ForwardRef('MessageReaction')

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    pass

# Add UserBase schema for channel users
class UserInChannel(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None

    class Config:
        orm_mode = True

class ReactionBase(BaseModel):
    code: str
    is_system: bool = True
    image_url: Optional[str] = None

class ReactionCreate(ReactionBase):
    pass

class Reaction(ReactionBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class MessageReactionCreate(BaseModel):
    reaction_id: int

class MessageReaction(BaseModel):
    id: int
    message_id: int
    reaction_id: int
    user_id: int
    created_at: datetime
    code: Optional[str] = None
    reaction: Reaction
    user: UserInChannel

    class Config:
        orm_mode = True

class MessageReplyCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    channel_id: int
    parent_id: Optional[int] = None
    user: UserInChannel
    reactions: List[MessageReaction] = []
    parent: Optional['Message'] = None

    class Config:
        orm_mode = True

# Update forward references
Message.update_forward_refs(Message=Message, MessageReaction=MessageReaction)
MessageReaction.update_forward_refs(Message=Message)

class ChannelBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_private: Optional[bool] = False
    is_dm: Optional[bool] = False
    join_code: Optional[str] = None

class ChannelCreate(ChannelBase):
    pass

class DMCreate(BaseModel):
    user_ids: List[int]  # The IDs of users to start a DM with
    name: Optional[str] = None  # Optional group name for multi-user DMs

class Channel(ChannelBase):
    id: int
    created_at: datetime
    owner_id: int
    users: List[UserInChannel] = []
    messages: List[Message] = []

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    bio: Optional[str] = None

class UserCreate(UserBase):
    auth0_id: str

class UserBioUpdate(BaseModel):
    bio: str

class UserNameUpdate(BaseModel):
    name: str

class User(UserBase):
    id: int
    auth0_id: str
    is_active: bool
    created_at: datetime
    channels: List[Channel] = []
    messages: List[Message] = []

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class MessageList(BaseModel):
    messages: List[Message]
    total: int
    has_more: bool

    class Config:
        orm_mode = True

class ChannelRoleBase(BaseModel):
    role: str

class ChannelRole(ChannelRoleBase):
    id: int
    channel_id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class ChannelInvite(BaseModel):
    join_code: str
    channel_id: int

class ChannelMemberUpdate(BaseModel):
    user_id: int
    role: Optional[str] = None

class ChannelPrivacyUpdate(BaseModel):
    is_private: bool
    join_code: Optional[str] = None

class UserWithLastDM(BaseModel):
    user: User
    last_dm_at: Optional[str] = None
    channel_id: Optional[int] = None  # ID of the one-on-one DM channel

    class Config:
        orm_mode = True

class DMCheckResponse(BaseModel):
    channel_id: Optional[int] = None

    class Config:
        orm_mode = True

