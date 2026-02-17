import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { authFetch } from '../../utils/auth';
import CompactChat from './CompactChat';
import './ClientPage.css';

function ClientPage({ onLogout }) {
  const { clientName, chatId } = useParams();
  const navigate = useNavigate();
  const isAdmin = localStorage.getItem('isAdminLoggedIn') === 'true';
  const [client, setClient] = useState(null);
  const [chats, setChats] = useState([]);
  const [messages, setMessages] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [tempChatId, setTempChatId] = useState(null);
  const inactivityTimerRef = useRef(null);

  // Settings Modal State
  const [showToolsModal, setShowToolsModal] = useState(false);
  const [tools, setTools] = useState([]);
  const [systemPrompt, setSystemPrompt] = useState('');
  const [newTool, setNewTool] = useState({
    name: '',
    description: '',
    url: '',
    method: 'GET',
    inputs: '{}',
    auth: 'none'
  });

  // Determine the actual client ID to use
  const actualClientId = client?.client_id;

  // Track the messages state
  const messagesRef = useRef(messages);
  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  // Inactivity / Follow-up logic
  useEffect(() => {
    if (inactivityTimerRef.current) {
      clearTimeout(inactivityTimerRef.current);
      inactivityTimerRef.current = null;
    }

    const currentChatId = selectedChatId || tempChatId;
    const chatMessages = messages[currentChatId] || [];

    if (currentChatId && !isTyping && chatMessages.length > 0) {
      const lastMessage = chatMessages[chatMessages.length - 1];

      if ((lastMessage.role === 'assistant' || lastMessage.ai_generated) && !lastMessage.isFollowUp) {
        inactivityTimerRef.current = setTimeout(() => {
          handleSendFollowUp(currentChatId);
        }, 3 * 60 * 1000); // 3 minutes
      }
    }

    return () => {
      if (inactivityTimerRef.current) {
        clearTimeout(inactivityTimerRef.current);
      }
    };
  }, [selectedChatId, tempChatId, isTyping, messages]);

  // Fetch client based on slug
  useEffect(() => {
    if (clientName) {
      fetchClientBySlug(clientName);
    }
  }, [clientName]);

  // Handle chatId from URL
  useEffect(() => {
    if (chatId && chats.length > 0) {
      setSelectedChatId(chatId);
    }
  }, [chatId, chats]);

  // Sync messages and navigate on select
  useEffect(() => {
    if (selectedChatId) {
      fetchMessages(selectedChatId);
      if (clientName) {
        navigate(`/${clientName}/${selectedChatId}`, { replace: true });
      }
    }
  }, [selectedChatId, clientName]);

  // Update tools/system prompt from client data
  useEffect(() => {
    if (client) {
      setTools(client.tools || []);
      setSystemPrompt(client.system_prompt || '');
    }
  }, [client]);

  const fetchClientBySlug = async (slug) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/clients/by-slug/${slug.toLowerCase()}`);
      if (response.ok) {
        const matchedClient = await response.json();
        setClient(matchedClient);
        fetchChats(matchedClient.client_id);
      } else {
        throw new Error('Client not found');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchChats = async (id) => {
    try {
      const response = await fetch(`/api/clients/${id}/chats`);
      if (response.ok) {
        const data = await response.json();
        setChats(data);
      }
    } catch (err) {
      console.error('Error fetching chats:', err);
    }
  };

  const fetchMessages = async (chatId) => {
    try {
      const response = await fetch(`/api/chats/${chatId}/messages`);
      if (response.ok) {
        const data = await response.json();
        const normalizedMessages = data.map(msg => ({
          ...msg,
          ai_generated: msg.ai_generated !== undefined ? msg.ai_generated : (msg.role === 'assistant')
        }));
        setMessages(prev => ({ ...prev, [chatId]: normalizedMessages }));
      }
    } catch (err) {
      console.error('Error fetching messages:', err);
    }
  };

  const handleNewChat = () => {
    setSelectedChatId(null);
    setTempChatId(null);
    setIsTyping(false);
    if (clientName) {
      navigate(`/${clientName}`, { replace: true });
    }
  };

  const handleSelectChat = (chatId) => {
    setSelectedChatId(chatId);
    setIsTyping(false);
  };

  const handleDeleteChat = async (chatId, e) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this chat?')) {
      return;
    }

    try {
      const response = await fetch(`/api/chats/${chatId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setChats(prev => prev.filter(chat => chat.chat_id !== chatId));
        if (selectedChatId === chatId) {
          handleNewChat();
        }
      } else {
        const error = await response.json();
        alert(`Error deleting chat: ${error.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error deleting chat:', err);
    }
  };

  const handleSendMessage = async (messageText) => {
    const tempUserMessageId = `temp-${Date.now()}`;
    const userMessage = {
      message_id: tempUserMessageId,
      content: messageText,
      ai_generated: false,
      created_at: new Date().toISOString()
    };

    let currentChatId = selectedChatId;
    let newChatCreated = false;

    // Add user message to UI immediately
    if (!currentChatId) {
      const newTempChatId = `temp-${Date.now()}`;
      setTempChatId(newTempChatId);
      setMessages(prev => ({
        ...prev,
        [newTempChatId]: [userMessage]
      }));
      currentChatId = newTempChatId;
    } else {
      setMessages(prev => ({
        ...prev,
        [currentChatId]: [...(prev[currentChatId] || []), userMessage]
      }));
    }

    setIsTyping(true);

    try {
      const response = await fetch('/api/chats/send-message-stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: currentChatId && !currentChatId.startsWith('temp-') ? currentChatId : null,
          client_id: actualClientId,
          message: messageText
        }),
      });

      if (!response.ok) throw new Error('Failed to send message');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let streamedContent = '';
      let currentStatusHint = null;
      let realChatId = currentChatId;
      let chatTitle = null;
      const tempAiMessageId = `temp-ai-${Date.now()}`;
      let buffer = '';
      let firstChunkReceived = false;

      const updateStreamingUI = (content, hint) => {
        const chatKey = realChatId || currentChatId;

        setMessages(prev => {
          const currentMessages = prev[chatKey] || [];
          const filteredMessages = currentMessages.filter(
            m => m.message_id !== tempAiMessageId
          );

          const aiMessage = {
            message_id: tempAiMessageId,
            content: content,
            statusHint: hint,
            ai_generated: true,
            role: 'assistant',
            streaming: true,
            created_at: new Date().toISOString()
          };

          return {
            ...prev,
            [chatKey]: [...filteredMessages, aiMessage]
          };
        });
      };


      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        buffer = buffer.replace(/}\s*{/g, '}\n{');
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmedLine = line.trim();
          if (!trimmedLine) continue;

          try {
            const jsonData = JSON.parse(trimmedLine);
            if (!firstChunkReceived) {
              setIsTyping(false);
              firstChunkReceived = true;
            }
            if (jsonData.type === 'chat_created') {
              realChatId = jsonData.chat_id;
              newChatCreated = true;
              setSelectedChatId(realChatId);
              setTempChatId(null);
              updateStreamingUI(streamedContent, currentStatusHint);
            } else if (jsonData.type === 'title_updated') {
              chatTitle = jsonData.title;
            } else if (jsonData.type === 'status_hint') {
              currentStatusHint = jsonData.message;
              updateStreamingUI(streamedContent, currentStatusHint);
              await new Promise(r => setTimeout(r, 0));
            } else if (jsonData.type === 'content') {
              currentStatusHint = null;
              streamedContent += jsonData.data || '';
              updateStreamingUI(streamedContent, null);
            } else if (jsonData.type === 'complete') {
              break;
            }
          } catch (e) {
            console.warn('Failed to parse chunk:', trimmedLine, e);
          }
        }
      }

      if (newChatCreated && realChatId) {
        await fetchChats(actualClientId);
        await fetchMessages(realChatId);
        if (chatTitle) {
          setChats(prev => prev.map(c => c.chat_id === realChatId ? { ...c, title: chatTitle } : c));
        }
      }
      setTempChatId(null);

    } catch (err) {
      console.error('Error sending message:', err);
      alert('Error sending message. Please try again.');
    } finally {
      setIsTyping(false);
    }
  };

  const handleSendFollowUp = async (chatId) => {
    if (!chatId || isTyping) return;
    setIsTyping(true);
    const tempAiMessageId = `followup-ai-${Date.now()}`;
    let streamedContent = '';

    try {
      const response = await fetch('/api/chats/send-message-stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          client_id: actualClientId,
          message: "Follow up with the user with a short message...",
          is_follow_up: true
        }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        buffer = buffer.replace(/}\s*{/g, '}\n{');
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmedLine = line.trim();
          if (!trimmedLine) continue;
          try {
            const jsonData = JSON.parse(trimmedLine);
            if (jsonData.type === 'content') {
              streamedContent += jsonData.data || '';
              setMessages(prev => {
                const updates = { ...prev };
                const currentMessages = prev[chatId] || [];
                const filteredMessages = currentMessages.filter(m => m.message_id !== tempAiMessageId);
                updates[chatId] = [...filteredMessages, {
                  message_id: tempAiMessageId,
                  content: streamedContent,
                  ai_generated: true,
                  role: 'assistant',
                  streaming: true,
                  isFollowUp: true,
                  created_at: new Date().toISOString()
                }];
                return updates;
              });
            }
          } catch (e) { }
        }
      }
    } catch (err) {
      console.error('Error sending follow-up:', err);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSaveTools = async () => {
    try {
      const response = await authFetch(`/api/clients/${actualClientId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tools, system_prompt: systemPrompt }),
      });

      if (response.ok) {
        const updatedClient = await response.json();
        setClient(updatedClient);
        setShowToolsModal(false);
        alert('Settings updated successfully');
      } else {
        throw new Error('Failed to update settings');
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleAddTool = () => {
    try {
      const parsedInputs = JSON.parse(newTool.inputs);
      const toolToAdd = { ...newTool, inputs: parsedInputs };
      setTools([...tools, toolToAdd]);
      setNewTool({
        name: '',
        description: '',
        url: '',
        method: 'GET',
        inputs: '{}',
        auth: 'none'
      });
    } catch (e) {
      alert('Invalid JSON for inputs');
    }
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
          <button onClick={() => navigate('/')} className="primary-btn">← Back Home</button>
        </div>
      </div>
    );
  }

  return (
    <div className="client-page">
      <div className="client-header">
        <div>
          <h1>{client?.company_name || 'Client'}</h1>
          <p className="client-url">{client?.website_url}</p>
        </div>
        <div className="header-actions">
          {isAdmin && (
            <>
              <button
                className="primary-btn"
                onClick={() => setShowToolsModal(true)}
              >
                Settings
              </button>
              <button
                onClick={() => navigate('/dashboard')}
                className="secondary-btn"
              >
                ← Back
              </button>
              <button
                onClick={() => {
                  if (window.confirm('Are you sure you want to logout?')) {
                    if (onLogout) onLogout();
                    navigate('/login');
                  }
                }}
                className="logout-btn"
              >
                Logout
              </button>
            </>
          )}
        </div>
      </div>

      <div className="compact-chat-wrapper">
        <CompactChat
          client={client}
          chats={chats}
          messages={messages}
          selectedChatId={selectedChatId}
          tempChatId={tempChatId}
          isTyping={isTyping}
          onSendMessage={handleSendMessage}
          onNewChat={handleNewChat}
          onSelectChat={handleSelectChat}
          onDeleteChat={handleDeleteChat}
          onHintClick={(hint) => handleSendMessage(hint)}
        />
      </div>

      {showToolsModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Client Settings</h2>
            <div className="system-prompt-section" style={{ marginBottom: '30px' }}>
              <h3>System Prompt</h3>
              <textarea
                value={systemPrompt}
                onChange={e => setSystemPrompt(e.target.value)}
                className="chat-input"
                style={{ minHeight: '150px', fontFamily: 'inherit', resize: 'vertical' }}
              />
            </div>

            <div className="tools-list">
              <h3>API Tools</h3>
              {tools.map((tool, index) => (
                <div key={index} className="tool-item">
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <strong>{tool.name}</strong>
                    <button onClick={() => setTools(tools.filter((_, i) => i !== index))} className="delete-btn">Remove</button>
                  </div>
                  <code>{tool.method} {tool.url}</code>
                </div>
              ))}
            </div>

            <div className="add-tool-form">
              <h3>Add New Tool</h3>
              <div style={{ display: 'grid', gap: '10px' }}>
                <input
                  placeholder="Name (e.g., get_weather)"
                  value={newTool.name}
                  onChange={e => setNewTool({ ...newTool, name: e.target.value })}
                  className="chat-input"
                />
                <input
                  placeholder="Description"
                  value={newTool.description}
                  onChange={e => setNewTool({ ...newTool, description: e.target.value })}
                  className="chat-input"
                />
                <div style={{ display: 'flex', gap: '10px' }}>
                  <select
                    value={newTool.method}
                    onChange={e => setNewTool({ ...newTool, method: e.target.value })}
                  >
                    <option value="GET">GET</option>
                    <option value="POST">POST</option>
                    <option value="PUT">PUT</option>
                    <option value="DELETE">DELETE</option>
                  </select>
                  <input
                    placeholder="URL Path (e.g., /api/weather)"
                    value={newTool.url}
                    onChange={e => setNewTool({ ...newTool, url: e.target.value })}
                    className="chat-input"
                    style={{ flex: 1 }}
                  />
                </div>
                <select
                  value={newTool.auth}
                  onChange={e => setNewTool({ ...newTool, auth: e.target.value })}
                >
                  <option value="none">No Auth</option>
                  <option value="bearer">Bearer Token</option>
                </select>
                <textarea
                  placeholder='Inputs JSON schema (e.g., {"query": {"city": {"type": "string"}}})'
                  value={newTool.inputs}
                  onChange={e => setNewTool({ ...newTool, inputs: e.target.value })}
                  className="chat-input"
                  style={{ minHeight: '100px', fontFamily: 'monospace' }}
                />
                <button onClick={handleAddTool} className="primary-btn">Add Tool</button>
              </div>
            </div>

            <div className="modal-actions">
              <button onClick={() => setShowToolsModal(false)} className="secondary-btn">Cancel</button>
              <button onClick={handleSaveTools} className="primary-btn">Save Changes</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ClientPage;