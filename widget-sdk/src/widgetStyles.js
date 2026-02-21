// Widget styles stored as a plain JS string.
// This is injected into the page at runtime via a <style> tag,
// making the widget fully self-contained without any separate stylesheet.
// Using a plain JS string (not ?inline) ensures compatibility with all
// build environments including Docker.

const widgetStyles = `
/* ============================================================
   Widget SDK — scoped styles
   All rules are scoped under .chat-widget-wrapper to avoid
   polluting the host page.
   ============================================================ */

/* ─── Wrapper ─── */
.chat-widget-wrapper {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 10000;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;

    --primary-color: #667eea;
    --primary-hover: #5a67d8;
    --bg-color: #f5f5f5;
    --sidebar-bg: #fff;
    --border-color: #e0e0e0;
    --text-color: #2d3748;
    --text-secondary: #4a5568;
    --danger-color: #e53e3e;
    --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 8px rgba(0, 0, 0, 0.08);
    --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.1);
    --shadow-primary: 0 4px 15px rgba(102, 126, 234, 0.4);
    --transition-fast: 0.15s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-base: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-smooth: 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    --radius-sm: 6px;
    --radius-md: 12px;
    --radius-lg: 18px;
    --radius-full: 50%;
}

/* Scoped box-sizing reset */
.chat-widget-wrapper *,
.chat-widget-wrapper *::before,
.chat-widget-wrapper *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

/* ─── Launcher Button ─── */
.chat-launcher {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 10001;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: #667eea;
    color: white;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1), 0 4px 15px rgba(102,126,234,0.4);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.chat-launcher:hover {
    transform: scale(1.1);
    background: #5a67d8;
}

/* ─── Chat Window ─── */
.chat-widget {
    width: 420px;
    height: 600px;
    background: white;
    border-radius: 18px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    margin-bottom: 16px;
    border: 1px solid #e0e0e0;
    min-height: 0;
}

/* ─── Header ─── */
.chat-header {
    padding: 16px 20px;
    background: #667eea;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
}

.header-info {
    display: flex;
    align-items: center;
    gap: 10px;
}

.header-info .dot {
    width: 8px;
    height: 8px;
    background: #4ade80;
    border-radius: 50%;
    box-shadow: 0 0 10px #4ade80;
    display: inline-block;
}

.header-info .title {
    font-weight: 600;
    font-size: 0.95rem;
}

.close-btn {
    background: transparent;
    border: none;
    color: white;
    font-size: 24px;
    cursor: pointer;
    opacity: 0.8;
    line-height: 1;
    padding: 0;
}

.close-btn:hover {
    opacity: 1;
}

/* ─── Error Banner ─── */
.error-banner {
    background: #fff5f5;
    color: #c53030;
    padding: 10px 16px;
    font-size: 0.85rem;
    border-bottom: 1px solid #fed7d7;
    flex-shrink: 0;
}

/* ─── Body (sidebar + chat area) ─── */
.chat-body {
    display: flex;
    flex: 1;
    overflow: hidden;
    min-height: 0;
    max-height: 100%;
}

/* ─── Sidebar / Chat List ─── */
.chat-list {
    width: 140px;
    min-width: 140px;
    border-right: 1px solid #e0e0e0;
    background: #fff;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
}

.chat-list-header {
    padding: 15px;
    border-bottom: 1px solid #e0e0e0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
}

.chat-list-header h3 {
    font-size: 0.9rem;
    font-weight: 600;
    color: #2d3748;
    margin: 0;
}

.new-chat-btn {
    padding: 4px 8px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 0.8rem;
    cursor: pointer;
    transition: background 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}

.new-chat-btn:hover {
    background: #5a67d8;
}

.chats {
    flex: 1;
    overflow-y: auto;
}

.chat-item {
    padding: 12px 15px;
    cursor: pointer;
    font-size: 0.85rem;
    color: #4a5568;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: background 0.15s cubic-bezier(0.4, 0, 0.2, 1);
    border-bottom: 1px solid rgba(0,0,0,0.04);
}

.chat-item:hover {
    background: #f7fafc;
}

.chat-item.active {
    background: #ebf4ff;
    color: #667eea;
    font-weight: 600;
}

.chat-title {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin-right: 4px;
    line-height: 1.4;
}

.delete-chat-btn {
    background: none;
    border: none;
    color: #e53e3e;
    cursor: pointer;
    font-size: 1.2rem;
    opacity: 0;
    transition: opacity 0.15s cubic-bezier(0.4, 0, 0.2, 1);
    flex-shrink: 0;
    line-height: 1;
    padding: 0 2px;
}

.chat-item:hover .delete-chat-btn {
    opacity: 1;
}

.empty-chats {
    padding: 16px;
    color: #9ca3af;
    font-size: 0.85rem;
    text-align: center;
}

/* ─── Chat Area ─── */
.chat-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #fff;
    min-width: 0;
    min-height: 0;
    overflow: hidden;
}

.back-btn {
    padding: 10px;
    background: none;
    border: none;
    color: #667eea;
    cursor: pointer;
    font-weight: 600;
    text-align: left;
    flex-shrink: 0;
}

/* ─── Messages ─── */
.messages {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 16px;
    background: #fafafa;
    min-height: 0;
    -webkit-overflow-scrolling: touch;
    overscroll-behavior: contain;
}

.message {
    max-width: 85%;
    padding: 12px 16px;
    border-radius: 12px;
    font-size: 0.95rem;
    line-height: 1.6;
    position: relative;
    word-wrap: break-word;
}

.message.user {
    align-self: flex-end;
    background: #667eea;
    color: white;
    border-bottom-right-radius: 4px;
}

.message.ai,
.message.assistant {
    align-self: flex-start;
    background: white;
    color: #2d3748;
    border: 1px solid #e0e0e0;
    border-bottom-left-radius: 4px;
}

/* ─── Message Content (Markdown) ─── */
.message-content {
    line-height: 1.6;
    word-wrap: break-word;
}

.message-content > *:first-child { margin-top: 0; }
.message-content > *:last-child  { margin-bottom: 0; }
.message-content p                { margin: 0 0 10px 0; }
.message-content p:last-child     { margin-bottom: 0; }
.message-content ul,
.message-content ol               { margin: 10px 0; padding-left: 20px; }
.message-content li               { margin-bottom: 4px; }
.message-content code             { background: rgba(0,0,0,0.05); padding: 2px 4px; border-radius: 4px; font-family: monospace; }
.message-content pre              { background: #2d3748; color: #fff; padding: 10px; border-radius: 6px; overflow-x: auto; margin: 8px 0; }

/* ─── Status Hint ─── */
.status-hint {
    font-size: 0.85rem;
    opacity: 0.75;
    margin-bottom: 4px;
    font-style: italic;
    animation: statusPulse 1.2s ease-in-out infinite;
}

@keyframes statusPulse {
    0%   { opacity: 0.4; }
    50%  { opacity: 0.85; }
    100% { opacity: 0.4; }
}

/* ─── Typing Indicator (inline in message) ─── */
.typing-indicator {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 0;
    transition: opacity 0.15s ease-in-out;
}

.typing-indicator span {
    width: 8px;
    height: 8px;
    background: #94a3b8;
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
    40%           { transform: scale(1); opacity: 1; }
}

/* ─── Standalone typing dots ─── */
.typing {
    display: flex;
    gap: 4px;
    padding: 10px;
    align-self: flex-start;
}

.typing span {
    width: 8px;
    height: 8px;
    background: #cbd5e0;
    border-radius: 50%;
    animation: typingBounce 1.4s infinite ease-in-out both;
}

.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
    0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
    40%           { transform: scale(1.1); opacity: 1; }
}

/* ─── Hints ─── */
.message-hints {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 10px;
}

.hint-button {
    background: rgba(79,70,229,0.1);
    border: 1px solid rgba(79,70,229,0.3);
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 0.85em;
    color: #4f46e5;
    cursor: pointer;
    transition: all 0.2s;
}

.hint-button:hover {
    background: rgba(79,70,229,0.2);
    border-color: #4f46e5;
}

/* ─── Follow-up badge ─── */
.follow-up-badge {
    font-size: 0.7rem;
    background: #ebf4ff;
    color: #667eea;
    padding: 2px 8px;
    border-radius: 10px;
    margin-bottom: 8px;
    display: inline-block;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border: 1px solid rgba(102,126,234,0.2);
}

/* ─── Input Area ─── */
.chat-input-area {
    padding: 12px;
    border-top: 1px solid #e0e0e0;
    display: flex;
    gap: 10px;
    align-items: flex-end;
    flex-shrink: 0;
    background: #fff;
}

.chat-input {
    flex: 1;
    padding: 10px 12px;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    outline: none;
    resize: none;
    font-family: inherit;
    font-size: 14px;
    min-height: 42px;
    max-height: 120px;
    line-height: 1.4;
    transition: border-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}

.chat-input:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 2px rgba(102,126,234,0.1);
}

.send-btn {
    padding: 0 16px;
    height: 42px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    flex-shrink: 0;
}

.send-btn:hover {
    background: #5a67d8;
    transform: translateY(-1px);
}

.send-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

/* ─── Mobile toggle button ─── */
.mobile-chat-list-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 10px 16px;
    background: #f8fafc;
    border: none;
    border-bottom: 1px solid #e2e8f0;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    color: #64748b;
    flex-shrink: 0;
}

/* ─── Animation ─── */
.animated-fade-in {
    animation: slideUpFade 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUpFade {
    from { opacity: 0; transform: translateY(20px) scale(0.95); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}

/* ============================================================
   MOBILE — 480px and below
   ============================================================ */
@media screen and (max-width: 480px) {
    .chat-widget-wrapper {
        position: fixed;
        bottom: 0; right: 0; left: 0; top: 0;
        z-index: 99999;
        display: block;
    }

    .chat-widget-wrapper:not(.open) {
        z-index: 100;
    }

    .chat-widget {
        width: 100vw; height: 100vh;
        max-width: 100vw; max-height: 100vh;
        border-radius: 0; margin: 0;
        display: flex; flex-direction: column; overflow: hidden;
    }

    .chat-widget-wrapper:not(.open) .chat-widget {
        display: none;
    }

    .chat-launcher {
        position: fixed;
        bottom: 16px; right: 16px;
        z-index: 100000;
    }

    .chat-header { padding: 12px 16px; }

    .chat-body { flex-direction: column; }

    .chat-list {
        display: none;
        width: 100%; min-width: unset;
        min-height: 80px; max-height: 35vh;
        border-right: none; border-bottom: 1px solid #e2e8f0;
        overflow-y: auto; -webkit-overflow-scrolling: touch;
        flex-shrink: 0;
    }

    .chat-list.mobile-visible {
        display: flex; flex-direction: column;
    }

    .chat-area {
        flex: 1; display: flex; flex-direction: column;
        min-height: 0; overflow: hidden; max-height: 100%;
    }

    .messages {
        flex: 1; overflow-y: auto;
        -webkit-overflow-scrolling: touch; overscroll-behavior: contain;
        padding: 12px; gap: 10px; min-height: 0; margin-bottom: 60px;
    }

    .chat-input-area {
        flex-shrink: 0 !important; position: fixed !important;
        bottom: 0 !important; left: 0 !important; right: 0 !important;
        width: 100% !important; background: #fff !important;
        border-top: 1px solid #e2e8f0 !important;
        z-index: 1000 !important; display: flex !important;
        padding: 10px 12px; gap: 8px;
    }

    .message { max-width: 85%; padding: 10px 14px; font-size: 14px; line-height: 1.5; }
    .chat-input { padding: 10px 12px; font-size: 14px; min-height: 40px; }
    .send-btn { padding: 0 14px; height: 40px; }
    .mobile-chat-list-toggle { display: flex; }
}

/* ============================================================
   TABLET — 481px to 768px
   ============================================================ */
@media screen and (min-width: 481px) and (max-width: 768px) {
    .chat-widget-wrapper { bottom: 16px; right: 16px; left: auto; top: auto; }
    .chat-launcher { bottom: 16px; right: 16px; }
    .chat-widget { width: 90vw; max-width: 420px; height: 70vh; max-height: 600px; border-radius: 16px; }
    .chat-body { flex-direction: row; }
    .chat-list { width: 120px; min-width: 120px; }
    .mobile-chat-list-toggle { display: none; }
}

/* ============================================================
   SMALL DESKTOP — 769px to 1024px
   ============================================================ */
@media screen and (min-width: 769px) and (max-width: 1024px) {
    .chat-widget { width: 400px; height: 580px; }
    .mobile-chat-list-toggle { display: none; }
}

/* ============================================================
   LARGE DESKTOP — 1025px and above
   ============================================================ */
@media screen and (min-width: 1025px) {
    .chat-widget { width: 420px; height: 600px; }
    .mobile-chat-list-toggle { display: none; }
}

/* ============================================================
   SHORT SCREENS
   ============================================================ */
@media screen and (max-height: 500px) {
    .chat-widget { height: calc(100vh - 20px); }
    .messages { flex: 1; min-height: 0; }
}
`;

export default widgetStyles;
