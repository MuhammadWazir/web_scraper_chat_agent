export const styles = `
    /* Base Reset & Box Sizing */
    *, *::before, *::after {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }

    :host { 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        
        /* CSS Variables */
        --primary-color: #667eea;
        --primary-hover: #5a67d8;
        --bg-color: #f5f5f5;
        --sidebar-bg: #fff;
        --border-color: #e0e0e0;
        --text-color: #2d3748;
        --text-secondary: #4a5568;
        --danger-color: #e53e3e;
        --shadow-sm: 0 2px 4px rgba(0,0,0,0.05);
        --shadow-md: 0 4px 8px rgba(0,0,0,0.08);
        --shadow-lg: 0 10px 25px rgba(0,0,0,0.1);
        --shadow-primary: 0 4px 15px rgba(102, 126, 234, 0.4);
        --transition-fast: 0.15s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-base: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-smooth: 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        --radius-sm: 6px;
        --radius-md: 12px;
        --radius-lg: 18px;
        --radius-full: 50%;
    }
    
    /* Launcher Button */
    .launcher {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        min-width: 60px;
        min-height: 60px;
        background: var(--primary-color);
        border-radius: var(--radius-full);
        color: white;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 28px;
        cursor: pointer;
        box-shadow: var(--shadow-primary);
        z-index: 99999;
        transition: transform var(--transition-base), background var(--transition-base);
        border: none;
        outline: none;
        user-select: none;
    }
    
    .launcher:hover {
        transform: scale(1.1);
        background: var(--primary-hover);
    }
    
    .launcher:active {
        transform: scale(1.05);
    }
    
    /* Widget Container */
    .widget-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 400px;
        height: 650px;
        max-width: calc(100vw - 40px);
        max-height: calc(100vh - 40px);
        background: var(--bg-color);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-lg);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        transition: transform var(--transition-smooth), opacity var(--transition-smooth);
        z-index: 99999;
        border: 1px solid rgba(0,0,0,0.05);
        will-change: transform;
    }
    
    .widget-container.closed {
        transform: translateY(120%);
        opacity: 0;
        pointer-events: none;
    }
    
    /* Header */
    .header {
        background: #fff;
        color: var(--text-color);
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        flex-shrink: 0;
        min-height: 60px;
    }
    
    .header-left {
        display: flex;
        align-items: center;
        gap: 10px;
        flex: 1;
        min-width: 0;
    }
    
    .header span {
        font-weight: 600;
        font-size: 1.1rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .back-btn {
        display: none;
        cursor: pointer;
        font-size: 1.4rem;
        padding: 5px;
        line-height: 1;
        user-select: none;
        color: var(--text-secondary);
        transition: color var(--transition-fast);
        flex-shrink: 0;
    }
    
    .back-btn:hover {
        color: var(--primary-color);
    }
    
    .close-btn {
        font-size: 28px;
        cursor: pointer;
        line-height: 1;
        user-select: none;
        color: var(--text-secondary);
        transition: color var(--transition-fast);
        flex-shrink: 0;
    }
    
    .close-btn:hover {
        color: var(--danger-color);
    }
    
    /* Content Area */
    .content {
        display: flex;
        flex: 1;
        overflow: hidden;
        min-height: 0;
        position: relative;
    }
    
    /* Sidebar */
    .sidebar {
        width: 140px;
        min-width: 140px;
        max-width: 140px;
        border-right: 1px solid var(--border-color);
        background: var(--sidebar-bg);
        overflow-y: auto;
        overflow-x: hidden;
        display: flex;
        flex-direction: column;
        flex-shrink: 0;
    }
    
    /* Custom Scrollbar */
    .sidebar::-webkit-scrollbar,
    .messages::-webkit-scrollbar {
        width: 6px;
    }
    
    .sidebar::-webkit-scrollbar-track,
    .messages::-webkit-scrollbar-track {
        background: transparent;
    }
    
    .sidebar::-webkit-scrollbar-thumb,
    .messages::-webkit-scrollbar-thumb {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 3px;
    }
    
    .sidebar::-webkit-scrollbar-thumb:hover,
    .messages::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 0, 0, 0.3);
    }
    
    /* New Chat Button */
    .new-chat-btn {
        margin: 10px;
        padding: 10px 12px;
        background: var(--primary-color);
        color: white;
        border: none;
        cursor: pointer;
        text-align: center;
        border-radius: var(--radius-sm);
        font-weight: 500;
        font-size: 0.9rem;
        transition: background var(--transition-fast), transform var(--transition-fast);
        flex-shrink: 0;
        white-space: nowrap;
    }
    
    .new-chat-btn:hover {
        background: var(--primary-hover);
    }
    
    .new-chat-btn:active {
        transform: scale(0.98);
    }
    
    /* Chat List */
    .chat-list {
        flex: 1;
        padding: 10px 0;
        overflow-y: auto;
        min-height: 0;
    }
    
    .chat-item {
        padding: 12px 15px;
        cursor: pointer;
        font-size: 0.9rem;
        color: var(--text-secondary);
        border-bottom: 1px solid transparent;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        position: relative;
        transition: background var(--transition-fast), color var(--transition-fast);
        user-select: none;
    }
    
    .chat-item:hover {
        background: #f7fafc;
        color: var(--primary-color);
    }
    
    .chat-item.active {
        background: #ebf4ff;
        color: var(--primary-color);
        font-weight: 600;
        border-right: 3px solid var(--primary-color);
    }
    
    .delete-chat {
        display: none;
        position: absolute;
        right: 8px;
        top: 50%;
        transform: translateY(-50%);
        color: var(--danger-color);
        font-size: 1.2rem;
        cursor: pointer;
        padding: 2px 6px;
        background: rgba(255, 255, 255, 0.95);
        border-radius: var(--radius-sm);
        line-height: 1;
        z-index: 10;
        transition: background var(--transition-fast);
    }
    
    .delete-chat:hover {
        background: #fff;
    }
    
    .chat-item:hover .delete-chat {
        display: block;
    }
    
    /* Main Chat Area */
    .main-chat {
        flex: 1;
        display: flex;
        flex-direction: column;
        background: linear-gradient(180deg, #fafafa 0%, #ffffff 100%);
        min-width: 0;
        overflow: hidden;
    }
    
    /* Messages Container */
    .messages {
        flex: 1;
        padding: 20px;
        overflow-y: auto;
        overflow-x: hidden;
        display: flex;
        flex-direction: column;
        gap: 12px;
        min-height: 0;
        scroll-behavior: smooth;
    }
    
    /* Message Bubbles */
    .message {
        max-width: 75%;
        padding: 12px 16px;
        border-radius: var(--radius-lg);
        line-height: 1.5;
        word-wrap: break-word;
        overflow-wrap: break-word;
        word-break: break-word;
        animation: slideIn var(--transition-smooth);
        position: relative;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .message.user {
        align-self: flex-end;
        background: var(--primary-color);
        color: white;
        border-bottom-right-radius: 4px;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .message.ai {
        align-self: flex-start;
        background: #fff;
        color: var(--text-color);
        border: 1px solid var(--border-color);
        border-bottom-left-radius: 4px;
        box-shadow: var(--shadow-sm);
    }
    
    /* Input Area */
    .input-area {
        padding: 15px;
        border-top: 1px solid var(--border-color);
        display: flex;
        gap: 10px;
        align-items: center;
        background: #fff;
        flex-shrink: 0;
    }
    
    .chat-input {
        flex: 1;
        min-width: 0;
        padding: 12px 15px;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        outline: none;
        font-size: 0.95rem;
        color: var(--text-color);
        background: #f8fafc;
        transition: border-color var(--transition-fast), background var(--transition-fast), box-shadow var(--transition-fast);
        font-family: inherit;
    }
    
    .chat-input:focus {
        border-color: var(--primary-color);
        background: #fff;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .chat-input::placeholder {
        color: #a0aec0;
    }
    
    .send-btn {
        background: var(--primary-color);
        color: white;
        border: none;
        width: 40px;
        height: 40px;
        min-width: 40px;
        min-height: 40px;
        border-radius: var(--radius-full);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform var(--transition-fast), background var(--transition-fast);
        flex-shrink: 0;
        outline: none;
    }
    
    .send-btn:hover {
        background: var(--primary-hover);
        transform: scale(1.05);
    }
    
    .send-btn:active {
        transform: scale(0.95);
    }
    
    .send-btn::after {
        content: '➤';
        font-size: 1.2rem;
        transform: translateX(2px);
    }
    
    /* Responsive Design - Mobile */
    @media (max-width: 640px) {
        .widget-container {
            width: 100%;
            height: 100%;
            max-width: 100vw;
            max-height: 100vh;
            bottom: 0;
            right: 0;
            border-radius: 0;
        }
        
        .sidebar {
            width: 100%;
            max-width: 100%;
            border-right: none;
            border-bottom: 1px solid var(--border-color);
        }
        
        .main-chat {
            width: 100%;
        }
        
        .content.mobile-chat-view .sidebar {
            display: none;
        }
        
        .content.mobile-chat-view .main-chat {
            display: flex;
        }
        
        .content.mobile-sidebar-view .sidebar {
            display: flex;
        }
        
        .content.mobile-sidebar-view .main-chat {
            display: none;
        }
        
        .mobile-chat-view .back-btn {
            display: block;
        }
        
        .message {
            max-width: 85%;
        }
    }
    
    /* Tablet Adjustments */
    @media (max-width: 768px) and (min-width: 641px) {
        .widget-container {
            width: 90%;
            height: 80%;
        }
    }
    
    /* Prevent text selection on UI elements */
    .header, .new-chat-btn, .chat-item, .send-btn, .launcher, .close-btn, .back-btn {
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
    }
    
    /* Allow text selection in messages and input */
    .message, .chat-input {
        -webkit-user-select: text;
        -moz-user-select: text;
        -ms-user-select: text;
        user-select: text;
    }

    /* Typing Indicator */
    .typing {
        display: flex;
        gap: 4px;
        padding: 12px 16px;
        align-items: center;
        min-height: 45px;
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
        40% { transform: scale(1.1); opacity: 1; }
    }
`;
