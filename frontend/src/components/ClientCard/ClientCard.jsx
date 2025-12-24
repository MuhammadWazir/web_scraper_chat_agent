import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './ClientCard.css';

function ClientCard({ client }) {
  const navigate = useNavigate();
  const [showPromptEditor, setShowPromptEditor] = useState(false);
  const [showVoiceModal, setShowVoiceModal] = useState(false);
  const [prompt, setPrompt] = useState('');
  const [promptLoading, setPromptLoading] = useState(false);
  const [promptSaving, setPromptSaving] = useState(false);
  const [voices, setVoices] = useState([]);
  const [voiceId, setVoiceId] = useState('');
  const [voiceSaving, setVoiceSaving] = useState(false);

  const prompts = client?.prompts;
  const areAllPromptsNull = !prompts || Object.values(prompts).every((v) => v === null || v === undefined);
  const isGenerating = areAllPromptsNull;

  const handleClick = (e) => {
    if (isGenerating) {
      e.preventDefault();
      e.stopPropagation();
      return;
    }
    navigate(`/client/${client.url_slug}`);
  };

  const openPromptEditor = async (e) => {
    e.stopPropagation();
    try {
      setPromptLoading(true);
      const resp = await fetch(`/api/client/${client.url_slug}/overall-prompt`);
      if (resp.ok) {
        const data = await resp.json();
        setPrompt(data.overall_prompt || '');
        setShowPromptEditor(true);
      }
    } finally {
      setPromptLoading(false);
    }
  };

  const savePrompt = async () => {
    try {
      setPromptSaving(true);
      await fetch(`/api/client/${client.url_slug}/overall-prompt`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ overall_prompt: prompt }),
      });
      setShowPromptEditor(false);
    } finally {
      setPromptSaving(false);
    }
  };

  const openVoiceModal = async (e) => {
    e.stopPropagation();
    try {
      const [voicesResp, currentResp] = await Promise.all([
        fetch('/api/voices'),
        fetch(`/api/client/${client.url_slug}/voice`),
      ]);
      if (voicesResp.ok) {
        const vd = await voicesResp.json();
        const list = Array.isArray(vd?.voices) ? vd.voices : (vd?.data || []);
        setVoices(list);
      }
      if (currentResp.ok) {
        const cd = await currentResp.json();
        setVoiceId(cd.voice_id || '');
      }
      setShowVoiceModal(true);
    } catch (_) {}
  };

  const saveVoice = async () => {
    try {
      setVoiceSaving(true);
      await fetch(`/api/client/${client.url_slug}/voice`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voice_id: voiceId || null }),
      });
      setShowVoiceModal(false);
    } finally {
      setVoiceSaving(false);
    }
  };

  return (
    <div className={`client-card ${isGenerating ? 'generating' : ''}`} onClick={handleClick}>
      <div className="client-card-header">
        <h3>{client.company_name || 'Unknown Company'}</h3>
      </div>
      <div className="client-card-body">
        <p className="client-url">
          <strong>Website:</strong> {client.request?.website_url}
        </p>
        {client.url_slug && (
          <p className="client-url-slug">
            <strong>URL:</strong> /client/{client.url_slug}
          </p>
        )}
        <p className="client-audience">
          <strong>Audience:</strong> {client.request?.target_audience || 'N/A'}
        </p>
        {isGenerating && (
          <div className="generating-status">
            <span className="spinner"></span>
            <p>Generating prompts for {client.company_name}...</p>
          </div>
        )}
      </div>
      <div className="client-card-footer">
        <button className="view-btn" disabled={isGenerating}>
          {isGenerating ? 'Generating...' : 'View Agent →'}
        </button>
        <div className="card-actions">
          <button className="secondary-btn" disabled={promptLoading} onClick={openPromptEditor}>
            Edit Prompt
          </button>
          <button className="secondary-btn" onClick={openVoiceModal}>
            Select Voice
          </button>
        </div>
      </div>

      {showPromptEditor && (
        <div className="modal-overlay" onClick={() => setShowPromptEditor(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Edit Overall Prompt</h2>
            </div>
            <div className="form-group">
              <label>Prompt Template</label>
              <textarea className="prompt-textarea" value={prompt} onChange={(e) => setPrompt(e.target.value)} />
            </div>
            <div className="modal-actions">
              <div className="action-buttons">
                <button className="cancel-btn" onClick={() => setShowPromptEditor(false)} disabled={promptSaving}>Cancel</button>
                <button className="save-btn" onClick={savePrompt} disabled={promptSaving}>{promptSaving ? 'Saving...' : 'Save'}</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showVoiceModal && (
        <div className="modal-overlay" onClick={() => setShowVoiceModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Select Voice</h2>
            </div>
            <div className="form-group">
              <label>Voice</label>
              <select className="form-input" value={voiceId} onChange={(e) => setVoiceId(e.target.value)}>
                <option value="">Default Agent Voice</option>
                {voices.map((v) => (
                  <option key={v.voice_id || v.id} value={(v.voice_id || v.id) || ''}>{v.name || 'Unnamed Voice'}</option>
                ))}
              </select>
            </div>
            <div className="modal-actions">
              <div className="action-buttons">
                <button className="cancel-btn" onClick={() => setShowVoiceModal(false)} disabled={voiceSaving}>Cancel</button>
                <button className="save-btn" onClick={saveVoice} disabled={voiceSaving}>{voiceSaving ? 'Saving...' : 'Save'}</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ClientCard;

