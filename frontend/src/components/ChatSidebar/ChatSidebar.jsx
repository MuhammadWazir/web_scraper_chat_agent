import React, { useState } from 'react';
import './ChatSidebar.css';

function ChatSidebar({ chats, selectedChatId, onSelectChat, onDeleteChat, onCreateChat }) {
  const [newChatTitle, setNewChatTitle] = useState('');
  const [creatingChat, setCreatingChat] = useState(false);

  const handleCreateChat = async () => {
    if (!newChatTitle.trim()) {
      alert('Please enter a chat title');
      return;
    }

    try {
      setCreatingChat(true);
      await onCreateChat(newChatTitle);
      setNewChatTitle('');
    } catch (error) {
      console.error('Error creating chat:', error);
    } finally {
      setCreatingChat(false);
    }
  };

  return (
    <div className="chats-sidebar">
      <div className="sidebar-header">
        <h2>Chats</h2>
        <div className="new-chat-form">
          <input
            type="text"
            placeholder="New chat title..."
            value={newChatTitle}
            onChange={(e) => setNewChatTitle(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleCreateChat()}
            disabled={creatingChat}
          />
          <button
            onClick={handleCreateChat}
            disabled={creatingChat || !newChatTitle.trim()}
            className="create-chat-btn"
          >
            {creatingChat ? 'Creating...' : 'New Chat'}
          </button>
        </div>
      </div>
      <div className="chats-list">
        {chats.length === 0 ? (
          <p className="empty-state">No chats yet. Create one to get started!</p>
        ) : (
          chats.map((chat) => (
            <div
              key={chat.chat_id}
              className={`chat-item ${selectedChatId === chat.chat_id ? 'active' : ''}`}
              onClick={() => onSelectChat(chat.chat_id)}
            >
              <div className="chat-item-content">
                <h3>{chat.title || 'Untitled Chat'}</h3>
                <p className="chat-meta">
                  {new Date(chat.created_at).toLocaleDateString()}
                </p>
              </div>
              <button
                className="delete-chat-btn"
                onClick={(e) => onDeleteChat(chat.chat_id, e)}
                title="Delete chat"
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default ChatSidebar;

