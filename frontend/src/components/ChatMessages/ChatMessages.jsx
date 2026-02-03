import React, { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './ChatMessages.css';

function ChatMessages({ messages, isTyping, isEmpty, onHintClick }) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
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
            {message.ai_generated ? (
              <>
                {message.isFollowUp && <div className="follow-up-badge">Follow-up</div>}
                {/* Status hint (visible while streaming) */}
                {message.streaming && message.statusHint && (
                  <div className="status-hint">
                    {message.statusHint}
                  </div>
                )}
                {/* Assistant response (streams incrementally) */}
                {message.content && <ReactMarkdown>{message.content}</ReactMarkdown>}
                {message.hints && message.hints.length > 0 && (
                  <div className="message-hints">
                    {message.hints.map((hint, idx) => (
                      <button
                        key={idx}
                        className="hint-button"
                        onClick={() => onHintClick && onHintClick(hint)}
                      >
                        {hint}
                      </button>
                    ))}
                  </div>
                )}
              </>
            ) : (
              message.content
            )}
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
