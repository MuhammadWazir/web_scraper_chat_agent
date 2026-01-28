export function parseSessionToken(sessionUrl) {
    let token = sessionUrl;
    
    if (sessionUrl.includes('?')) {
        const urlParams = new URLSearchParams(sessionUrl.split('?')[1]);
        token = urlParams.get('token') || token;
    } else if (sessionUrl.includes('/')) {
        const parts = sessionUrl.split('/');
        token = parts[parts.length - 1];
    }
    
    return token;
}

export function createElement(tag, className, innerHTML = '') {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (innerHTML) element.innerHTML = innerHTML;
    return element;
}

export function isMobileView() {
    return window.innerWidth < 640;
}

export function scrollToBottom(container) {
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}
