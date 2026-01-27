import React, { useState, useEffect } from 'react';
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

  /* Tools Management logic */
  const [showToolsModal, setShowToolsModal] = useState(false);
  const [tools, setTools] = useState([]);
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
    // Optimistically add user message immediately
    const tempUserMessageId = `temp-${Date.now()}`;
    const userMessage = {
      message_id: tempUserMessageId,
      content: messageText,
      ai_generated: false,
      created_at: new Date().toISOString()
    };

    // If no chat selected, create a new one
    let currentChatId = selectedChatId;
    if (!currentChatId) {
      // We'll get the chat_id from the response
      currentChatId = null;
    }

    // Add user message optimistically (create temp chat state if needed)
    if (!currentChatId) {
      // Create a temporary chat state for the new chat
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
      const response = await fetch('/api/chats/send-message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: currentChatId && !currentChatId.startsWith('temp-') ? currentChatId : null,
          client_id: clientIp,
          message: messageText
        }),
      });

      if (response.ok) {
        const result = await response.json();

        // Update chat list if new chat was created
        if (result.chat_id && result.chat_id !== selectedChatId) {
          const newChat = {
            chat_id: result.chat_id,
            title: result.chat_title,
            created_at: new Date().toISOString()
          };
          setChats(prev => [newChat, ...prev]);
          setSelectedChatId(result.chat_id);
        }

        // Replace temp message with real messages or append to existing
        setMessages(prev => {
          const newMessages = { ...prev };

          // Get temp messages if we were using a temp chat
          let messagesToPreserve = [];
          if (currentChatId && currentChatId.startsWith('temp-')) {
            // We're creating a new chat, get messages from temp chat
            messagesToPreserve = newMessages[currentChatId] || [];
            // Remove temp chat ID
            delete newMessages[currentChatId];
          } else {
            // We're adding to existing chat, get existing messages
            messagesToPreserve = newMessages[result.chat_id] || [];
          }

          // Remove the temp user message if it exists
          const filteredMessages = messagesToPreserve.filter(m => m.message_id !== tempUserMessageId);

          // Add real messages (append, don't replace)
          return {
            ...newMessages,
            [result.chat_id]: [
              ...filteredMessages,
              result.user_message,
              result.ai_message
            ]
          };
        });

        // Clear temp chat ID
        setTempChatId(null);
      } else {
        // Remove temp message on error
        setMessages(prev => {
          const newMessages = { ...prev };
          // Remove temp chat IDs
          Object.keys(newMessages).forEach(id => {
            if (id.startsWith('temp-')) {
              delete newMessages[id];
            }
          });
          // Remove temp message from real chat if it exists
          if (currentChatId && !currentChatId.startsWith('temp-')) {
            newMessages[currentChatId] = (newMessages[currentChatId] || []).filter(m => m.message_id !== tempUserMessageId);
          }
          return newMessages;
        });
        const error = await response.json();
        throw new Error(error.detail || 'Unknown error');
      }
    } catch (err) {
      console.error('Error sending message:', err);
      alert(`Error sending message: ${err.message}`);
      // Remove temp message on error
      setMessages(prev => {
        const newMessages = { ...prev };
        // Remove temp chat IDs
        Object.keys(newMessages).forEach(id => {
          if (id.startsWith('temp-')) {
            delete newMessages[id];
          }
        });
        // Remove temp message from real chat if it exists
        if (currentChatId && !currentChatId.startsWith('temp-')) {
          newMessages[currentChatId] = (newMessages[currentChatId] || []).filter(m => m.message_id !== tempUserMessageId);
        }
        return newMessages;
      });
      throw err;
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
        body: JSON.stringify({ tools }),
      });

      if (response.ok) {
        const updatedClient = await response.json();
        setClient(updatedClient);
        setShowToolsModal(false);
        alert('Tools updated successfully');
      } else {
        throw new Error('Failed to update tools');
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
            Manage Tools
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
          onSelectChat={setSelectedChatId}
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
            <h2>Manage Tools</h2>

            <div className="tools-list">
              <h3>Current Tools</h3>
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
