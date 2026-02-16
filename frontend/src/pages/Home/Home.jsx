import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ClientForm from '../../components/ClientForm/ClientForm';
import ClientCard from '../../components/ClientCard/ClientCard';
import { authFetch } from '../../utils/auth';
import './Home.css';

function Home({ onLogout }) {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      setLoading(true);
      const response = await authFetch('/api/clients');
      if (response.ok) {
        const data = await response.json();
        setClients(data);
      }
    } catch (error) {
      console.error('Error fetching clients:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClient = async (clientId, e) => {
    e.stopPropagation();

    if (!window.confirm('Are you sure you want to delete this client? This will also delete all associated data from Qdrant.')) {
      return;
    }

    try {
      const response = await authFetch(`/api/clients/${clientId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        // Remove client from state
        setClients(prev => prev.filter(client => client.client_id !== clientId));
        alert('Client deleted successfully');
      } else {
        const error = await response.json();
        alert(`Error deleting client: ${error.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error deleting client:', err);
      alert('Error deleting client. Please try again.');
    }
  };

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      onLogout();
      navigate('/login');
    }
  };

  return (
    <div className="home-container">
      <header className="home-header">
        <div>
          <h1>Web Scraper Chat Agent</h1>
          <p>Manage your AI chat agents</p>
        </div>
        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
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
                <ClientCard
                  key={client.client_id}
                  client={client}
                  onDelete={handleDeleteClient}
                />
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default Home;
