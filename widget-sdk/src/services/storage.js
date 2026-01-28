export class StorageService {
    constructor(sessionToken) {
        this.sessionToken = sessionToken;
        this.storageKey = `widget_msgs_${sessionToken}`;
    }

    loadMessages() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored) {
                return JSON.parse(stored);
            }
            return {};
        } catch (error) {
            console.error('Failed to load messages from storage:', error);
            return {};
        }
    }

    saveMessages(messages) {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(messages));
        } catch (error) {
            console.error('Failed to save messages to storage:', error);
        }
    }

    clearMessages() {
        try {
            localStorage.removeItem(this.storageKey);
        } catch (error) {
            console.error('Failed to clear messages from storage:', error);
        }
    }
}
