import { createElement } from '../utils/dom.js';

export class ChatList {
    constructor(shadowRoot, chats, activeChatId, onSelectChat, onDeleteChat) {
        this.shadowRoot = shadowRoot;
        this.chats = chats;
        this.activeChatId = activeChatId;
        this.onSelectChat = onSelectChat;
        this.onDeleteChat = onDeleteChat;
    }

    render() {
        const listContainer = this.shadowRoot.querySelector('.chat-list');
        if (!listContainer) return;

        listContainer.innerHTML = '';

        this.chats.forEach(chat => {
            const chatItem = createElement('div', `chat-item ${chat.chat_id === this.activeChatId ? 'active' : ''}`);
            
            chatItem.innerHTML = `
                <span>${this.escapeHtml(chat.title || 'New Chat')}</span>
                <span class="delete-chat">×</span>
            `;

            // Select chat handler
            chatItem.addEventListener('click', () => {
                this.onSelectChat(chat.chat_id);
            });

            // Delete chat handler
            const deleteBtn = chatItem.querySelector('.delete-chat');
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.onDeleteChat(chat.chat_id);
            });

            listContainer.appendChild(chatItem);
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
