export class ApiService {
    constructor(baseUrl, authToken = null) {
        this.baseUrl = baseUrl;
        this.authToken = authToken;
    }

    async initSession(sessionToken) {
        try {
            const response = await fetch(`${this.baseUrl}/widget/init/${sessionToken}`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`Failed to initialize session: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Session initialization error:', error);
            throw error;
        }
    }

    async loadChats(sessionToken) {
        try {
            const response = await fetch(`${this.baseUrl}/widget/${sessionToken}/chats`);
            
            if (!response.ok) {
                throw new Error(`Failed to load chats: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to load chats:', error);
            throw error;
        }
    }

    async createChat(sessionToken) {
        try {
            const response = await fetch(`${this.baseUrl}/widget/${sessionToken}/chats`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`Failed to create chat: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to create chat:', error);
            throw error;
        }
    }

    async deleteChat(sessionToken, chatId) {
        try {
            const response = await fetch(`${this.baseUrl}/widget/${sessionToken}/chats/${chatId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error(`Failed to delete chat: ${response.status}`);
            }

            return true;
        } catch (error) {
            console.error('Failed to delete chat:', error);
            throw error;
        }
    }

    async sendMessage(sessionToken, chatId, content) {
        try {
            const requestBody = { content };
            
            if (this.authToken) {
                requestBody.authorization = this.authToken;
            }

            const response = await fetch(
                `${this.baseUrl}/widget/${sessionToken}/chats/${chatId}/messages`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestBody)
                }
            );

            if (!response.ok) {
                throw new Error(`Failed to send message: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to send message:', error);
            throw error;
        }
    }
}
