import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import './CompactChat.css';

/**
 * A compact chat component styled exactly like the widget.
 * It uses the same layout and CSS classes as the widget-sdk.
 */
function CompactChat({
    client,
    chats,
    messages,
    selectedChatId,
    tempChatId,
    isTyping,
    onSendMessage,
    onNewChat,
    onSelectChat,
    onDeleteChat,
    onHintClick
}) {
    const [isOpen, setIsOpen] = useState(false);
    const [inputValue, setInputValue] = useState('');
    const messagesEndRef = useRef(null);
    const displayChatId = selectedChatId || tempChatId;
    const currentMessages = displayChatId ? (messages[displayChatId] || []) : [];

    useEffect(() => {
        if (isOpen) {
            messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
    }, [currentMessages, isTyping, isOpen]);

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleSend = () => {
        if (!inputValue.trim()) return;
        onSendMessage(inputValue);
        setInputValue('');
    };

    return (
        <div className="compact-chat-wrapper-internal">
            {/* Launcher Button */}
            {!isOpen && (
                <button className="compact-chat-launcher" onClick={() => setIsOpen(true)}>
                    <svg viewBox="0 0 24 24" width="28" height="28">
                        <path fill="currentColor" d="M12,2C6.47,2,2,6.47,2,12c0,2.21,0.72,4.24,1.94,5.88L3,22l4.12-0.94C8.76,21.65,10.32,22,12,22c5.53,0,10-4.47,10-10 S17.53,2,12,2" />
                    </svg>
                </button>
            )}

            {/* Chat Window */}
            {isOpen && (
                <div className="compact-chat-window animated-fade-in">
                    <div className="compact-chat-header">
                        <div className="compact-header-info">
                            <span className="compact-dot"></span>
                            <span className="compact-title">AI Assistant</span>
                        </div>
                        <button className="compact-close-btn" onClick={() => setIsOpen(false)}>×</button>
                    </div>

                    <div className="compact-chat-container">
                        {/* Sidebar */}
                        <div className="compact-chat-list">
                            <div className="compact-chat-list-header">
                                <h3>Chats</h3>
                                <button className="compact-new-chat-btn" onClick={onNewChat}>
                                    + New
                                </button>
                            </div>
                            <div className="compact-chats">
                                {chats.length === 0 ? (
                                    <div className="compact-empty-chats">No chats yet</div>
                                ) : (
                                    chats.map((chat) => (
                                        <div
                                            key={chat.chat_id}
                                            className={`compact-chat-item ${selectedChatId === chat.chat_id ? 'active' : ''}`}
                                            onClick={() => onSelectChat(chat.chat_id)}
                                        >
                                            <div className="compact-chat-title">{chat.title || 'New Chat'}</div>
                                            <button
                                                className="compact-delete-chat-btn"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    onDeleteChat(chat.chat_id, e);
                                                }}
                                            >
                                                ×
                                            </button>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>

                        {/* Main Area */}
                        <div className="compact-chat-area">
                            <div className="compact-messages">
                                {currentMessages.length === 0 && !isTyping && (
                                    <div className="compact-no-messages">
                                        <p>No messages yet. Start the conversation!</p>
                                    </div>
                                )}

                                {currentMessages.map((message, idx) => (
                                    <div
                                        key={message.message_id || idx}
                                        className={`compact-message ${message.ai_generated ? 'assistant' : 'user'}`}
                                    >
                                        {message.ai_generated ? (
                                            <>
                                                {message.isFollowUp && <div className="compact-follow-up-badge">Follow-up</div>}

                                                {(message.streaming || message.statusHint || message.content) && (
                                                    <div className="compact-message-inner">
                                                        {message.streaming && !message.statusHint && !message.content && (
                                                            <div className="compact-typing-indicator-inline">
                                                                <span></span>
                                                                <span></span>
                                                                <span></span>
                                                            </div>
                                                        )}

                                                        {message.statusHint && (
                                                            <div className="compact-status-hint">
                                                                {message.statusHint}
                                                            </div>
                                                        )}

                                                        {message.content && (
                                                            <div className="compact-message-content">
                                                                <ReactMarkdown>{message.content}</ReactMarkdown>
                                                            </div>
                                                        )}
                                                    </div>
                                                )}

                                                {message.hints && message.hints.length > 0 && (
                                                    <div className="compact-message-hints">
                                                        {message.hints.map((hint, hintIdx) => (
                                                            <button
                                                                key={hintIdx}
                                                                className="compact-hint-button"
                                                                onClick={() => onHintClick && onHintClick(hint)}
                                                            >
                                                                {hint}
                                                            </button>
                                                        ))}
                                                    </div>
                                                )}
                                            </>
                                        ) : (
                                            <div className="compact-message-content">{message.content}</div>
                                        )}
                                    </div>
                                ))}

                                {isTyping && (
                                    <div className="compact-message assistant compact-typing-indicator">
                                        <span></span>
                                        <span></span>
                                        <span></span>
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>

                            <div className="compact-chat-input-area">
                                <textarea
                                    className="compact-chat-input"
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder="Type your message..."
                                    rows={1}
                                />
                                <button className="compact-send-btn" onClick={handleSend} disabled={isTyping}>
                                    <svg viewBox="0 0 24 24" width="20" height="20">
                                        <path fill="currentColor" d="M2,21L23,12L2,3V10L17,12L2,14V21Z" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default CompactChat;
