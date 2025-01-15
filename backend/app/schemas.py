from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, ForwardRef, Generic, TypeVar
from pydantic import EmailStr
from pydantic import Field

# Type variable for generic search response
T = TypeVar('T')

# Forward references for circular dependencies
Message = ForwardRef('Message')
MessageReaction = ForwardRef('MessageReaction')

class SearchHighlight(BaseModel):
    """Base class for search result highlighting"""
    content: Optional[List[str]] = None
    name: Optional[List[str]] = None
    email: Optional[List[str]] = None
    description: Optional[List[str]] = None
    file_name: Optional[List[str]] = None
    message_content: Optional[List[str]] = None

class SearchResponse(BaseModel, Generic[T]):
    """Generic search response wrapper"""
    total: int
    items: List[T]

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

class FileUploadBase(BaseModel):
    file_name: str
    content_type: Optional[str] = None
    file_size: Optional[int] = None

class FileUploadCreate(FileUploadBase):
    pass

class FileUpload(FileUploadBase):
    id: int
    message_id: int
    s3_key: str
    uploaded_at: datetime
    uploaded_by: int
    is_deleted: bool = False
    channel_id: Optional[int] = None
    message_content: Optional[str] = None
    highlight: Optional[SearchHighlight] = None

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
    edited_at: Optional[datetime] = None
    user_id: int
    channel_id: int
    parent_id: Optional[int] = None
    has_replies: bool = False
    user: UserInChannel
    reactions: List[MessageReaction] = []
    parent: Optional['Message'] = None
    files: List[FileUpload] = []
    highlight: Optional[SearchHighlight] = None

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
    highlight: Optional[SearchHighlight] = None
    member_count: Optional[int] = None

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
    highlight: Optional[SearchHighlight] = None

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

class UserList(BaseModel):
    users: List[User]
    total: int
    has_more: bool

    class Config:
        orm_mode = True

class ChannelList(BaseModel):
    channels: List[Channel]
    total: int
    has_more: bool

    class Config:
        orm_mode = True

class FileList(BaseModel):
    files: List[FileUpload]
    total: int
    has_more: bool

    class Config:
        orm_mode = True

class MessageSearch(Message):
    """Message search result with highlighting"""
    highlight: Optional[SearchHighlight] = None

class UserSearch(User):
    """User search result with highlighting"""
    highlight: Optional[SearchHighlight] = None

class ChannelSearch(Channel):
    """Channel search result with highlighting"""
    highlight: Optional[SearchHighlight] = None
    member_count: Optional[int] = None

class FileSearch(FileUpload):
    """File search result with highlighting"""
    highlight: Optional[SearchHighlight] = None
    channel_id: Optional[int] = None
    message_content: Optional[str] = None

class ChannelRoleBase(BaseModel):
    role: str

class ChannelRole(ChannelRoleBase):
    id: int
    channel_id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class ChannelMemberUpdate(BaseModel):
    user_id: int
    role: Optional[str] = None

class ChannelPrivacyUpdate(BaseModel):
    is_private: bool

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

class AIMessageBase(BaseModel):
    message: str  # Changed from content to message to match database model
    role: str  # 'user' or 'assistant'

class AIMessageCreate(AIMessageBase):
    pass

class AIMessage(AIMessageBase):
    id: int
    conversation_id: int
    channel_id: int
    user_id: int
    timestamp: datetime = Field(alias='created_at')
    parameters: Optional[dict] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class AIConversationBase(BaseModel):
    channelId: int = Field(alias='channel_id')

class AIConversationCreate(AIConversationBase):
    pass

class AIConversation(AIConversationBase):
    id: int
    userId: int = Field(alias='user_id')
    messages: List[AIMessage]
    createdAt: datetime = Field(alias='created_at')
    updatedAt: Optional[datetime] = Field(alias='last_message')  # Made optional

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class AIConversationList(BaseModel):
    conversations: List[AIConversation]

    class Config:
        orm_mode = True

class AIQueryRequest(BaseModel):
    query: str

class AIQueryResponse(BaseModel):
    conversation: AIConversation
    message: AIMessage

    class Config:
        orm_mode = True

class ChannelSummaryResponse(BaseModel):
    summary: str

    class Config:
        orm_mode = True
