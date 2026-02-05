import React from 'react';
import './ApiKeyModal.css';

function ApiKeyModal({ apiKey, onClose }) {
    const [copied, setCopied] = React.useState(false);

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(apiKey);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    };

    return (
        <div className="api-key-modal-overlay" onClick={onClose}>
            <div className="api-key-modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="api-key-modal-header">
                    <h2>Your API Key</h2>
                </div>

                <div className="api-key-modal-body">
                    <div className="api-key-warning">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                        <p><strong>Important:</strong> This is the only time you'll see this API key. Please copy and save it securely.</p>
                    </div>

                    <div className="api-key-display">
                        <code>{apiKey}</code>
                    </div>

                    <button
                        onClick={handleCopy}
                        className={`copy-btn ${copied ? 'copied' : ''}`}
                    >
                        {copied ? (
                            <>
                                <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                                Copied!
                            </>
                        ) : (
                            <>
                                <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                                    <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                                    <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
                                </svg>
                                Copy to Clipboard
                            </>
                        )}
                    </button>
                </div>

                <div className="api-key-modal-footer">
                    <button onClick={onClose} className="got-it-btn">
                        Got it, I saved my API key
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ApiKeyModal;
