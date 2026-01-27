class ChatWidget {
    constructor(config = {}) {
        this.sessionToken = null;
        this.baseUrl = config.baseUrl || 'http://localhost:8000';
        this.authToken = config.authToken || null;
        this.activeChatId = null;
        this.chats = [];
        this.messages = {}; // Local cache of messages: { chatId: [msgs] }
    }

    async init(sessionUrl) {
        try {
            let token = sessionUrl;
            if (sessionUrl.includes('?')) {
                const urlParams = new URLSearchParams(sessionUrl.split('?')[1]);
                token = urlParams.get('token') || token;
            } else if (sessionUrl.includes('/')) {
                 const parts = sessionUrl.split('/');
                 token = parts[parts.length - 1];
            }

            this.sessionToken = token;
            
            // 1. Initialize Session
            const response = await fetch(`${this.baseUrl}/widget/init/${this.sessionToken}`, {
                method: 'POST'
            });

            if (!response.ok) throw new Error('Failed to initialize session');
            const data = await response.json();
            
            // 2. Load Chats
            await this.loadChats();

            // 3. Load Messages from LocalStorage
            this.loadMessagesFromStorage();

            console.log('Widget session initialized');
            return data;
        } catch (error) {
            console.error('Widget initialization error:', error);
            throw error;
        }
    }

    async loadChats() {
        try {
            const resp = await fetch(`${this.baseUrl}/widget/${this.sessionToken}/chats`);
            if (resp.ok) {
                this.chats = await resp.json();
                this.renderChatList();
            }
        } catch (e) {
            console.error("Failed to load chats", e);
        }
    }

    loadMessagesFromStorage() {
        try {
            const stored = localStorage.getItem(`widget_msgs_${this.sessionToken}`);
            if (stored) {
                this.messages = JSON.parse(stored);
            }
        } catch (e) {
            console.error("Failed to load local messages", e);
        }
    }

    saveMessagesToStorage() {
        try {
            localStorage.setItem(`widget_msgs_${this.sessionToken}`, JSON.stringify(this.messages));
        } catch (e) {
            console.error("Failed to save messages", e);
        }
    }

    async createChat() {
        try {
            const resp = await fetch(`${this.baseUrl}/widget/${this.sessionToken}/chats`, { method: 'POST' });
            if (resp.ok) {
                const newChat = await resp.json();
                this.chats.unshift(newChat); // Add to top
                this.activeChatId = newChat.chat_id;
                this.messages[newChat.chat_id] = [];
                this.renderChatList();
                this.renderMessages();
            }
        } catch (e) {
            console.error("Failed to create chat", e);
        }
    }

    async deleteChat(chatId, event) {
        if (event) event.stopPropagation();
        if (!confirm("Delete this chat?")) return;

        try {
            const resp = await fetch(`${this.baseUrl}/widget/${this.sessionToken}/chats/${chatId}`, { method: 'DELETE' });
            if (resp.ok) {
                this.chats = this.chats.filter(c => c.chat_id !== chatId);
                delete this.messages[chatId];
                this.saveMessagesToStorage();
                
                if (this.activeChatId === chatId) {
                    this.activeChatId = null;
                    this.renderMessages(); // Clear view
                }
                this.renderChatList();
            }
        } catch (e) {
            console.error("Failed to delete chat", e);
        }
    }

    selectChat(chatId) {
        this.activeChatId = chatId;
        this.renderMessages();
        
        // Mobile view adjustment could go here (hide sidebar)
        const sidebar = this.shadowRoot.querySelector('.sidebar');
        const main = this.shadowRoot.querySelector('.main-chat');
        if (window.innerWidth < 600) {
            sidebar.style.display = 'none';
            main.style.display = 'flex';
            this.shadowRoot.querySelector('.back-btn').style.display = 'block';
        }
    }

    render(selector) {
        const container = document.querySelector(selector);
        if (!container) return;

        const shadow = container.attachShadow({ mode: 'open' });
        const style = document.createElement('style');
        style.textContent = `
            :host { 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
                --primary-color: #667eea;
                --bg-color: #f5f5f5;
                --sidebar-bg: #fff;
                --border-color: #e0e0e0;
                --text-color: #2d3748;
            }
            .widget-container {
                position: fixed; bottom: 20px; right: 20px;
                width: 400px; height: 650px;
                background: var(--bg-color); border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                display: flex; flex-direction: column; overflow: hidden;
                transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                z-index: 99999;
                border: 1px solid rgba(0,0,0,0.05);
            }
            .widget-container.closed { transform: translateY(120%); }
            
            .header {
                background: #fff; color: var(--text-color); padding: 15px 20px;
                display: flex; justify-content: space-between; align-items: center;
                cursor: pointer;
                border-bottom: 1px solid var(--border-color);
                box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            }
            .header span { font-weight: 600; font-size: 1.1rem; }
            
            .content { display: flex; flex: 1; overflow: hidden; height: 100%; }
            
            .sidebar {
                width: 140px; border-right: 1px solid var(--border-color); background: var(--sidebar-bg);
                overflow-y: auto; display: flex; flex-direction: column;
            }
            
            .chat-list { flex: 1; padding: 10px 0; }
            .chat-item {
                padding: 12px 15px; cursor: pointer; font-size: 0.9rem; color: #4a5568;
                border-bottom: 1px solid transparent; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
                position: relative; transition: all 0.2s;
            }
            .chat-item:hover { background: #f7fafc; color: var(--primary-color); }
            .chat-item.active { background: #ebf4ff; color: var(--primary-color); font-weight: 600; border-right: 3px solid var(--primary-color); }
            .delete-chat {
                display: none; position: absolute; right: 8px; top: 50%; transform: translateY(-50%);
                color: #e53e3e; font-size: 1.1rem; cursor: pointer; padding: 2px;
                background: rgba(255,255,255,0.8); border-radius: 50%;
            }
            .chat-item:hover .delete-chat { display: block; }
            
            .new-chat-btn {
                margin: 10px; padding: 8px; background: var(--primary-color); color: white; border: none;
                cursor: pointer; text-align: center; border-radius: 6px; font-weight: 500;
                transition: transform 0.1s;
            }
            .new-chat-btn:active { transform: scale(0.98); }

            .main-chat { 
                flex: 1; display: flex; flex-direction: column; 
                background: linear-gradient(180deg, #fafafa 0%, #ffffff 100%);
            }
            .messages { 
                flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px;
            }
            .message { 
                max-width: 75%; padding: 12px 16px; border-radius: 18px; 
                line-height: 1.5; word-wrap: break-word; animation: slideIn 0.3s;
            }
            @keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
            .message.user { 
                align-self: flex-end; background: var(--primary-color); color: white; 
                border-bottom-right-radius: 4px; box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
            }
            .message.ai { 
                align-self: flex-start; background: #fff; color: var(--text-color); 
                border: 1px solid var(--border-color); border-bottom-left-radius: 4px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            
            .input-area { 
                padding: 15px; border-top: 1px solid var(--border-color); 
                display: flex; gap: 10px; align-items: center; background: #fff;
            }
            .chat-input { 
                flex: 1; padding: 12px 15px; border: 1px solid #e2e8f0; border-radius: 20px; 
                outline: none; font-size: 0.95rem; color: var(--text-color); background: #f8fafc;
                transition: border-color 0.2s;
            }
            .chat-input:focus { border-color: var(--primary-color); background: #fff; box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2); }
            .send-btn { 
                background: var(--primary-color); color: white; border: none; 
                width: 40px; height: 40px; border-radius: 50%; cursor: pointer; 
                display: flex; align-items: center; justify-content: center;
                transition: transform 0.2s, background 0.2s;
            }
            .send-btn:hover { background: #5a67d8; transform: scale(1.05); }
            .send-btn:active { transform: scale(0.95); }
            .send-btn::after { content: '➤'; font-size: 1.2rem; transform: translateX(2px); }
            
            .launcher {
                position: fixed; bottom: 20px; right: 20px;
                width: 60px; height: 60px; background: var(--primary-color);
                border-radius: 50%; color: white; display: flex;
                justify-content: center; align-items: center; font-size: 28px;
                cursor: pointer; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); z-index: 99999;
                transition: transform 0.2s, background 0.2s;
            }
            .launcher:hover { transform: scale(1.1); background: #5a67d8; }
            
            .back-btn { display: none; margin-right: 15px; cursor: pointer; font-size: 1.2rem; padding: 5px; }
            
            /* Responsive */
            @media (max-width: 600px) {
                .widget-container { width: 100%; height: 100%; bottom: 0; right: 0; border-radius: 0; }
                .sidebar { width: 100%; }
                .main-chat { display: none; width: 100%; }
            }
        `;
        shadow.appendChild(style);

        const wrapper = document.createElement('div');
        wrapper.innerHTML = `
            <div class="launcher">💬</div>
            <div class="widget-container closed">
                <div class="header">
                    <div style="display:flex; align-items:center;">
                        <span class="back-btn">←</span>
                        <span>AI Assistant</span>
                    </div>
                    <span class="close-btn" style="font-size: 24px;">×</span>
                </div>
                <div class="content">
                    <div class="sidebar">
                        <button class="new-chat-btn">New Chat +</button>
                        <div class="chat-list"></div>
                    </div>
                    <div class="main-chat">
                        <div class="messages"></div>
                        <div class="input-area">
                            <input type="text" class="chat-input" placeholder="Type a message..." />
                            <button class="send-btn" aria-label="Send"></button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        shadow.appendChild(wrapper);

        this.shadowRoot = shadow;
        this.bindEvents();
        this.renderChatList();
    }

    bindEvents() {
        const root = this.shadowRoot;
        const launcher = root.querySelector('.launcher');
        const container = root.querySelector('.widget-container');
        const closeBtn = root.querySelector('.close-btn');
        const newChatBtn = root.querySelector('.new-chat-btn');
        const sendBtn = root.querySelector('.send-btn');
        const input = root.querySelector('.chat-input');
        const backBtn = root.querySelector('.back-btn');

        const toggle = () => {
            container.classList.toggle('closed');
            launcher.style.display = container.classList.contains('closed') ? 'flex' : 'none';
        };

        launcher.addEventListener('click', toggle);
        closeBtn.addEventListener('click', toggle);
        newChatBtn.addEventListener('click', () => this.createChat());
        
        const send = async () => {
            const txt = input.value.trim();
            if(!txt) return;
            
            if(!this.activeChatId) {
                await this.createChat();
                if(!this.activeChatId) return;
            }
            
            input.value = '';
            this.appendMessage(this.activeChatId, txt, true);
            
            try {
                const requestBody = { 
                    content: txt
                };
                
                if (this.authToken) {
                    requestBody.authorization = this.authToken;
                }

                const resp = await fetch(`${this.baseUrl}/widget/${this.sessionToken}/chats/${this.activeChatId}/messages`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestBody)
                });
                
                if(resp.ok) {
                    const data = await resp.json();
                    this.appendMessage(this.activeChatId, data.content, false);
                } else {
                    this.appendMessage(this.activeChatId, "Error: Could not send message", false);
                }
            } catch(e) {
                this.appendMessage(this.activeChatId, "Network error", false);
            }
        };

        sendBtn.addEventListener('click', send);
        
        // Proper event listener for Enter key
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                send();
            }
        });
        
        backBtn.addEventListener('click', () => {
             root.querySelector('.sidebar').style.display = 'flex';
             root.querySelector('.main-chat').style.display = 'none';
             backBtn.style.display = 'none';
             this.activeChatId = null;
        });
    }

    renderChatList() {
        const list = this.shadowRoot.querySelector('.chat-list');
        if(!list) return;
        
        list.innerHTML = '';
        this.chats.forEach(chat => {
            const div = document.createElement('div');
            div.className = `chat-item ${chat.chat_id === this.activeChatId ? 'active' : ''}`;
            div.innerHTML = `
                <span>${chat.title || 'New Chat'}</span>
                <span class="delete-chat">×</span>
            `;
            div.onclick = () => this.selectChat(chat.chat_id);
            div.querySelector('.delete-chat').onclick = (e) => this.deleteChat(chat.chat_id, e);
            list.appendChild(div);
        });
    }

    renderMessages() {
        const container = this.shadowRoot.querySelector('.messages');
        if(!container) return;
        
        container.innerHTML = '';
        if(!this.activeChatId) return;

        const msgs = this.messages[this.activeChatId] || [];
        msgs.forEach(m => {
            const div = document.createElement('div');
            div.className = `message ${m.role}`;
            div.textContent = m.content;
            container.appendChild(div);
        });
        container.scrollTop = container.scrollHeight;
    }

    appendMessage(chatId, text, isUser) {
        if (!this.messages[chatId]) this.messages[chatId] = [];
        this.messages[chatId].push({ role: isUser ? 'user' : 'ai', content: text });
        this.saveMessagesToStorage();
        if (this.activeChatId === chatId) {
            this.renderMessages();
        }
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatWidget;
} else {
    window.ChatWidget = ChatWidget;
}