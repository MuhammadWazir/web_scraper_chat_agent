import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ChatSidebar from '../../components/ChatSidebar/ChatSidebar';
import ChatMessages from '../../components/ChatMessages/ChatMessages';
import MessageInput from '../../components/MessageInput/MessageInput';
import './ClientPage.css';

function ClientPage() {
  const { clientId } = useParams();
  const navigate = useNavigate();
  const [client, setClient] = useState(null);
  const [chats, setChats] = useState([]);
  const [messages, setMessages] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedChatId, setSelectedChatId] = useState(null);

  useEffect(() => {
    fetchClient();
    fetchChats();
  }, [clientId]);

  useEffect(() => {
    if (selectedChatId) {
      fetchMessages(selectedChatId);
    }
  }, [selectedChatId]);

  const fetchClient = async () => {
    try {
      const response = await fetch(`/api/clients/${clientId}`);
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
      const response = await fetch(`/api/clients/${clientId}/chats`);
      if (response.ok) {
        const data = await response.json();
        setChats(data);
        // Auto-select first chat if available
        if (data.length > 0 && !selectedChatId) {
          setSelectedChatId(data[0].chat_id);
        }
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
        setMessages(prev => ({ ...prev, [chatId]: data }));
      }
    } catch (err) {
      console.error('Error fetching messages:', err);
    }
  };

  const handleCreateChat = async (title) => {
    try {
      const response = await fetch('/api/chats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_id: clientId,
          title: title
        }),
      });

      if (response.ok) {
        const newChat = await response.json();
        setChats(prev => [newChat, ...prev]);
        setSelectedChatId(newChat.chat_id);
        return newChat;
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Unknown error');
      }
    } catch (err) {
      console.error('Error creating chat:', err);
      alert(`Error creating chat: ${err.message}`);
      throw err;
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
    if (!selectedChatId) {
      return;
    }

    try {
      const response = await fetch('/api/chats/send-message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: selectedChatId,
          message: messageText
        }),
      });

      if (response.ok) {
        // Refresh messages
        await fetchMessages(selectedChatId);
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Unknown error');
      }
    } catch (err) {
      console.error('Error sending message:', err);
      alert(`Error sending message: ${err.message}`);
      throw err;
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

  const currentMessages = selectedChatId ? (messages[selectedChatId] || []) : [];

  return (
    <div className="client-page">
      <div className="client-header">
        <div>
          <h1>{client?.company_name || 'Client'}</h1>
          <p className="client-url">{client?.website_url}</p>
        </div>
        <div className="header-actions">
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
          onCreateChat={handleCreateChat}
        />

        <div className="chat-main">
          {selectedChatId ? (
            <>
              <ChatMessages messages={currentMessages} />
              <MessageInput
                onSendMessage={handleSendMessage}
                disabled={!selectedChatId}
              />
            </>
          ) : (
            <div className="no-chat-selected">
              <p>Select a chat from the sidebar or create a new one to start chatting.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ClientPage;
