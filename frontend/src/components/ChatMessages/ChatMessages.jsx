import React, { useEffect, useRef, useState } from 'react';
import './ChatMessages.css';

function ChatMessages({ messages, isTyping, isEmpty }) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive or typing starts
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  if (isEmpty && !isTyping) {
    return (
      <div className="messages-container empty-messages">
        <h2 className="empty-message-title">How can I help you?</h2>
      </div>
    );
  }

  if (messages.length === 0 && !isTyping && !isEmpty) {
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
      {isTyping && (
        <div className="message ai-message typing-indicator">
          <div className="message-content typing-content">
            <span className="typing-dot"></span>
            <span className="typing-dot"></span>
            <span className="typing-dot"></span>
          </div>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default ChatMessages;
