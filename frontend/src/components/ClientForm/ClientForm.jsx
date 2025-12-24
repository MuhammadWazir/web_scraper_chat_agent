import React, { useState } from 'react';
import './ClientForm.css';

function ClientForm({ onClientCreated }) {
  const [creating, setCreating] = useState(false);
  const [formData, setFormData] = useState({
    website_url: '',
    target_audience: '',
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
    
    if (!formData.website_url || !formData.target_audience || !formData.company_name) {
      return;
    }

    try {
      setCreating(true);
      
      const response = await fetch('/api/create-voice-agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const result = await response.json();
        setFormData({ website_url: '', target_audience: '', company_name: '' });
        if (onClientCreated) onClientCreated();
        
        window.location.href = `/client/${result.url}`;
      }
    } catch (error) {
      console.error('Error creating client:', error);
    } finally {
      setCreating(false);
    }
  };

  return (
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
          />
        </div>

        <div className="form-group">
          <label htmlFor="target_audience">Target Audience</label>
          <input
            type="text"
            id="target_audience"
            name="target_audience"
            value={formData.target_audience}
            onChange={handleInputChange}
            placeholder="e.g., businesses, consumers, developers"
            disabled={creating}
          />
        </div>

        <button type="submit" className="submit-btn" disabled={creating}>
          {creating ? (
            <>
              <span className="spinner"></span>
              Creating Agent...
            </>
          ) : (
            'Create Client'
          )}
        </button>
      </form>
    </section>
  );
}

export default ClientForm;

