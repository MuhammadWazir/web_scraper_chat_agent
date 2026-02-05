import React, { useState } from 'react';
import './ChatSidebar.css';

function ChatSidebar({ chats, selectedChatId, onSelectChat, onDeleteChat, onNewChat }) {
  const [showMenuFor, setShowMenuFor] = useState(null);

  const handleMenuClick = (e, chatId) => {
    e.stopPropagation();
    setShowMenuFor(showMenuFor === chatId ? null : chatId);
  };

  const handleDelete = (e, chatId) => {
    e.stopPropagation();
    setShowMenuFor(null);
    onDeleteChat(chatId, e);
  };

  return (
    <div className="chats-sidebar">
      <div className="sidebar-header">
        <button className="new-chat-button" onClick={onNewChat}>
          + New Chat
        </button>
      </div>
      <div className="chats-list">
        {chats.length === 0 ? (
          <p className="empty-state">No chats yet. Send a message to start!</p>
        ) : (
          chats.map((chat) => (
            <div
              key={chat.chat_id}
              className={`chat-item ${selectedChatId === chat.chat_id ? 'active' : ''}`}
              onClick={() => onSelectChat(chat.chat_id)}
            >
              <div className="chat-item-content">
                <h3>{chat.title || 'New Chat'}</h3>
              </div>
              <div className="chat-item-actions">
                <button
                  className="menu-btn"
                  onClick={(e) => handleMenuClick(e, chat.chat_id)}
                  title="Menu"
                >
                  ⋮
                </button>
                {showMenuFor === chat.chat_id && (
                  <div className="menu-dropdown" onClick={(e) => e.stopPropagation()}>
                    <button
                      className="delete-menu-btn"
                      onClick={(e) => handleDelete(e, chat.chat_id)}
                    >
                      Delete
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default ChatSidebar;
