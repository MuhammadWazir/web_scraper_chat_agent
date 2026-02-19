import React from 'react';

export function ChatList({ chats, activeChatId, onSelectChat, onDeleteChat, onNewChat, className = '' }) {
    return (
        <div className={`chat-list ${className}`}>
            <div className="chat-list-header">
                <h3>Chats</h3>
                <button className="new-chat-btn" onClick={onNewChat}>
                    + New
                </button>
            </div>

            <div className="chats">
                {chats.length === 0 ? (
                    <div className="empty-chats">No chats yet</div>
                ) : (
                    chats.map((chat) => (
                        <div
                            key={chat.chat_id}
                            className={`chat-item ${activeChatId === chat.chat_id ? 'active' : ''}`}
                            onClick={() => onSelectChat(chat.chat_id)}
                        >
                            <div className="chat-title">{chat.title || 'New Chat'}</div>
                            <button
                                className="delete-chat-btn"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onDeleteChat(chat.chat_id);
                                }}
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
