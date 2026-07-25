import React, { useState, useEffect } from 'react';
import { Send, Search, CheckCircle2, AlertCircle, Clock, RotateCcw, FileText } from 'lucide-react';
import { createTicket, getTickets, getTicketById, updateTicketStatus } from '../services/api';

export default function CustomerPortal() {
  const [activeTab, setActiveTab] = useState('create');
  
  // Form State
  const [formData, setFormData] = useState({
    external_ref: 'web-' + Math.random().toString(36).substring(2, 8),
    customer_id: 'CUST-2041',
    customer_name: 'Anita Sharma',
    customer_email: 'anita.sharma@example.com',
    subject: 'Charged twice for one order',
    description: 'My payment was deducted twice for order #4471 on July 19th. Please refund the duplicate $149.99 charge immediately as my bank account is now overdrawn.',
    category: 'Billing',
    priority: 'High',
    channel: 'web_app'
  });

  const [submissionResult, setSubmissionResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Status Search State
  const [searchId, setSearchId] = useState('');
  const [searchedTicket, setSearchedTicket] = useState(null);
  const [recentTickets, setRecentTickets] = useState([]);

  useEffect(() => {
    fetchRecentTickets();
  }, []);

  const fetchRecentTickets = async () => {
    try {
      const res = await getTickets();
      setRecentTickets(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    setSubmissionResult(null);

    const payload = {
      external_ref: formData.external_ref,
      customer: {
        customer_id: formData.customer_id,
        name: formData.customer_name,
        email: formData.customer_email
      },
      subject: formData.subject,
      description: formData.description,
      category: formData.category,
      priority: formData.priority,
      channel: formData.channel,
      metadata: {
        submitted_via: 'Customer Portal UI'
      }
    };

    try {
      const res = await createTicket(payload);
      setSubmissionResult(res.data);
      fetchRecentTickets();
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to submit ticket');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchId.trim()) return;
    try {
      const res = await getTicketById(searchId.trim());
      setSearchedTicket(res.data);
    } catch (err) {
      alert('Ticket not found!');
      setSearchedTicket(null);
    }
  };

  const handleReopen = async (ticketId) => {
    try {
      await updateTicketStatus(ticketId, {
        status: 'In Progress',
        actor: 'Customer',
        notes: 'Customer re-opened ticket: Issue still persists.'
      });
      alert(`Ticket ${ticketId} has been re-opened!`);
      fetchRecentTickets();
      if (searchedTicket && searchedTicket.ticket_id === ticketId) {
        setSearchedTicket({ ...searchedTicket, status: 'In Progress' });
      }
    } catch (err) {
      alert('Failed to re-open ticket');
    }
  };

  const fillSample = (type) => {
    if (type === 'billing') {
      setFormData({
        external_ref: 'web-' + Math.random().toString(36).substring(2, 8),
        customer_id: 'CUST-2041',
        customer_name: 'Anita Sharma',
        customer_email: 'anita.sharma@example.com',
        subject: 'Charged twice for one order',
        description: 'My payment was deducted twice for order #4471 on July 19th. Please refund the duplicate $149.99 charge immediately as my bank account is now overdrawn.',
        category: 'Billing',
        priority: 'High',
        channel: 'web_app'
      });
    } else if (type === 'trap_outage') {
      // Priority trap: marked low by customer, text indicates severe outage
      setFormData({
        external_ref: 'web-' + Math.random().toString(36).substring(2, 8),
        customer_id: 'CUST-3092',
        customer_name: 'Marcus Vance',
        customer_email: 'marcus.v@company.com',
        subject: 'CRITICAL: Database outage in production',
        description: 'Entire database cluster connection is timing out with 500 errors across all customer instances! Urgent assistance required!',
        category: 'Technical',
        priority: 'Low', // Customer mistakenly typed Low
        channel: 'web_app'
      });
    } else if (type === 'vague') {
      setFormData({
        external_ref: 'web-' + Math.random().toString(36).substring(2, 8),
        customer_id: 'CUST-8812',
        customer_name: 'Tom Holland',
        customer_email: 'tom@example.com',
        subject: 'System issue',
        description: 'It broke.',
        category: 'General',
        priority: 'Low',
        channel: 'web_app'
      });
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px 16px' }}>
      {/* Tab Navigation */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
        <button
          onClick={() => setActiveTab('create')}
          className={`btn ${activeTab === 'create' ? 'btn-primary' : 'btn-secondary'}`}
        >
          <Send size={16} /> Raise a Ticket
        </button>
        <button
          onClick={() => setActiveTab('status')}
          className={`btn ${activeTab === 'status' ? 'btn-primary' : 'btn-secondary'}`}
        >
          <Search size={16} /> Ticket Status & History
        </button>
      </div>

      {activeTab === 'create' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
          {/* Ticket Form */}
          <div className="glass-card" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Submit Support Request</h2>
              <div style={{ display: 'flex', gap: '6px' }}>
                <button type="button" onClick={() => fillSample('billing')} className="btn btn-secondary btn-sm">Sample Billing</button>
                <button type="button" onClick={() => fillSample('trap_outage')} className="btn btn-secondary btn-sm">Prio Trap</button>
                <button type="button" onClick={() => fillSample('vague')} className="btn btn-secondary btn-sm">Vague</button>
              </div>
            </div>

            <form onSubmit={handleSubmit}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div className="form-group">
                  <label>Customer ID</label>
                  <input
                    type="text"
                    className="form-control"
                    value={formData.customer_id}
                    onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Customer Name</label>
                  <input
                    type="text"
                    className="form-control"
                    value={formData.customer_name}
                    onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Customer Email</label>
                <input
                  type="email"
                  className="form-control"
                  value={formData.customer_email}
                  onChange={(e) => setFormData({ ...formData, customer_email: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Subject</label>
                <input
                  type="text"
                  className="form-control"
                  value={formData.subject}
                  onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  className="form-control"
                  rows={4}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  required
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div className="form-group">
                  <label>Category (Optional)</label>
                  <select
                    className="form-control"
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  >
                    <option value="Billing">Billing</option>
                    <option value="Technical">Technical</option>
                    <option value="Account">Account</option>
                    <option value="UI/UX">UI/UX</option>
                    <option value="Feature Request">Feature Request</option>
                    <option value="">Leave Empty (AI Infer)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Claimed Priority (Optional)</label>
                  <select
                    className="form-control"
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  >
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                    <option value="">Leave Empty (AI Infer)</option>
                  </select>
                </div>
              </div>

              <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '12px' }} disabled={loading}>
                {loading ? 'Processing via Automation Engine...' : 'Submit Ticket'}
              </button>
            </form>
          </div>

          {/* Submission Output & AI Verification Preview */}
          <div>
            {submissionResult && (
              <div className="glass-card" style={{ padding: '24px', borderColor: 'var(--accent-success)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--accent-success)', marginBottom: '16px' }}>
                  <CheckCircle2 size={24} />
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Ticket Successfully Ingested</h3>
                </div>

                <div style={{ background: 'rgba(10, 13, 20, 0.7)', padding: '16px', borderRadius: '8px', marginBottom: '16px' }}>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>HTTP 201 Response Output:</p>
                  <pre style={{ color: '#a5b4fc', fontSize: '0.85rem', marginTop: '8px', overflowX: 'auto' }}>
                    {JSON.stringify(submissionResult, null, 2)}
                  </pre>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '0.9rem' }}>
                  {submissionResult.is_duplicate && (
                    <div style={{ color: 'var(--accent-warning)', fontWeight: 700 }}>
                      Duplicate ticket detected{submissionResult.duplicate_of ? ` against ${submissionResult.duplicate_of}` : ''}. No new assignment was created.
                    </div>
                  )}
                  <div><strong>Generated Ticket ID:</strong> <span style={{ color: 'var(--accent-secondary)', fontWeight: 700 }}>{submissionResult.ticket_id}</span></div>
                  <div><strong>AI Verified Priority:</strong> <span className={`badge badge-${submissionResult.resolved_priority.toLowerCase()}`}>{submissionResult.resolved_priority}</span></div>
                  <div><strong>Routed Level:</strong> <span style={{ color: '#a5b4fc', fontWeight: 600 }}>{submissionResult.assigned_level}</span></div>
                  <div><strong>Assigned Agent ID:</strong> <span style={{ color: '#67e8f9', fontWeight: 600 }}>{submissionResult.assigned_agent_id || 'Queued'}</span></div>
                  <div><strong>Confirmation Email:</strong> <span style={{ color: 'var(--accent-success)' }}>Logged in Persistent Email DB</span></div>
                </div>
              </div>
            )}

            {!submissionResult && (
              <div className="glass-card" style={{ padding: '24px', opacity: 0.85 }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '12px' }}>SwiftDesk Pipeline Ingestion Flow</h3>
                <ol style={{ paddingLeft: '20px', color: 'var(--text-muted)', lineHeight: '1.8', fontSize: '0.875rem' }}>
                  <li>Payload received at <code style={{ color: '#a5b4fc' }}>POST /api/tickets</code></li>
                  <li>Schema validation & requirement enforcement</li>
                  <li>Hybrid AI Classification & Untrusted Priority verification</li>
                  <li>Duplicate ticket & vagueness detection</li>
                  <li>L1 / L2 / L3 routing rule evaluation</li>
                  <li>Active capacity load balancing</li>
                  <li>Audit Trail event logged</li>
                  <li>Customer & Engineer confirmation emails generated</li>
                </ol>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'status' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Search Box */}
          <div className="glass-card" style={{ padding: '20px' }}>
            <form onSubmit={handleSearch} style={{ display: 'flex', gap: '12px' }}>
              <input
                type="text"
                className="form-control"
                placeholder="Enter Ticket ID (e.g. TKT-100001)..."
                value={searchId}
                onChange={(e) => setSearchId(e.target.value)}
              />
              <button type="submit" className="btn btn-primary"><Search size={16} /> Search</button>
            </form>
          </div>

          {/* Search Result Ticket Card */}
          {searchedTicket && (
            <div className="glass-card" style={{ padding: '24px', borderLeft: '4px solid var(--accent-primary)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <div>
                  <span style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-secondary)' }}>{searchedTicket.ticket_id}</span>
                  <h3 style={{ fontSize: '1.1rem', marginTop: '4px' }}>{searchedTicket.subject}</h3>
                </div>
                <span className={`badge badge-${searchedTicket.status.toLowerCase().replace(' ', '')}`}>{searchedTicket.status}</span>
              </div>

              <p style={{ color: 'var(--text-muted)', marginBottom: '16px' }}>{searchedTicket.description}</p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', background: 'rgba(10, 13, 20, 0.5)', padding: '12px', borderRadius: '8px', fontSize: '0.85rem' }}>
                <div><span style={{ color: 'var(--text-dim)' }}>Priority:</span> {searchedTicket.resolved_priority}</div>
                <div><span style={{ color: 'var(--text-dim)' }}>Category:</span> {searchedTicket.resolved_category}</div>
                <div><span style={{ color: 'var(--text-dim)' }}>Level:</span> {searchedTicket.assigned_level}</div>
                <div><span style={{ color: 'var(--text-dim)' }}>Agent:</span> {searchedTicket.assigned_agent_name || 'Queued'}</div>
              </div>

              {/* Status Timeline */}
              <div style={{ marginTop: '20px' }}>
                <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '10px' }}>STATUS LIFECYCLE TIMELINE</h4>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  {['New', 'Assigned', 'In Progress', 'Resolved', 'Closed'].map((step, idx) => {
                    const isDone = ['New', 'Assigned', 'In Progress', 'Resolved', 'Closed'].indexOf(searchedTicket.status) >= idx;
                    return (
                      <div key={step} style={{ flex: 1, textAlign: 'center' }}>
                        <div style={{
                          height: '6px',
                          borderRadius: '3px',
                          background: isDone ? 'linear-gradient(90deg, #6366f1, #10b981)' : 'rgba(255,255,255,0.1)',
                          marginBottom: '6px'
                        }} />
                        <span style={{ fontSize: '0.75rem', color: isDone ? 'var(--text-main)' : 'var(--text-dim)' }}>{step}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {(searchedTicket.status === 'Resolved' || searchedTicket.status === 'Closed') && (
                <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end' }}>
                  <button onClick={() => handleReopen(searchedTicket.ticket_id)} className="btn btn-warning btn-sm">
                    <RotateCcw size={14} /> Re-open Ticket
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Ticket History Table */}
          <div className="glass-card" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '16px' }}>All Submitted Tickets</h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '10px' }}>Ticket ID</th>
                    <th style={{ padding: '10px' }}>Subject</th>
                    <th style={{ padding: '10px' }}>Category</th>
                    <th style={{ padding: '10px' }}>Priority</th>
                    <th style={{ padding: '10px' }}>Status</th>
                    <th style={{ padding: '10px' }}>Assigned Agent</th>
                  </tr>
                </thead>
                <tbody>
                  {recentTickets.map(t => (
                    <tr key={t.ticket_id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '10px', color: 'var(--accent-secondary)', fontWeight: 600 }}>{t.ticket_id}</td>
                      <td style={{ padding: '10px' }}>{t.subject}</td>
                      <td style={{ padding: '10px' }}>{t.resolved_category}</td>
                      <td style={{ padding: '10px' }}><span className={`badge badge-${t.resolved_priority.toLowerCase()}`}>{t.resolved_priority}</span></td>
                      <td style={{ padding: '10px' }}><span className={`badge badge-${t.status.toLowerCase().replace(' ', '')}`}>{t.status}</span></td>
                      <td style={{ padding: '10px', color: 'var(--text-muted)' }}>{t.assigned_agent_name || 'Queued'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
