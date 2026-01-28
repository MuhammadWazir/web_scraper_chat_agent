import { ApiService } from './services/api.js';
import { StorageService } from './services/storage.js';
import { ChatList } from './components/ChatList.js';
import { MessageList } from './components/MessageList.js';
import { EventHandlers } from './components/EventHandlers.js';
import { getTemplate } from './components/template.js';
import { styles } from './styles.js';
import { parseSessionToken, isMobileView } from './utils/dom.js';

export class ChatWidget {
    constructor(config = {}) {
        this.sessionToken = null;
        this.baseUrl = config.baseUrl || 'http://localhost:8000';
        this.authToken = config.authToken || null;
        this.activeChatId = null;
        this.chats = [];
        this.messages = {}; // Local cache: { chatId: [msgs] }
        
        // Initialize services
        this.apiService = new ApiService(this.baseUrl, this.authToken);
        this.storageService = null; // Initialized after session token is set
        this.eventHandlers = null; // Initialized after render
    }

    async init(sessionUrl) {
        try {
            this.sessionToken = parseSessionToken(sessionUrl);
            this.storageService = new StorageService(this.sessionToken);

            // Initialize session
            const data = await this.apiService.initSession(this.sessionToken);

            // Load chats
            await this.loadChats();

            // Load messages from localStorage
            this.messages = this.storageService.loadMessages();

            console.log('Widget session initialized successfully');
            return data;
        } catch (error) {
            console.error('Widget initialization error:', error);
            throw error;
        }
    }

    async loadChats() {
        try {
            this.chats = await this.apiService.loadChats(this.sessionToken);
            this.renderChatList();
        } catch (error) {
            console.error('Failed to load chats:', error);
        }
    }

    async createChat() {
        try {
            const newChat = await this.apiService.createChat(this.sessionToken);
            this.chats.unshift(newChat);
            this.activeChatId = newChat.chat_id;
            this.messages[newChat.chat_id] = [];
            
            this.renderChatList();
            this.renderMessages();
            
            // Show chat view on mobile
            if (isMobileView() && this.eventHandlers) {
                this.eventHandlers.showMobileChat();
            }
        } catch (error) {
            console.error('Failed to create chat:', error);
        }
    }

    async deleteChat(chatId) {
        if (!confirm('Delete this chat?')) return;

        try {
            await this.apiService.deleteChat(this.sessionToken, chatId);
            
            this.chats = this.chats.filter(c => c.chat_id !== chatId);
            delete this.messages[chatId];
            this.storageService.saveMessages(this.messages);

            if (this.activeChatId === chatId) {
                this.activeChatId = null;
                this.renderMessages();
            }

            this.renderChatList();
        } catch (error) {
            console.error('Failed to delete chat:', error);
        }
    }

    selectChat(chatId) {
        this.activeChatId = chatId;
        this.renderMessages();

        // Show chat view on mobile
        if (isMobileView() && this.eventHandlers) {
            this.eventHandlers.showMobileChat();
        }
    }

    async sendMessage() {
        const input = this.shadowRoot.querySelector('.chat-input');
        const text = input.value.trim();

        if (!text) return;

        // Create chat if none exists
        if (!this.activeChatId) {
            await this.createChat();
            if (!this.activeChatId) return;
        }

        const chatId = this.activeChatId;
        input.value = '';

        // Add user message
        this.appendMessage(chatId, text, true);

        // Show typing indicator
        const messageList = new MessageList(this.shadowRoot, []);
        if (this.activeChatId === chatId) {
            messageList.showTypingIndicator();
        }

        try {
            const response = await this.apiService.sendMessage(
                this.sessionToken,
                chatId,
                text
            );

            if (this.activeChatId === chatId) {
                messageList.hideTypingIndicator();
            }

            this.appendMessage(chatId, response.content, false);
        } catch (error) {
            if (this.activeChatId === chatId) {
                messageList.hideTypingIndicator();
            }
            this.appendMessage(chatId, 'Error: Could not send message', false);
            console.error('Send message error:', error);
        }
    }

    appendMessage(chatId, content, isUser) {
        if (!this.messages[chatId]) {
            this.messages[chatId] = [];
        }

        const message = {
            role: isUser ? 'user' : 'ai',
            content: content
        };

        this.messages[chatId].push(message);
        this.storageService.saveMessages(this.messages);

        if (this.activeChatId === chatId) {
            const messageList = new MessageList(this.shadowRoot, [message]);
            messageList.appendMessage(message);
        }
    }

    render(selector) {
        const container = document.querySelector(selector);
        if (!container) {
            console.error(`Container "${selector}" not found`);
            return;
        }

        // Create shadow DOM
        const shadow = container.attachShadow({ mode: 'open' });

        // Add styles
        const styleElement = document.createElement('style');
        styleElement.textContent = styles;
        shadow.appendChild(styleElement);

        // Add HTML template
        const wrapper = document.createElement('div');
        wrapper.innerHTML = getTemplate();
        shadow.appendChild(wrapper);

        this.shadowRoot = shadow;

        // Initialize event handlers
        this.eventHandlers = new EventHandlers(this);
        this.eventHandlers.bindAll();

        // Initial render
        this.renderChatList();
        this.renderMessages();
    }

    renderChatList() {
        if (!this.shadowRoot) return;

        const chatList = new ChatList(
            this.shadowRoot,
            this.chats,
            this.activeChatId,
            (chatId) => this.selectChat(chatId),
            (chatId) => this.deleteChat(chatId)
        );

        chatList.render();
    }

    renderMessages() {
        if (!this.shadowRoot) return;

        const messages = this.activeChatId ? (this.messages[this.activeChatId] || []) : [];
        const messageList = new MessageList(this.shadowRoot, messages);
        messageList.render();
    }
}
