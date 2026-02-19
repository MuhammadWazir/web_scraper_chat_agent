import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import './CompactChat.css';

/**
 * A compact chat component styled exactly like the widget-sdk ChatWidget.
 * Mirrors the widget-sdk layout: fixed bottom-right launcher, same CSS classes.
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
    const [isMobile, setIsMobile] = useState(false);
    const [showChat, setShowChat] = useState(true);
    const [mobileChatListOpen, setMobileChatListOpen] = useState(false);
    const messagesEndRef = useRef(null);

    const displayChatId = selectedChatId || tempChatId;
    const currentMessages = displayChatId ? (messages[displayChatId] || []) : [];

    useEffect(() => {
        const handleResize = () => {
            setIsMobile(window.innerWidth <= 768);
        };
        handleResize();
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

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

    const handleSelectChat = (chatId) => {
        onSelectChat(chatId);
        if (isMobile) {
            setShowChat(true);
            setMobileChatListOpen(false);
        }
    };

    return (
        <div className="cw-wrapper">
            {/* Launcher Button */}
            {!isOpen && (
                <button className="cw-launcher" onClick={() => setIsOpen(true)}>
                    <svg viewBox="0 0 24 24" width="28" height="28">
                        <path fill="currentColor" d="M12,2C6.47,2,2,6.47,2,12c0,2.21,0.72,4.24,1.94,5.88L3,22l4.12-0.94C8.76,21.65,10.32,22,12,22c5.53,0,10-4.47,10-10 S17.53,2,12,2" />
                    </svg>
                </button>
            )}

            {/* Chat Window */}
            {isOpen && (
                <div className="cw-widget animated-fade-in">
                    {/* Header */}
                    <div className="cw-header">
                        <div className="cw-header-info">
                            <span className="cw-dot"></span>
                            <span className="cw-title">AI Assistant</span>
                        </div>
                        <button className="cw-close-btn" onClick={() => setIsOpen(false)}>×</button>
                    </div>

                    {/* Container: sidebar + chat area */}
                    <div className={`cw-container ${isMobile && showChat ? 'mobile-chat-view' : ''}`}>

                        {/* Mobile toggle - only shown on mobile */}
                        {isMobile && (
                            <button
                                className="cw-mobile-toggle"
                                onClick={() => setMobileChatListOpen(!mobileChatListOpen)}
                            >
                                {mobileChatListOpen ? '▼ Hide Chats' : '▲ Show Chats'}
                            </button>
                        )}

                        {/* Sidebar - always shown on desktop; controlled by mobileChatListOpen on mobile */}
                        {(!isMobile || !showChat || mobileChatListOpen) && (
                            <div className={`cw-chat-list ${mobileChatListOpen ? 'mobile-visible' : ''}`}>
                                <div className="cw-chat-list-header">
                                    <h3>Chats</h3>
                                    <button className="cw-new-chat-btn" onClick={onNewChat}>
                                        + New
                                    </button>
                                </div>
                                <div className="cw-chats">
                                    {chats.length === 0 ? (
                                        <div className="cw-empty-chats">No chats yet</div>
                                    ) : (
                                        chats.map((chat) => (
                                            <div
                                                key={chat.chat_id}
                                                className={`cw-chat-item ${(selectedChatId === chat.chat_id || tempChatId === chat.chat_id) ? 'active' : ''}`}
                                                onClick={() => handleSelectChat(chat.chat_id)}
                                            >
                                                <div className="cw-chat-item-title">{chat.title || 'New Chat'}</div>
                                                <button
                                                    className="cw-delete-btn"
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
                        )}

                        {/* Chat Area */}
                        {(!isMobile || showChat) && (
                            <div className="cw-chat-area">
                                {isMobile && (
                                    <button className="cw-back-btn" onClick={() => setShowChat(false)}>
                                        ← Back
                                    </button>
                                )}

                                {/* Messages */}
                                <div className="cw-messages">
                                    {currentMessages.length === 0 && !isTyping && (
                                        <div className="cw-no-messages">
                                            <p>No messages yet. Start the conversation!</p>
                                        </div>
                                    )}

                                    {currentMessages.map((message, idx) => (
                                        <div
                                            key={message.message_id || idx}
                                            className={`cw-message ${message.ai_generated ? 'assistant' : 'user'}`}
                                        >
                                            {message.ai_generated ? (
                                                <>
                                                    {message.isFollowUp && (
                                                        <div className="cw-follow-up-badge">Follow-up</div>
                                                    )}

                                                    {/* Status hint */}
                                                    {message.streaming && message.statusHint && (
                                                        <div className="cw-status-hint">{message.statusHint}</div>
                                                    )}

                                                    {/* Inline typing indicator when streaming but no content */}
                                                    {message.streaming && !message.content && (
                                                        <div className="cw-typing-indicator">
                                                            <span></span>
                                                            <span></span>
                                                            <span></span>
                                                        </div>
                                                    )}

                                                    {/* Content */}
                                                    {message.content && (
                                                        <div className="cw-message-content">
                                                            <ReactMarkdown>{message.content}</ReactMarkdown>
                                                        </div>
                                                    )}

                                                    {/* Hints */}
                                                    {message.hints && message.hints.length > 0 && (
                                                        <div className="cw-message-hints">
                                                            {message.hints.map((hint, hintIdx) => (
                                                                <button
                                                                    key={hintIdx}
                                                                    className="cw-hint-button"
                                                                    onClick={() => onHintClick && onHintClick(hint)}
                                                                >
                                                                    {hint}
                                                                </button>
                                                            ))}
                                                        </div>
                                                    )}
                                                </>
                                            ) : (
                                                <div className="cw-message-content">{message.content}</div>
                                            )}
                                        </div>
                                    ))}

                                    {isTyping && (
                                        <div className="cw-message assistant cw-typing-dots">
                                            <span></span>
                                            <span></span>
                                            <span></span>
                                        </div>
                                    )}

                                    <div ref={messagesEndRef} />
                                </div>

                                {/* Input */}
                                <div className="cw-input-area">
                                    <textarea
                                        className="cw-input"
                                        value={inputValue}
                                        onChange={(e) => setInputValue(e.target.value)}
                                        onKeyPress={handleKeyPress}
                                        placeholder="Type your message..."
                                        rows={1}
                                    />
                                    <button className="cw-send-btn" onClick={handleSend} disabled={isTyping}>
                                        <svg viewBox="0 0 24 24" width="20" height="20">
                                            <path fill="currentColor" d="M2,21L23,12L2,3V10L17,12L2,14V21Z" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

export default CompactChat;
