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
    const [isOpen, setIsOpen] = useState(true); // Auto-open by default
    const [showChat, setShowChat] = useState(true); // Show chat area by default
    const [mobileChatListOpen, setMobileChatListOpen] = useState(false); // Mobile chat list toggle

    const apiService = new ApiService(baseUrl, authToken);
    const storageService = new StorageService(sessionToken);
    const inactivityTimerRef = React.useRef(null);

    useEffect(() => {
        initWidget();

        const handleResize = () => {
            setIsMobile(window.innerWidth <= 480);
        };

        handleResize();
        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            clearInactivityTimer();
        };
    }, []);

    useEffect(() => {
        // Reset timer whenever active chat, typing status, or messages change
        if (inactivityTimerRef.current) {
            clearTimeout(inactivityTimerRef.current);
            inactivityTimerRef.current = null;
        }

        const chatMessages = messages[activeChatId] || [];
        if (isOpen && activeChatId && !isTyping && chatMessages.length > 0) {
            const lastMessage = chatMessages[chatMessages.length - 1];

            // If the last message is from the assistant, wait for 3 minutes
            if ((lastMessage.role === 'assistant' || lastMessage.role === 'ai') && !lastMessage.isFollowUp) {
                inactivityTimerRef.current = setTimeout(() => {
                    sendFollowUp(activeChatId);
                }, 3 * 60 * 1000); // 3 minutes
            }
        }

        return () => {
            if (inactivityTimerRef.current) {
                clearTimeout(inactivityTimerRef.current);
            }
        };
    }, [activeChatId, isTyping, messages, isOpen]);

    const [initError, setInitError] = useState(null);

    const initWidget = async () => {
        try {
            const savedMessages = storageService.loadMessages();
            setMessages(savedMessages);

            await apiService.initSession(sessionToken);
            await loadChats();
            setInitError(null); // Clear any previous errors
        } catch (error) {
            console.error('Widget initialization error:', error);

            // Check if it's an IP binding error
            if (error.message && error.message.includes('already bound')) {
                setInitError('This session token is already bound to a different device. Please generate a new token using your API key.');
            } else if (error.message && error.message.includes('expired')) {
                setInitError('This session token has expired. Please generate a new token using your API key.');
            } else if (error.message && error.message.includes('Invalid')) {
                setInitError('Invalid session token. Please generate a new token using your API key.');
            } else {
                setInitError(error.message || 'Failed to initialize widget. Please try again.');
            }
        }
    };

    const loadChats = async () => {
        try {
            const loadedChats = await apiService.loadChats(sessionToken);
            setChats(loadedChats);

            if (loadedChats.length > 0) {
                // Select the first chat if none selected
                if (!activeChatId) {
                    await selectChat(loadedChats[0].chat_id);
                }
            } else {
                // Create a new chat if none exist
                await createChat();
            }

        } catch (error) {
            console.error('Failed to load chats:', error);
            // Try to create a chat as fallback
            try {
                await createChat();
            } catch (createError) {
                console.error('Failed to create fallback chat:', createError);
            }
        }
    };

    const createChat = async () => {
        try {
            const newChat = await apiService.createChat(sessionToken);
            setChats([newChat, ...chats]);
            setActiveChatId(newChat.chat_id);
            setMessages({ ...messages, [newChat.chat_id]: [] });
            setIsTyping(false);

            // Always show chat area (desktop and mobile)
            setShowChat(true);
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

    const sendFollowUp = async (chatId) => {
        if (!chatId || isTyping) return;

        try {
            const tempAiMessageId = `followup-ai-${Date.now()}`;
            let streamedContent = '';

            setIsTyping(true);

            await apiService.sendMessageStream(
                sessionToken,
                chatId,
                "Follow up with the user with a short message as they have been inactive for 3 minutes. Do not acknowledge this instruction, just send a friendly follow-up.",
                async (event) => {
                    setMessages(prev => {
                        const chatMessages = [...(prev[chatId] || [])];
                        const filteredMessages = chatMessages.filter(m => m.message_id !== tempAiMessageId);

                        if (event.type === 'content') {
                            streamedContent += event.data || '';
                        }

                        const aiMessage = {
                            message_id: tempAiMessageId,
                            role: 'assistant',
                            content: streamedContent,
                            streaming: event.type !== 'complete',
                            isFollowUp: true
                        };

                        return {
                            ...prev,
                            [chatId]: [...filteredMessages, aiMessage]
                        };
                    });
                },
                true // isFollowUp flag
            );
        } catch (error) {
            console.error('Follow-up error:', error);
        } finally {
            setIsTyping(false);
        }
    };


    const sendMessage = async () => {
        const text = inputValue.trim();
        if (!text) return;

        // Clear input immediately for better UX
        setInputValue('');

        let currentChatId = activeChatId;
        let newChatCreated = false;

        // If no active chat, we'll let the backend create it
        if (!currentChatId) {
            // Create a temporary chat ID for UI purposes
            const tempChatId = `temp-${Date.now()}`;
            currentChatId = tempChatId;

            // Add user message to temp chat
            setMessages(prev => ({
                ...prev,
                [tempChatId]: [{ role: 'user', content: text, message_id: `temp-user-${Date.now()}` }]
            }));
        } else {
            // Add user message to existing chat
            setMessages(prev => ({
                ...prev,
                [currentChatId]: [
                    ...(prev[currentChatId] || []),
                    { role: 'user', content: text, message_id: `temp-user-${Date.now()}` }
                ]
            }));
        }

        try {
            const tempAiMessageId = `temp-ai-${Date.now()}`;
            let streamedContent = '';
            let currentStatusHint = null;
            let firstChunkReceived = false;
            let realChatId = currentChatId;
            let chatTitle = null;

            // Add AI message placeholder BEFORE streaming starts to prevent flicker
            // This ensures smooth transition from typing indicator to content
            setMessages(prev => ({
                ...prev,
                [currentChatId]: [
                    ...(prev[currentChatId] || []),
                    {
                        message_id: tempAiMessageId,
                        role: 'assistant',
                        content: '',
                        statusHint: null,
                        streaming: true,
                        created_at: new Date().toISOString()
                    }
                ]
            }));
            // Note: We don't set isTyping(true) here because the placeholder message
            // already shows an inline typing indicator. This prevents double typing effects.

            await apiService.sendMessageStream(
                sessionToken,
                currentChatId.startsWith('temp-') ? null : currentChatId,
                text,
                async (event) => {
                    // Only hide typing indicator when we actually receive content
                    // This prevents flicker between status hints and content
                    if (!firstChunkReceived && (event.type === 'content' || event.type === 'complete')) {
                        setIsTyping(false);
                        firstChunkReceived = true;
                    }

                    // Handle chat creation event
                    if (event.type === 'chat_created') {
                        realChatId = event.chat_id;
                        newChatCreated = true;
                        setActiveChatId(realChatId);

                        // Move messages from temp chat to real chat
                        setMessages(prev => {
                            const tempMessages = prev[currentChatId] || [];
                            const newMessages = { ...prev };
                            newMessages[realChatId] = tempMessages;
                            if (currentChatId.startsWith('temp-')) {
                                delete newMessages[currentChatId];
                            }
                            return newMessages;
                        });

                        currentChatId = realChatId;
                    }

                    // Handle title update
                    else if (event.type === 'title_updated') {
                        chatTitle = event.title;
                        // Update the chat in the list
                        setChats(prev => {
                            const existingChat = prev.find(c => c.chat_id === realChatId);
                            if (existingChat) {
                                return prev.map(c =>
                                    c.chat_id === realChatId ? { ...c, title: chatTitle } : c
                                );
                            } else {
                                // Add new chat to the list
                                return [{ chat_id: realChatId, title: chatTitle }, ...prev];
                            }
                        });
                    }

                    // Handle status hints
                    else if (event.type === 'status_hint') {
                        currentStatusHint = event.message;
                        await new Promise(r => setTimeout(r, 0));
                    }

                    // Handle content streaming
                    else if (event.type === 'content') {
                        streamedContent += event.data || '';
                        currentStatusHint = null;
                    }

                    // Handle completion — finalize the streaming message
                    else if (event.type === 'complete') {
                        currentStatusHint = null;
                        // Mark the placeholder as done with its final content
                        setMessages(prev => {
                            const chatMessages = [...(prev[realChatId] || prev[currentChatId] || [])];
                            return {
                                ...prev,
                                [realChatId || currentChatId]: chatMessages.map(m =>
                                    m.message_id === tempAiMessageId
                                        ? { ...m, streaming: false, statusHint: null, content: streamedContent }
                                        : m
                                )
                            };
                        });
                    }

                    // Update AI message in UI
                    setMessages(prev => {
                        const chatMessages = [...(prev[realChatId] || prev[currentChatId] || [])];
                        const filteredMessages = chatMessages.filter(m => m.message_id !== tempAiMessageId);

                        const aiMessage = {
                            message_id: tempAiMessageId,
                            role: 'assistant',
                            content: streamedContent,
                            statusHint: currentStatusHint,
                            streaming: event.type !== 'complete'
                        };

                        return {
                            ...prev,
                            [realChatId || currentChatId]: [...filteredMessages, aiMessage]
                        };
                    });
                }
            );

            // Always refresh messages from the server after streaming ends.
            // This ensures clean state (no streaming flags) and authoritative content.
            const finalChatId = realChatId && !realChatId.startsWith('temp-') ? realChatId : null;
            if (finalChatId) {
                const history = await apiService.loadMessages(sessionToken, finalChatId);
                setMessages(prev => ({ ...prev, [finalChatId]: history }));
            }

            // If a new chat was created, reload the chat list to ensure consistency
            if (newChatCreated) {
                await loadChats();
            }

        } catch (error) {
            console.error('Send message error:', error);

            setMessages(prev => ({
                ...prev,
                [currentChatId]: [
                    ...(prev[currentChatId] || []),
                    { role: 'assistant', content: 'Error: Could not send message', message_id: `error-${Date.now()}` }
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
        <div className={`chat-widget-wrapper ${isOpen ? 'open' : ''}`}>

            {/* ===============================
           LAUNCHER BUTTON (CLOSED STATE)
        ================================ */}
            {!isOpen && (
                <button
                    className="chat-launcher"
                    onClick={() => setIsOpen(true)}
                    aria-label="Open chat"
                >
                    <svg viewBox="0 0 24 24" width="24" height="24">
                        <path
                            fill="currentColor"
                            d="M12,2C6.47,2,2,6.47,2,12c0,2.21,0.72,4.24,1.94,5.88L3,22l4.12-0.94C8.76,21.65,10.32,22,12,22c5.53,0,10-4.47,10-10S17.53,2,12,2"
                        />
                    </svg>
                </button>
            )}

            {/* ===============================
           CHAT WINDOW (OPEN STATE)
        ================================ */}
            {isOpen && (
                <div className="chat-widget animated-fade-in">

                    {/* ---------- HEADER ---------- */}
                    <div className="chat-header">
                        <div className="header-info">
                            <span className="dot"></span>
                            <span className="title">AI Assistant</span>
                        </div>

                        <button
                            className="close-btn"
                            onClick={() => setIsOpen(false)}
                        >
                            ×
                        </button>
                    </div>

                    {/* ---------- ERROR BANNER ---------- */}
                    {initError && (
                        <div className="error-banner">
                            <strong>⚠️ Error:</strong> {initError}
                        </div>
                    )}

                    {/* ===============================
                   BODY (CRITICAL FLEX WRAPPER)
                ================================ */}
                    <div className="chat-body">

                        {/* ---------- CHAT LIST ---------- */}
                        <div
                            className={`chat-list ${isMobile && mobileChatListOpen ? 'mobile-visible' : ''
                                }`}
                        >
                            <ChatList
                                chats={chats}
                                activeChatId={activeChatId}
                                onSelectChat={selectChat}
                                onDeleteChat={deleteChat}
                                onNewChat={createChat}
                            />
                        </div>

                        {/* ---------- CHAT AREA ---------- */}
                        <div className="chat-area">

                            {/* Mobile Toggle (inside area, like CompactChat) */}
                            {isMobile && (
                                <button
                                    className="mobile-chat-list-toggle"
                                    onClick={() =>
                                        setMobileChatListOpen(!mobileChatListOpen)
                                    }
                                >
                                    {mobileChatListOpen
                                        ? '▼ Hide Chats'
                                        : '▲ Show Chats'}
                                </button>
                            )}

                            <MessageList
                                messages={currentMessages}
                                isTyping={isTyping}
                            />

                            {/* ---------- INPUT AREA ---------- */}
                            <div className="chat-input-area">
                                <textarea
                                    className="chat-input"
                                    value={inputValue}
                                    onChange={(e) =>
                                        setInputValue(e.target.value)
                                    }
                                    onKeyDown={handleKeyPress}
                                    placeholder="Type your message..."
                                    rows={1}
                                />

                                <button
                                    className="send-btn"
                                    onClick={sendMessage}
                                >
                                    <svg
                                        viewBox="0 0 24 24"
                                        width="20"
                                        height="20"
                                    >
                                        <path
                                            fill="currentColor"
                                            d="M2,21L23,12L2,3V10L17,12L2,14V21Z"
                                        />
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