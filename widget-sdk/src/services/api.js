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
                // Try to parse error details from response
                let errorMessage = `Failed to initialize session: ${response.status}`;
                try {
                    const errorData = await response.json();
                    if (errorData.detail) {
                        errorMessage = errorData.detail;
                    }
                } catch (e) {
                    // If parsing fails, use default message
                }
                throw new Error(errorMessage);
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

    /**
     * Send a message with streaming response and status hints
     * @param {string} sessionToken - Widget session token
     * @param {string} chatId - Chat ID
     * @param {string} content - Message content
     * @param {function} onChunk - Callback for each chunk
     *   Receives objects with: {type, message?, data?}
     *   - type: "status_hint" | "content" | "title_updated" | "complete"
     *   - message: status hint text (for status_hint)
     *   - data: content chunk (for content)
     */
    async sendMessageStream(sessionToken, chatId, content, onChunk, isFollowUp = false) {
        try {
            const requestBody = { 
                content,
                is_follow_up: isFollowUp
            };
            
            if (this.authToken) {
                requestBody.authorization = this.authToken;
            }

            const response = await fetch(
                `${this.baseUrl}/widget/${sessionToken}/chats/${chatId}/messages-stream`,
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

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            let buffer = '';

            const processLine = async (line) => {
                const trimmed = line.trim();
                if (!trimmed) return;
                try {
                    const jsonData = JSON.parse(trimmed);
                    if (onChunk) {
                        await onChunk(jsonData);
                    }
                } catch (parseError) {
                    console.warn('Failed to parse chunk:', trimmed, parseError);
                }
            };

            while (true) {
                const { done, value } = await reader.read();

                if (value) {
                    buffer += decoder.decode(value, { stream: true });
                }

                if (done) {
                    // Flush the TextDecoder and any remaining buffered JSON
                    buffer += decoder.decode();
                    if (buffer.trim()) {
                        buffer = buffer.replace(/}\s*{/g, '}\n{');
                        for (const line of buffer.split('\n')) {
                            await processLine(line);
                        }
                    }
                    break;
                }

                // Split fused JSON objects — same aggressive regex as the frontend
                buffer = buffer.replace(/}\s*{/g, '}\n{');
                const lines = buffer.split('\n');
                // Keep the last (potentially incomplete) line in the buffer
                buffer = lines.pop() ?? '';

                for (const line of lines) {
                    await processLine(line);
                }
            }
        } catch (error) {
            console.error('Failed to send message stream:', error);
            throw error;
        }
    }
    async loadMessages(sessionToken, chatId) {
        try {
            const response = await fetch(`${this.baseUrl}/widget/${sessionToken}/chats/${chatId}/messages`);

            if (!response.ok) {
                throw new Error(`Failed to load messages: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Failed to load messages:', error);
            throw error;
        }
    }
}