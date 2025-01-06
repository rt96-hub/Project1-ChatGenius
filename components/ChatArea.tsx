'use client'

import React, { useState, useEffect } from 'react'
import MessageList from './MessageList'
import MessageInput from './MessageInput'

const ChatArea = () => {
  const [messages, setMessages] = useState<Array<{ id: number; content: string; user: string }>>([])

  useEffect(() => {
    // TODO: Fetch initial messages from the server
  }, [])

  const handleSendMessage = (message: string) => {
    // TODO: Send message to the server
    setMessages([...messages, { id: Date.now(), content: message, user: 'You' }])
  }

  return (
    <div className="flex-1 flex flex-col bg-white">
      <MessageList messages={messages} />
      <MessageInput onSendMessage={handleSendMessage} />
    </div>
  )
}

export default ChatArea

