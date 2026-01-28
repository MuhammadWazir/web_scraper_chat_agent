import { ChatWidget } from './ChatWidget.js';

// Export for both module and global usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ChatWidget };
} else {
    window.ChatWidget = ChatWidget;
}

export { ChatWidget };
