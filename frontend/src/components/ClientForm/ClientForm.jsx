import React, { useState } from 'react';
import ApiKeyModal from '../ApiKeyModal/ApiKeyModal';
import './ClientForm.css';

function ClientForm({ onClientCreated }) {
  const [creating, setCreating] = useState(false);
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [formData, setFormData] = useState({
    website_url: '',
    company_name: ''
  });

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.website_url || !formData.company_name) {
      return;
    }

    try {
      setCreating(true);

      const response = await fetch('/api/create-client', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const result = await response.json();

        if (result.api_key) {
          setApiKey(result.api_key);
          setShowApiKeyModal(true);
        }

        setFormData({ website_url: '', company_name: '' });
        if (onClientCreated) onClientCreated();
      } else {
        const error = await response.json();
        alert(`Error creating client: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error creating client:', error);
      alert('Error creating client. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  const handleCloseModal = () => {
    setShowApiKeyModal(false);
    setApiKey('');
  };

  return (
    <>
      <section className="client-form-section">
        <h2>Create New Client</h2>
        <form onSubmit={handleSubmit} className="client-form">
          <div className="form-group">
            <label htmlFor="company_name">Company Name</label>
            <input
              type="text"
              id="company_name"
              name="company_name"
              value={formData.company_name}
              onChange={handleInputChange}
              placeholder="Enter company name"
              disabled={creating}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="website_url">Website URL</label>
            <input
              type="url"
              id="website_url"
              name="website_url"
              value={formData.website_url}
              onChange={handleInputChange}
              placeholder="https://example.com"
              disabled={creating}
              required
            />
          </div>

          <button type="submit" className="submit-btn" disabled={creating}>
            {creating ? (
              <>
                <span className="spinner"></span>
                Creating Client...
              </>
            ) : (
              'Create Client'
            )}
          </button>
        </form>
      </section>

      {showApiKeyModal && (
        <ApiKeyModal apiKey={apiKey} onClose={handleCloseModal} />
      )}
    </>
  );
}

export default ClientForm;
