import React, { useState, useEffect } from 'react';
import { UserCheck, Play, CheckCircle, Lock, Inbox, AlertTriangle, RefreshCw } from 'lucide-react';
import { getEngineers, getTickets, updateTicketStatus, reassignTicket } from '../services/api';

export default function SupportPortal() {
  const [engineers, setEngineers] = useState([]);
  const [selectedAgentId, setSelectedAgentId] = useState('');
  const [assignedTickets, setAssignedTickets] = useState([]);
  const [eligibleQueue, setEligibleQueue] = useState([]);
  const [activeTab, setActiveTab] = useState('assigned');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchEngineers();
  }, []);

  useEffect(() => {
    if (selectedAgentId) {
      fetchTicketsForAgent();
    }
  }, [selectedAgentId]);

  const fetchEngineers = async () => {
    try {
      const res = await getEngineers();
      setEngineers(res.data);
      if (res.data.length > 0 && !selectedAgentId) {
        setSelectedAgentId(res.data[0].agent_id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const currentAgent = engineers.find(e => e.agent_id === selectedAgentId) || null;

  const fetchTicketsForAgent = async () => {
    if (!currentAgent) return;
    setLoading(true);
    try {
      const resAll = await getTickets();
      const all = resAll.data;

      // My Assigned Tickets
      const assigned = all.filter(t => t.assigned_agent_id === currentAgent.agent_id && t.status !== 'Closed');
      setAssignedTickets(assigned);

      // Eligible Queue: Tickets in 'New' status that this agent level is legally allowed to pick
      const level = currentAgent.level;
      let allowedPriorities = ['Low'];
      if (level === 'L2') allowedPriorities = ['Low', 'Medium'];
      if (level === 'L3') allowedPriorities = ['Low', 'Medium', 'High'];

      const queue = all.filter(t => t.status === 'New' && allowedPriorities.includes(t.resolved_priority));
      setEligibleQueue(queue);

    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (ticketId, newStatus) => {
    try {
      await updateTicketStatus(ticketId, {
        status: newStatus,
        actor: currentAgent ? `${currentAgent.name} (${currentAgent.agent_id})` : 'SupportAgent',
        notes: `Status updated to ${newStatus} via Support Portal.`
      });
      fetchTicketsForAgent();
      fetchEngineers();
    } catch (err) {
      alert('Failed to update status');
    }
  };

  const handlePickTicket = async (ticketId) => {
    if (!currentAgent) return;
    if (currentAgent.current_load >= currentAgent.max_capacity) {
      alert(`Capacity Limit Reached! ${currentAgent.name} is at maximum capacity (${currentAgent.max_capacity} tickets).`);
      return;
    }

    try {
      await reassignTicket(ticketId, currentAgent.agent_id, `Picked up from queue by ${currentAgent.name}`);
      fetchTicketsForAgent();
      fetchEngineers();
    } catch (err) {
      alert('Failed to pick ticket');
    }
  };

  return (
    <div style={{ maxWidth: '1300px', margin: '0 auto', padding: '24px 16px' }}>
      {/* Top Controls: Select Agent Profile */}
      <div className="glass-card" style={{ padding: '20px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: '6px' }}>SELECT ACTIVE ENGINEER PROFILE</label>
            <select
              className="form-control"
              style={{ width: '320px', fontWeight: 600 }}
              value={selectedAgentId}
              onChange={(e) => setSelectedAgentId(e.target.value)}
            >
              {engineers.map(e => (
                <option key={e.agent_id} value={e.agent_id}>
                  {e.name} ({e.agent_id}) — Level {e.level} [{e.current_load}/{e.max_capacity} Active]
                </option>
              ))}
            </select>
          </div>

          {currentAgent && (
            <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>LEVEL PERMISSIONS</span>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-secondary)' }}>
                  Level {currentAgent.level} ({currentAgent.level === 'L1' ? 'Low Only' : currentAgent.level === 'L2' ? 'Low & Medium' : 'High, Medium, Low'})
                </div>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>ACTIVE CAPACITY LOAD</span>
                <div style={{ fontSize: '1.1rem', fontWeight: 700, color: currentAgent.current_load >= currentAgent.max_capacity ? 'var(--accent-danger)' : 'var(--accent-success)' }}>
                  {currentAgent.current_load} / {currentAgent.max_capacity} Tickets
                </div>
              </div>
              <button onClick={() => { fetchTicketsForAgent(); fetchEngineers(); }} className="btn btn-secondary btn-sm">
                <RefreshCw size={14} /> Refresh
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
        <button
          onClick={() => setActiveTab('assigned')}
          className={`btn ${activeTab === 'assigned' ? 'btn-primary' : 'btn-secondary'}`}
        >
          <UserCheck size={16} /> My Assigned Tickets ({assignedTickets.length})
        </button>
        <button
          onClick={() => setActiveTab('queue')}
          className={`btn ${activeTab === 'queue' ? 'btn-primary' : 'btn-secondary'}`}
        >
          <Inbox size={16} /> Eligible Queue Pick-up ({eligibleQueue.length})
        </button>
      </div>

      {/* Assigned Tickets Tab */}
      {activeTab === 'assigned' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: '20px' }}>
          {assignedTickets.length === 0 && (
            <div className="glass-card" style={{ padding: '30px', gridColumn: '1 / -1', textAlign: 'center', color: 'var(--text-muted)' }}>
              No active assigned tickets for {currentAgent?.name}. Check the Eligible Queue tab to pick up unassigned tickets.
            </div>
          )}

          {assignedTickets.map(t => (
            <div key={t.ticket_id} className="glass-card glass-card-interactive" style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <span style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--accent-secondary)' }}>{t.ticket_id}</span>
                  <div style={{ display: 'flex', gap: '6px' }}>
                    <span className={`badge badge-${t.resolved_priority.toLowerCase()}`}>{t.resolved_priority}</span>
                    <span className={`badge badge-${t.status.toLowerCase().replace(' ', '')}`}>{t.status}</span>
                  </div>
                </div>

                <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '8px' }}>{t.subject}</h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '14px', lineHeight: '1.5' }}>
                  {t.description}
                </p>

                <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '14px' }}>
                  <div><strong>Customer:</strong> {t.customer_name} ({t.customer_email})</div>
                  <div><strong>Category:</strong> {t.resolved_category}</div>
                  <div><strong>Assignment Reason:</strong> {t.assignment_reason}</div>
                  {t.is_vague && <div style={{ color: 'var(--accent-warning)', marginTop: '4px' }}>⚠️ Flagged as Vague Ticket</div>}
                  {t.language !== 'en' && <div style={{ color: '#a5b4fc', marginTop: '2px' }}>🌐 Detected Language: {t.language.toUpperCase()}</div>}
                </div>
              </div>

              {/* Status Action Buttons */}
              <div style={{ display: 'flex', gap: '8px', paddingTop: '12px', borderTop: '1px solid var(--border-color)' }}>
                {t.status === 'Assigned' && (
                  <button onClick={() => handleStatusChange(t.ticket_id, 'In Progress')} className="btn btn-primary btn-sm" style={{ flex: 1 }}>
                    <Play size={14} /> Start Working
                  </button>
                )}
                {(t.status === 'Assigned' || t.status === 'In Progress') && (
                  <button onClick={() => handleStatusChange(t.ticket_id, 'Resolved')} className="btn btn-success btn-sm" style={{ flex: 1 }}>
                    <CheckCircle size={14} /> Resolve Ticket
                  </button>
                )}
                {t.status === 'Resolved' && (
                  <button onClick={() => handleStatusChange(t.ticket_id, 'Closed')} className="btn btn-secondary btn-sm" style={{ flex: 1 }}>
                    <Lock size={14} /> Close Ticket
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Eligible Queue Tab */}
      {activeTab === 'queue' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: '20px' }}>
          {eligibleQueue.length === 0 && (
            <div className="glass-card" style={{ padding: '30px', gridColumn: '1 / -1', textAlign: 'center', color: 'var(--text-muted)' }}>
              No queued unassigned tickets currently eligible for Level {currentAgent?.level}.
            </div>
          )}

          {eligibleQueue.map(t => (
            <div key={t.ticket_id} className="glass-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                  <span style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--accent-secondary)' }}>{t.ticket_id}</span>
                  <span className={`badge badge-${t.resolved_priority.toLowerCase()}`}>{t.resolved_priority} Priority</span>
                </div>

                <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '8px' }}>{t.subject}</h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '14px', lineHeight: '1.5' }}>
                  {t.description}
                </p>

                <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '14px' }}>
                  <div><strong>Required Level:</strong> Level {t.assigned_level}</div>
                  <div><strong>Category:</strong> {t.resolved_category}</div>
                </div>
              </div>

              <button
                onClick={() => handlePickTicket(t.ticket_id)}
                className="btn btn-primary btn-sm"
                style={{ width: '100%' }}
                disabled={currentAgent?.current_load >= currentAgent?.max_capacity}
              >
                <Inbox size={14} /> Pick Up Ticket
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
