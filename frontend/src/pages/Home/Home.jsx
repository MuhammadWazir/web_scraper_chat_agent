import React, { useState, useEffect, useRef } from 'react';
import ClientForm from '../../components/ClientForm/ClientForm';
import ClientCard from '../../components/ClientCard/ClientCard';
import './Home.css';

function Home() {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    fetchClients();
    connectWebSocket();

    return () => {
      // Cleanup WebSocket on unmount
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === 'client_update') {
          setClients(prevClients => 
            prevClients.map(client => 
              client.client_id === message.data.client_id ? message.data : client
            )
          );
        }
      } catch (error) {}
    };

    ws.onclose = () => {
      setTimeout(connectWebSocket, 3000);
    };

    wsRef.current = ws;
  };

  const fetchClients = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/clients');
      const data = await response.json();
      setClients(data);
    } catch (error) {
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-container">
      <header className="home-header">
        <div>
          <h1>Voice Agent Dashboard</h1>
          <p>Manage your AI voice agents</p>
        </div>
      </header>

      <div className="home-content">
        <ClientForm onClientCreated={fetchClients} />

        <section className="clients-section">
          <h2>All Clients</h2>
          
          {loading ? (
            <div className="loading">
              <div className="spinner"></div>
              <p>Loading clients...</p>
            </div>
          ) : clients.length === 0 ? (
            <div className="empty-state">
              <p>No clients yet. Create your first client!</p>
            </div>
          ) : (
            <div className="clients-grid">
              {clients.map((client) => (
                <ClientCard key={client.client_id} client={client} />
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default Home;

