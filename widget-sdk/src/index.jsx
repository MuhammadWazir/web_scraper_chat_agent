import React from 'react';
import { createRoot } from 'react-dom/client';
import { ChatWidget as InternalChatWidget } from './ChatWidget.jsx';
// Plain JS import — works in every build environment (no Vite ?inline needed).
import widgetStyles from './widgetStyles.js';

// ─── Self-contained style injection ───────────────────────────────────────────
// Injects a <style> element exactly once so the widget works on any page
// without requiring the host to load a separate stylesheet.
function injectStyles() {
    const STYLE_ID = '__web-scraper-chat-widget-styles__';
    if (!document.getElementById(STYLE_ID)) {
        const style = document.createElement('style');
        style.id = STYLE_ID;
        style.textContent = widgetStyles;
        document.head.appendChild(style);
    }
}

class ChatWidget {
    constructor(config = {}) {
        this.config = config;
        this.container = null;
        this.root = null;
        this.sessionToken = config.sessionToken || null;
    }

    async init(sessionToken) {
        this.sessionToken = sessionToken;
        // Initialization logic if needed
        return Promise.resolve();
    }

    render(selector) {
        // Inject styles before rendering
        injectStyles();

        this.container = document.querySelector(selector);
        if (!this.container) {
            console.error(`ChatWidget: Container "${selector}" not found`);
            return;
        }

        const token = this.sessionToken || this.config.sessionToken || this._parseSessionToken();

        if (!token) {
            console.warn('ChatWidget: No session token provided. Widget may not initialize correctly.');
        }

        this.root = createRoot(this.container);
        this.root.render(
            <InternalChatWidget
                sessionToken={token}
                baseUrl={this.config.baseUrl}
                authToken={this.config.authToken}
            />
        );
    }

    destroy() {
        if (this.root) {
            this.root.unmount();
            this.root = null;
        }
    }

    _parseSessionToken() {
        if (typeof window === 'undefined') return null;
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('s') || urlParams.get('token') || window.CHAT_WIDGET_SESSION;
    }
}



// Dedicated initialization function for simple global script usage
const init = (config = {}) => {
    const widget = new ChatWidget(config);
    return {
        async init(sessionToken) {
            await widget.init(sessionToken);
            return this;
        },
        render(selector) {
            widget.render(selector);
            return this;
        },
        destroy() {
            widget.destroy();
        }
    };
};

// Attach to window for direct global access (standard practice for widgets)
if (typeof window !== 'undefined') {
    window.ChatWidget = ChatWidget;
    window.WebScraperChat = { ChatWidget, init };
}

// Named export
export { ChatWidget, init };
// Default export
export default ChatWidget;
