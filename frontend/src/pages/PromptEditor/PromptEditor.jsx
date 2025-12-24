import React, { useState, useEffect } from 'react';
import './PromptEditor.css';

function PromptEditor() {
  const [systemPrompt, setSystemPrompt] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchSystemPrompt();
  }, []);

  const fetchSystemPrompt = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/system-prompt');
      const data = await response.json();
      setSystemPrompt(data.prompt);
    } catch (error) {
      setMessage('Error loading system prompt');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setMessage('');
      
      const response = await fetch('/api/system-prompt', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: systemPrompt }),
      });

      if (response.ok) {
        setMessage('System prompt saved successfully!');
        setTimeout(() => setMessage(''), 3000);
      } else {
        setMessage('Error saving system prompt');
      }
    } catch (error) {
      setMessage('Error saving system prompt');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="prompt-editor">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading prompt editor...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="prompt-editor">
      <header className="prompt-header">
        <div>
          <h1>System Prompt Editor</h1>
          <p>Configure the overall behavior and personality of all voice agents</p>
        </div>
        <button onClick={() => window.location.href = '/'} className="back-btn">
          ← Back to Dashboard
        </button>
      </header>

      <div className="prompt-content">
        <div className="prompt-info">
          <h3>About System Prompts</h3>
          <p>
            The system prompt defines the core principles, personality, and behavior
            that all voice agents will follow. This serves as the foundation, with
            client-specific prompts (background, rules, scripts, FAQs) layered on top.
          </p>
        </div>

        <div className="editor-section">
          <label htmlFor="system-prompt">System Prompt</label>
          <textarea
            id="system-prompt"
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            placeholder="Enter the overall system prompt..."
            rows={25}
          />
        </div>

        <div className="editor-actions">
          <button 
            onClick={handleSave} 
            className="save-btn"
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save System Prompt'}
          </button>
          {message && (
            <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
              {message}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default PromptEditor;

