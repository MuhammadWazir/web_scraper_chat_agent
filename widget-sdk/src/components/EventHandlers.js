import { isMobileView } from '../utils/dom.js';

export class EventHandlers {
    constructor(widget) {
        this.widget = widget;
        this.shadowRoot = widget.shadowRoot;
    }

    bindAll() {
        this.bindLauncherEvents();
        this.bindHeaderEvents();
        this.bindChatEvents();
        this.bindInputEvents();
        this.bindMobileEvents();
    }

    bindLauncherEvents() {
        const launcher = this.shadowRoot.querySelector('.launcher');
        const container = this.shadowRoot.querySelector('.widget-container');

        launcher.addEventListener('click', () => {
            this.toggleWidget();
        });
    }

    bindHeaderEvents() {
        const closeBtn = this.shadowRoot.querySelector('.close-btn');

        closeBtn.addEventListener('click', () => {
            this.toggleWidget();
        });
    }

    bindChatEvents() {
        const newChatBtn = this.shadowRoot.querySelector('.new-chat-btn');

        newChatBtn.addEventListener('click', async () => {
            await this.widget.createChat();
        });
    }

    bindInputEvents() {
        const sendBtn = this.shadowRoot.querySelector('.send-btn');
        const input = this.shadowRoot.querySelector('.chat-input');

        const sendMessage = async () => {
            await this.widget.sendMessage();
        };

        sendBtn.addEventListener('click', sendMessage);

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    bindMobileEvents() {
        const backBtn = this.shadowRoot.querySelector('.back-btn');

        backBtn.addEventListener('click', () => {
            this.showMobileSidebar();
        });
    }

    toggleWidget() {
        const launcher = this.shadowRoot.querySelector('.launcher');
        const container = this.shadowRoot.querySelector('.widget-container');
        
        const isClosed = container.classList.contains('closed');
        
        if (isClosed) {
            container.classList.remove('closed');
            launcher.style.display = 'none';
        } else {
            container.classList.add('closed');
            launcher.style.display = 'flex';
            // Reset to sidebar view on close for mobile
            if (isMobileView()) {
                this.showMobileSidebar();
            }
        }
    }

    showMobileChat() {
        if (!isMobileView()) return;

        const content = this.shadowRoot.querySelector('.content');
        content.classList.add('mobile-chat-view');
        content.classList.remove('mobile-sidebar-view');
    }

    showMobileSidebar() {
        if (!isMobileView()) return;

        const content = this.shadowRoot.querySelector('.content');
        content.classList.add('mobile-sidebar-view');
        content.classList.remove('mobile-chat-view');
        
        // Clear active chat
        this.widget.activeChatId = null;
        this.widget.renderMessages();
    }
}
