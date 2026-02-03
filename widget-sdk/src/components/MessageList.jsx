import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

export function MessageList({ messages, isTyping, onHintClick }) {
    const messagesEndRef = useRef(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isTyping]);

    return (
        <div className="messages">
            {messages.map((message, idx) => (
                <div
                    key={idx}
                    className={`message ${message.role} ${(message.role === 'ai' || message.role === 'assistant') ? 'ai-message-wrapper' : ''}`}
                >
                    {message.role === 'ai' || message.role === 'assistant' ? (
                        <>
                            {/* Status hint (visible while streaming) */}
                            {message.streaming && message.statusHint && (
                                <div className="status-hint">
                                    {message.statusHint}
                                </div>
                            )}
                            {/* Assistant response (streams incrementally) */}
                            {message.content && (
                                <div className="message-content">
                                    <ReactMarkdown>{message.content}</ReactMarkdown>
                                </div>
                            )}
                            {message.hints && message.hints.length > 0 && (
                                <div className="message-hints">
                                    {message.hints.map((hint, hintIdx) => (
                                        <button
                                            key={hintIdx}
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
                        <div className="message-content">{message.content}</div>
                    )}
                </div>
            ))}

            {isTyping && (
                <div className="message ai typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            )}

            <div ref={messagesEndRef} />
        </div>
    );
}
