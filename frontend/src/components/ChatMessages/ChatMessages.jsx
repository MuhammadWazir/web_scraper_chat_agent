import React, { useEffect, useRef } from 'react';
import './ChatMessages.css';

function ChatMessages({ messages }) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="messages-container empty-messages">
        <p>No messages yet. Start the conversation!</p>
      </div>
    );
  }

  return (
    <div className="messages-container">
      {messages.map((message) => (
        <div
          key={message.message_id}
          className={`message ${message.ai_generated ? 'ai-message' : 'user-message'}`}
        >
          <div className="message-content">
            {message.content}
          </div>
          <div className="message-meta">
            {new Date(message.created_at).toLocaleString()}
            {message.ai_generated && <span className="ai-badge">AI</span>}
          </div>
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default ChatMessages;

