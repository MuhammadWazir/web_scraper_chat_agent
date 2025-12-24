import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './ClientPage.css';

function ClientPage() {
  const { clientId } = useParams();
  const navigate = useNavigate();
  const [client, setClient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [widgetLoaded, setWidgetLoaded] = useState(false);
  const [overallPromptData, setOverallPromptData] = useState(null);
  const [clientVoiceId, setClientVoiceId] = useState('');
  const widgetContainerRef = useRef(null);
  const prompts = client?.prompts;
  const areAllPromptsNull = !prompts || Object.values(prompts).every((v) => v === null || v === undefined);
  const isGenerating = areAllPromptsNull;

  useEffect(() => {
    fetchClient();
    fetchOverallPrompt();
    fetchClientVoice();
  }, [clientId]);

  // Poll for prompts while they are being generated
  useEffect(() => {
    if (loading || error) return;
    if (!isGenerating) return;
    const intervalId = setInterval(() => {
      fetchClient(true);
    }, 5000);
    return () => clearInterval(intervalId);
  }, [loading, error, isGenerating, clientId]);

  useEffect(() => {
    // Load ElevenLabs script if not already loaded
    if (!document.querySelector('script[src*="elevenlabs"]')) {
      const script = document.createElement('script');
      script.src = 'https://unpkg.com/@elevenlabs/convai-widget-embed';
      script.async = true;
      document.body.appendChild(script);
    }

    // Initialize widget when client data is available
    if (client && widgetContainerRef.current && !isGenerating) {
      initializeWidget();
    }
  }, [client, isGenerating, clientVoiceId]);

  const fetchClient = async (silent = false) => {
    try {
      if (!silent) setLoading(true);
      const response = await fetch(`/api/client/${clientId}?t=${Date.now()}`, { cache: 'no-store' });
      
      if (!response.ok) {
        throw new Error('Client not found');
      }
      
      const data = await response.json();
      setClient(data);
    } catch (err) {
      setError(err.message);
    } finally {
      if (!silent) setLoading(false);
    }
  };

  const fetchOverallPrompt = async () => {
    try {
      const response = await fetch(`/api/client/${clientId}/overall-prompt`);
      if (response.ok) {
        const data = await response.json();
        setOverallPromptData(data);
      }
    } catch (err) {
      console.error('Error fetching overall prompt:', err);
    }
  };

  const fetchClientVoice = async () => {
    try {
      const resp = await fetch(`/api/client/${clientId}/voice`);
      if (resp.ok) {
        const data = await resp.json();
        setClientVoiceId(data.voice_id || '');
      }
    } catch (err) {
      // ignore
    }
  };

  const generateMainPrompt = (assets) => {
    const now = new Date();
    const daysOfWeek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const nytd = now.toLocaleString("en-US", { timeZone: "America/New_York", weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit'});
    const latd = now.toLocaleString("en-US", { timeZone: "America/Los_Angeles", weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit'});
    const sytd = now.toLocaleString("en-US", { timeZone: "Australia/Sydney", weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit'});
    
    
    // Helper function to escape quotes and clean text for HTML attribute
    const escapeForAttribute = (text) => {
      if (!text) return "";
      return text
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\n/g, " ")
        .replace(/\s+/g, " ")
        .trim();
    };
    
    // Use the custom or default overall prompt template
    let prompt = overallPromptData.overall_prompt || "";
    
    // Replace placeholders
    prompt = prompt
      .replace(/{day_of_week}/g, daysOfWeek[now.getUTCDay()])
      .replace(/{current_datetime_utc}/g, now.toISOString().replace("T",", ").replace("Z"," in UTC"))
      .replace(/{current_datetime_ny}/g, nytd)
      .replace(/{current_datetime_la}/g, latd)
      .replace(/{current_datetime_sydney}/g, sytd)
      .replace(/{background}/g, assets.background || "")
      .replace(/{rules}/g, assets.rules || "")
      .replace(/{script}/g, assets.script || "")
      .replace(/{faqs}/g, assets.faqs || "");
    
    
    // Return escaped prompt for use in HTML attribute
    return escapeForAttribute(prompt);
  };

  const initializeWidget = async () => {
    if (!widgetContainerRef.current || !client) return;

    // Clear existing widget
    widgetContainerRef.current.innerHTML = '';

    // Generate main prompt using client's prompts data
    const mainPrompt = generateMainPrompt(client.prompts);

    // Fetch signed URL from backend for security
    let signedUrl = '';
    try {
      const url = clientVoiceId ? `/api/signed-url?voice_id=${encodeURIComponent(clientVoiceId)}` : `/api/signed-url`;
      const resp = await fetch(url);
      if (resp.ok) {
        const data = await resp.json();
        signedUrl = data?.signed_url || '';
      }
    } catch (e) {
      // Non-fatal; widget can still attempt without signed url
    }

    // Create ElevenLabs widget element with all attributes
    const widget = document.createElement('elevenlabs-convai');
    if (signedUrl) {
      widget.setAttribute('signed-url', signedUrl);
    }
    widget.setAttribute('override-prompt', mainPrompt);
    widget.setAttribute('override-first-message', 'Hello! How can I help you today?');
    if (clientVoiceId) {
      widget.setAttribute('override-voice-id', clientVoiceId);
    }
    widget.setAttribute('avatar-orb-color-1', '#667eea');
    widget.setAttribute('avatar-orb-color-2', '#764ba2');
    
    widgetContainerRef.current.appendChild(widget);
  };

  if (loading) {
    return (
      <div className="client-page">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading client...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="client-page">
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="client-page">
      <div className="client-header">
        <div>
          <h1>{client?.company_name || 'Client Agent'}</h1>
          {overallPromptData?.is_custom && (
            <span className="custom-prompt-badge">● Custom Prompt Active</span>
          )}
        </div>
        <div className="header-actions">
          <button
            onClick={() => window.location.href = '/'}
            className="secondary-btn"
          >
            ← Back
          </button>
        </div>
      </div>
      
      <div ref={widgetContainerRef}>
        {/* ElevenLabs widget will be inserted here when prompts are ready */}
      </div>

    </div>
  );
}

export default ClientPage;

