export function getTemplate() {
    return `
        <div class="launcher">💬</div>
        <div class="widget-container closed">
            <div class="header">
                <div class="header-left">
                    <span class="back-btn">←</span>
                    <span>AI Assistant</span>
                </div>
                <span class="close-btn">×</span>
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
}
