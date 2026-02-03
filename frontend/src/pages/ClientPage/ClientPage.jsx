import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ChatSidebar from '../../components/ChatSidebar/ChatSidebar';
import ChatMessages from '../../components/ChatMessages/ChatMessages';
import MessageInput from '../../components/MessageInput/MessageInput';
import './ClientPage.css';

function ClientPage() {
  const { clientIp } = useParams();
  const navigate = useNavigate();
  const [client, setClient] = useState(null);
  const [chats, setChats] = useState([]);
  const [messages, setMessages] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [tempChatId, setTempChatId] = useState(null);

  // Use ref to track the latest message state without triggering re-renders
  const messagesRef = useRef(messages);
  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  /* Tools Management logic */
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

  useEffect(() => {
    if (client && client.tools) {
      setTools(client.tools);
    }
    if (client && client.system_prompt) {
      setSystemPrompt(client.system_prompt);
    }
  }, [client]);

  useEffect(() => {
    fetchClient();
    fetchChats();
  }, [clientIp]);

  useEffect(() => {
    if (selectedChatId) {
      fetchMessages(selectedChatId);
    }
  }, [selectedChatId]);

  const fetchClient = async () => {
    try {
      const response = await fetch(`/api/clients/${clientIp}`);
      if (!response.ok) {
        throw new Error('Client not found');
      }
      const data = await response.json();
      setClient(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchChats = async () => {
    try {
      const response = await fetch(`/api/clients/${clientIp}/chats`);
      if (response.ok) {
        const data = await response.json();
        setChats(data);
      }
    } catch (err) {
      console.error('Error fetching chats:', err);
    }
  };

  const handleNewChat = () => {
    setSelectedChatId(null);
    setTempChatId(null);
    setIsTyping(false);
  };

  const handleSelectChat = (chatId) => {
    setSelectedChatId(chatId);
    setIsTyping(false);
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
          setSelectedChatId(null);
          setMessages(prev => {
            const newMessages = { ...prev };
            delete newMessages[chatId];
            return newMessages;
          });
        }
      } else {
        const error = await response.json();
        alert(`Error deleting chat: ${error.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error deleting chat:', err);
      alert('Error deleting chat. Please try again.');
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
          client_id: clientIp,
          message: messageText
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let streamedContent = '';
      let currentStatusHint = null;
      let realChatId = currentChatId;
      let chatTitle = null;
      const tempAiMessageId = `temp-ai-${Date.now()}`;
      let buffer = '';
      let firstChunkReceived = false;

      // Inner helper to update messages state directly
      const updateStreamingUI = (content, hint) => {
        const chatKey = newChatCreated ? realChatId : currentChatId;

        setMessages(prev => {
          const updates = { ...prev };
          const currentMessages = prev[chatKey] || prev[currentChatId] || [];
          const filteredMessages = currentMessages.filter(m => m.message_id !== tempAiMessageId);

          const aiMessage = {
            message_id: tempAiMessageId,
            content: content,
            statusHint: hint,
            ai_generated: true,
            role: 'assistant',
            streaming: true,
            created_at: new Date().toISOString()
          };

          // Apply to active key
          updates[chatKey] = [...filteredMessages, aiMessage];

          // CRITICAL: If we just created a chat, also update the old temp key
          // because the UI state (selectedChatId) might not have re-rendered yet.
          if (newChatCreated && chatKey !== currentChatId) {
            updates[currentChatId] = [...filteredMessages, aiMessage];
          }

          return updates;
        });
      };

      // Process streaming response
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Fix fused JSONs if any
        buffer = buffer.replace(/}\s*{/g, '}\n{');
        const lines = buffer.split('\n');

        // Keep potential incomplete line in buffer
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
              // Initial update to move user message to new chat
              updateStreamingUI(streamedContent, currentStatusHint);

            } else if (jsonData.type === 'title_updated') {
              chatTitle = jsonData.title;

            } else if (jsonData.type === 'status_hint') {
              currentStatusHint = jsonData.message;
              updateStreamingUI(streamedContent, currentStatusHint);
              // Yield to allow React to render the hint before content arrives
              await new Promise(r => setTimeout(r, 0));

            } else if (jsonData.type === 'content') {
              currentStatusHint = null; // Clear hint when content starts
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

      // After streaming completes, fetch final messages and update chat list
      if (newChatCreated && realChatId) {
        await fetchChats();
        await fetchMessages(realChatId);
        setSelectedChatId(realChatId);

        if (chatTitle) {
          setChats(prev => prev.map(chat =>
            chat.chat_id === realChatId ? { ...chat, title: chatTitle } : chat
          ));
        }

        setMessages(prev => {
          const newMessages = { ...prev };
          delete newMessages[currentChatId];
          return newMessages;
        });
      }

      setTempChatId(null);

    } catch (err) {
      console.error('Error sending message:', err);
      alert('Error sending message. Please try again.');

      setMessages(prev => {
        const newMessages = { ...prev };
        const chatKey = currentChatId;
        if (newMessages[chatKey]) {
          newMessages[chatKey] = newMessages[chatKey].filter(m =>
            m.message_id !== tempUserMessageId && !m.message_id.startsWith('temp-ai-')
          );
        }
        return newMessages;
      });
    } finally {
      setIsTyping(false);
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
          <button onClick={() => navigate('/')} className="secondary-btn">
            ← Back to Home
          </button>
        </div>
      </div>
    );
  }

  // Show messages from selected chat, or from temp chat if we're creating a new one
  const displayChatId = selectedChatId || tempChatId;
  const currentMessages = displayChatId ? (messages[displayChatId] || []) : [];



  const handleSaveTools = async () => {
    try {
      const response = await fetch(`/api/clients/${clientIp}`, {
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

  const handleRemoveTool = (index) => {
    const newTools = [...tools];
    newTools.splice(index, 1);
    setTools(newTools);
  };

  return (
    <div className="client-page">
      <div className="client-header">
        <div>
          <h1>{client?.company_name || 'Client'}</h1>
          <p className="client-url">{client?.website_url}</p>
        </div>
        <div className="header-actions">
          <button
            onClick={() => setShowToolsModal(true)}
            className="primary-btn"
          >
            Settings
          </button>
          <button
            onClick={() => navigate('/')}
            className="secondary-btn"
          >
            ← Back
          </button>
        </div>
      </div>

      <div className="client-content">
        <ChatSidebar
          chats={chats}
          selectedChatId={selectedChatId}
          onSelectChat={handleSelectChat}
          onDeleteChat={handleDeleteChat}
          onNewChat={handleNewChat}
        />

        <div className="chat-main">
          <ChatMessages
            messages={currentMessages}
            isTyping={isTyping}
            isEmpty={!displayChatId && currentMessages.length === 0}
          />
          <MessageInput
            onSendMessage={handleSendMessage}
            disabled={false}
          />
        </div>
      </div>

      {showToolsModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Client Settings</h2>

            <div className="system-prompt-section" style={{ marginBottom: '30px' }}>
              <h3>System Prompt</h3>
              <p style={{ fontSize: '0.9em', color: '#888', marginBottom: '10px' }}>
                Define custom instructions for the AI assistant. This will be injected into every conversation.
              </p>
              <textarea
                placeholder="Enter system prompt instructions here... (e.g., You are a helpful customer service agent for XYZ company.)"
                value={systemPrompt}
                onChange={e => setSystemPrompt(e.target.value)}
                className="chat-input"
                style={{ minHeight: '150px', fontFamily: 'inherit', resize: 'vertical' }}
              />
            </div>

            <div className="tools-list">
              <h3>API Tools</h3>
              {tools.length === 0 && <p>No tools configured.</p>}
              {tools.map((tool, index) => (
                <div key={index} className="tool-item">
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <strong>{tool.name}</strong>
                    <button onClick={() => handleRemoveTool(index)} className="delete-btn">Remove</button>
                  </div>
                  <p>{tool.description}</p>
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