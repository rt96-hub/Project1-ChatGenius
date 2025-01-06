import React from 'react'

interface Message {
  id: number;
  content: string;
  user: string;
}

interface MessageListProps {
  messages: Message[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message) => (
        <div key={message.id} className="bg-gray-100 rounded-lg p-3">
          <strong className="font-semibold text-purple-600">{message.user}: </strong>
          <span className="text-gray-800">{message.content}</span>
        </div>
      ))}
    </div>
  )
}

export default MessageList

