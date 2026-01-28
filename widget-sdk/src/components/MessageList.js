import { createElement, scrollToBottom } from '../utils/dom.js';

export class MessageList {
    constructor(shadowRoot, messages) {
        this.shadowRoot = shadowRoot;
        this.messages = messages;
    }

    render() {
        const container = this.shadowRoot.querySelector('.messages');
        if (!container) return;

        container.innerHTML = '';

        this.messages.forEach(msg => {
            const messageElement = createElement('div', `message ${msg.role}`);
            messageElement.textContent = msg.content;
            container.appendChild(messageElement);
        });

        // Scroll to bottom after rendering
        scrollToBottom(container);
    }

    appendMessage(message) {
        const container = this.shadowRoot.querySelector('.messages');
        if (!container) return;

        const messageElement = createElement('div', `message ${message.role}`);
        messageElement.textContent = message.content;
        container.appendChild(messageElement);

        // Scroll to bottom after appending
        scrollToBottom(container);
    }

    showTypingIndicator() {
        const container = this.shadowRoot.querySelector('.messages');
        if (!container) return;

        // Remove existing indicator if any
        this.hideTypingIndicator();

        const indicator = createElement('div', 'message ai typing');
        indicator.id = 'typing-indicator';
        indicator.innerHTML = '<span></span><span></span><span></span>';
        container.appendChild(indicator);
        scrollToBottom(container);
    }

    hideTypingIndicator() {
        const indicator = this.shadowRoot.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
}
