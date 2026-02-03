import React, { useState, useEffect } from 'react';
import { ChatList } from './components/ChatList.jsx';
import { MessageList } from './components/MessageList.jsx';
import { ApiService } from './services/api.js';
import { StorageService } from './services/storage.js';
import './styles.css';

export function ChatWidget({ sessionToken, baseUrl = 'http://localhost:8000', authToken = null }) {
    const [chats, setChats] = useState([]);
    const [activeChatId, setActiveChatId] = useState(null);
    const [messages, setMessages] = useState({});
    const [inputValue, setInputValue] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [isMobile, setIsMobile] = useState(false);
    const [isOpen, setIsOpen] = useState(false);
    const [showChat, setShowChat] = useState(false);

    const apiService = new ApiService(baseUrl, authToken);
    const storageService = new StorageService(sessionToken);

    useEffect(() => {
        initWidget();

        const handleResize = () => {
            setIsMobile(window.innerWidth <= 768);
        };

        handleResize();
        window.addEventListener('resize', handleResize);

        return () => window.removeEventListener('resize', handleResize);
    }, []);

    const initWidget = async () => {
        try {
            const savedMessages = storageService.loadMessages();
            setMessages(savedMessages);

            await apiService.initSession(sessionToken);
            await loadChats();
        } catch (error) {
            console.error('Widget initialization error:', error);
        }
    };

    const loadChats = async () => {
        try {
            const loadedChats = await apiService.loadChats(sessionToken);
            setChats(loadedChats);

            // Auto-select first chat if none active
            if (!activeChatId && loadedChats.length > 0) {
                selectChat(loadedChats[0].chat_id);
            }
        } catch (error) {
            console.error('Failed to load chats:', error);
        }
    };

    const createChat = async () => {
        try {
            const newChat = await apiService.createChat(sessionToken);
            setChats([newChat, ...chats]);
            setActiveChatId(newChat.chat_id);
            setMessages({ ...messages, [newChat.chat_id]: [] });
            setIsTyping(false);

            if (isMobile) {
                setShowChat(true);
            }
        } catch (error) {
            console.error('Failed to create chat:', error);
        }
    };

    const deleteChat = async (chatId) => {
        if (!confirm('Delete this chat?')) return;

        try {
            await apiService.deleteChat(sessionToken, chatId);

            setChats(chats.filter(c => c.chat_id !== chatId));
            const newMessages = { ...messages };
            delete newMessages[chatId];
            setMessages(newMessages);
            storageService.saveMessages(newMessages);

            if (activeChatId === chatId) {
                setActiveChatId(null);
            }
        } catch (error) {
            console.error('Failed to delete chat:', error);
        }
    };

    const selectChat = async (chatId) => {
        setActiveChatId(chatId);
        setIsTyping(false);

        // Fetch messages if not already in state OR if we want to refresh from server
        // Using a ref or checking current state properly:
        setMessages(currentMessages => {
            if (!currentMessages[chatId] || currentMessages[chatId].length === 0) {
                // Trigger fetch if missing
                apiService.loadMessages(sessionToken, chatId).then(history => {
                    setMessages(prev => ({
                        ...prev,
                        [chatId]: history
                    }));
                }).catch(err => console.error('History load failed:', err));
            }
            return currentMessages;
        });

        if (isMobile) {
            setShowChat(true);
        }
    };

    const sendMessage = async () => {
        const text = inputValue.trim();
        if (!text) return;

        if (!activeChatId) {
            await createChat();
            if (!activeChatId) return;
        }

        const chatId = activeChatId;
        setInputValue('');

        // Add user message to UI
        const newMessages = {
            ...messages,
            [chatId]: [
                ...(messages[chatId] || []),
                { role: 'user', content: text }
            ]
        };
        setMessages(newMessages);
        setIsTyping(true);

        try {
            const tempAiMessageId = `temp-ai-${Date.now()}`;
            let streamedContent = '';
            let currentStatusHint = null;
            let firstChunkReceived = false;

            await apiService.sendMessageStream(
                sessionToken,
                chatId,
                text,
                async (event) => {
                    setMessages(prev => {
                        const chatMessages = [...(prev[chatId] || [])];
                        // Remove any existing temp AI message for this stream
                        const filteredMessages = chatMessages.filter(m => m.message_id !== tempAiMessageId);

                        if (!firstChunkReceived) {
                            setIsTyping(false);
                            firstChunkReceived = true;
                        }

                        if (event.type === 'status_hint') {
                            currentStatusHint = event.message;
                        } else if (event.type === 'content') {
                            streamedContent += event.data || '';
                            currentStatusHint = null; // Clear hint when content starts
                        } else if (event.type === 'complete') {
                            currentStatusHint = null;
                        }

                        const aiMessage = {
                            message_id: tempAiMessageId,
                            role: 'assistant',
                            content: streamedContent,
                            statusHint: currentStatusHint,
                            streaming: event.type !== 'complete'
                        };

                        return {
                            ...prev,
                            [chatId]: [...filteredMessages, aiMessage]
                        };
                    });

                    // Yield to allow React to render the hint before content arrives
                    if (event.type === 'status_hint') {
                        await new Promise(r => setTimeout(r, 0));
                    }
                }
            );
        } catch (error) {
            console.error('Send message error:', error);

            setMessages(prev => ({
                ...prev,
                [chatId]: [
                    ...(prev[chatId] || []),
                    { role: 'assistant', content: 'Error: Could not send message' }
                ]
            }));
        } finally {
            setIsTyping(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const currentMessages = activeChatId ? (messages[activeChatId] || []) : [];

    return (
        <div className="chat-widget-wrapper">
            {/* Launcher Button */}
            {!isOpen && (
                <button className="chat-launcher" onClick={() => setIsOpen(true)}>
                    <svg viewBox="0 0 24 24" width="24" height="24">
                        <path fill="currentColor" d="M12,2C6.47,2,2,6.47,2,12c0,2.21,0.72,4.24,1.94,5.88L3,22l4.12-0.94C8.76,21.65,10.32,22,12,22c5.53,0,10-4.47,10-10 S17.53,2,12,2" />
                    </svg>
                </button>
            )}

            {/* Chat Window */}
            {isOpen && (
                <div className="chat-widget animated-fade-in">
                    <div className="chat-header">
                        <div className="header-info">
                            <span className="dot"></span>
                            <span className="title">AI Assistant</span>
                        </div>
                        <button className="close-btn" onClick={() => setIsOpen(false)}>×</button>
                    </div>

                    <div className={`chat-container ${(isMobile && showChat) ? 'mobile-chat-view' : ''}`}>
                        {(!isMobile || !showChat) && (
                            <ChatList
                                chats={chats}
                                activeChatId={activeChatId}
                                onSelectChat={selectChat}
                                onDeleteChat={deleteChat}
                                onNewChat={createChat}
                            />
                        )}

                        {(!isMobile || showChat) && (
                            <div className="chat-area">
                                {isMobile && (
                                    <button className="back-btn" onClick={() => setShowChat(false)}>
                                        ← Back
                                    </button>
                                )}

                                <MessageList
                                    messages={currentMessages}
                                    isTyping={isTyping}
                                />

                                <div className="chat-input-area">
                                    <textarea
                                        className="chat-input"
                                        value={inputValue}
                                        onChange={(e) => setInputValue(e.target.value)}
                                        onKeyPress={handleKeyPress}
                                        placeholder="Type your message..."
                                        rows={1}
                                    />
                                    <button className="send-btn" onClick={sendMessage}>
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