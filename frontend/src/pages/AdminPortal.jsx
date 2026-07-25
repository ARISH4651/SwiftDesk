import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend
} from 'recharts';
import { 
  Shield, Activity, Users, AlertTriangle, Mail, History, RefreshCw, Zap, UserPlus, Filter, Search 
} from 'lucide-react';
import { 
  getDashboardStats, getTickets, getEngineers, reassignTicket, 
  getAuditLogs, getEmailLogs, triggerSLA, triggerEODSummary, ingestSampleBatch, updateEngineerAvailability 
} from '../services/api';

const COLORS = ['#6366f1', '#06b6d4', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6'];

export default function AdminPortal() {
  const [stats, setStats] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [engineers, setEngineers] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [emailLogs, setEmailLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('tickets');
  const [loading, setLoading] = useState(false);

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');

  // Reassign Modal State
  const [reassignModal, setReassignModal] = useState({ open: false, ticketId: null, targetAgent: '' });

  useEffect(() => {
    loadAllData();
  }, []);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [resStats, resTickets, resEngs, resAudit, resEmail] = await Promise.all([
        getDashboardStats(),
        getTickets(),
        getEngineers(),
        getAuditLogs(),
        getEmailLogs()
      ]);
      setStats(resStats.data);
      setTickets(resTickets.data);
      setEngineers(resEngs.data);
      setAuditLogs(resAudit.data);
      setEmailLogs(resEmail.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunBatchIngest = async () => {
    setLoading(true);
    try {
      const res = await ingestSampleBatch();
      alert(`Batch Ingested Successfully! ${res.data.ingested_count} tickets ingested across all edge cases.`);
      loadAllData();
    } catch (err) {
      alert('Batch Ingestion Failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRunSLACheck = async () => {
    try {
      await triggerSLA();
      alert('SLA Monitoring Engine Executed!');
      loadAllData();
    } catch (err) {
      alert('SLA check failed');
    }
  };

  const handleSendEODSummary = async () => {
    try {
      await triggerEODSummary();
      alert('Daily Admin Summary Email Triggered & Logged!');
      loadAllData();
    } catch (err) {
      alert('EOD summary failed');
    }
  };

  const handleToggleEngineerAvailability = async (agentId, currentStatus) => {
    try {
      await updateEngineerAvailability(agentId, !currentStatus);
      loadAllData();
    } catch (err) {
      alert('Failed to update availability');
    }
  };

  const handleExecuteReassign = async () => {
    if (!reassignModal.targetAgent) {
      alert('Please select an agent');
      return;
    }
    try {
      await reassignTicket(reassignModal.ticketId, reassignModal.targetAgent, 'Manual Admin Reassignment');
      alert(`Ticket ${reassignModal.ticketId} reassigned!`);
      setReassignModal({ open: false, ticketId: null, targetAgent: '' });
      loadAllData();
    } catch (err) {
      alert('Reassignment failed');
    }
  };

  // Filtered Tickets
  const filteredTickets = tickets.filter(t => {
    const matchesSearch = t.ticket_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          t.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          t.customer_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter ? t.status === statusFilter : true;
    const matchesPriority = priorityFilter ? t.resolved_priority === priorityFilter : true;
    return matchesSearch && matchesStatus && matchesPriority;
  });

  // Chart Data Formatting
  const statusChartData = stats ? Object.entries(stats.status_counts).map(([name, value]) => ({ name, value })) : [];
  const priorityChartData = stats ? Object.entries(stats.priority_counts).map(([name, value]) => ({ name, value })) : [];
  const categoryChartData = stats ? Object.entries(stats.category_counts).map(([name, value]) => ({ name, value })) : [];
  const reassignTicketDetails = reassignModal.ticketId ? tickets.find(t => t.ticket_id === reassignModal.ticketId) : null;

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '24px 16px' }}>
      {/* Action Bar Header */}
      <div className="glass-card" style={{ padding: '16px 24px', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Shield size={24} color="var(--accent-success)" />
          <div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 800 }}>Admin Operations Center</h2>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Real-time Analytics, L1/L2/L3 Routing Control & SLA Monitoring</p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button onClick={handleRunBatchIngest} className="btn btn-primary btn-sm" disabled={loading}>
            <Zap size={14} /> Ingest 15 Test Tickets (Batch)
          </button>
          <button onClick={handleRunSLACheck} className="btn btn-secondary btn-sm">
            <Activity size={14} /> Run SLA Check Engine
          </button>
          <button onClick={handleSendEODSummary} className="btn btn-secondary btn-sm">
            <Mail size={14} /> Trigger EOD Summary Email
          </button>
          <button onClick={loadAllData} className="btn btn-secondary btn-sm">
            <RefreshCw size={14} /> Refresh
          </button>
        </div>
      </div>

      {/* Metrics Cards Grid */}
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <div className="glass-card" style={{ padding: '20px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>TOTAL INGESTED</span>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '4px', color: '#fff' }}>{stats.total_tickets}</div>
          </div>
          <div className="glass-card" style={{ padding: '20px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>OPEN TICKETS</span>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '4px', color: 'var(--accent-secondary)' }}>{stats.open_tickets}</div>
          </div>
          <div className="glass-card" style={{ padding: '20px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>RESOLVED / CLOSED</span>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '4px', color: 'var(--accent-success)' }}>{stats.resolved_tickets}</div>
          </div>
          <div className="glass-card" style={{ padding: '20px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>SLA BREACHES</span>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '4px', color: stats.sla_breaches > 0 ? 'var(--accent-danger)' : 'var(--text-muted)' }}>{stats.sla_breaches}</div>
          </div>
          <div className="glass-card" style={{ padding: '20px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>LEVEL ESCALATIONS</span>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '4px', color: 'var(--accent-warning)' }}>{stats.escalations}</div>
          </div>
          <div className="glass-card" style={{ padding: '20px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>AVG RESOLUTION TIME</span>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, marginTop: '4px', color: '#a5b4fc' }}>{stats.avg_resolution_hours}h</div>
          </div>
        </div>
      )}

      {/* Visual Analytics Charts Section */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginBottom: '24px' }}>
        {/* Status Distribution */}
        <div className="glass-card" style={{ padding: '20px', height: '300px' }}>
          <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '10px' }}>Tickets by Status</h3>
          <ResponsiveContainer width="100%" height="80%">
            <PieChart>
              <Pie data={statusChartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label>
                {statusChartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Priority Breakdown */}
        <div className="glass-card" style={{ padding: '20px', height: '300px' }}>
          <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '10px' }}>Tickets by Priority</h3>
          <ResponsiveContainer width="100%" height="80%">
            <BarChart data={priorityChartData}>
              <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip />
              <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Category Distribution */}
        <div className="glass-card" style={{ padding: '20px', height: '300px' }}>
          <h3 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '10px' }}>Tickets by Category</h3>
          <ResponsiveContainer width="100%" height="80%">
            <BarChart data={categoryChartData}>
              <XAxis dataKey="name" stroke="#9ca3af" fontSize={10} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip />
              <Bar dataKey="value" fill="#06b6d4" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Engineer Roster & Workload Control Card */}
      <div className="glass-card" style={{ padding: '20px', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px' }}>Engineer Roster & Load Balancing Control</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '14px' }}>
          {engineers.map(e => (
            <div key={e.agent_id} style={{ background: 'rgba(10, 13, 20, 0.6)', padding: '14px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 700 }}>{e.name} ({e.agent_id})</span>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--accent-secondary)' }}>Level {e.level}</span>
              </div>
              
              <div style={{ marginTop: '8px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Workload: <strong>{e.current_load} / {e.max_capacity}</strong> tickets
                <div style={{ width: '100%', background: 'rgba(255,255,255,0.1)', height: '6px', borderRadius: '3px', marginTop: '4px' }}>
                  <div style={{ width: `${(e.current_load / e.max_capacity) * 100}%`, background: e.current_load >= e.max_capacity ? '#ef4444' : '#10b981', height: '100%', borderRadius: '3px' }} />
                </div>
              </div>

              <div style={{ marginTop: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: e.is_available ? 'var(--accent-success)' : 'var(--accent-danger)' }}>
                  {e.is_available ? '● Available' : '○ Unavailable'}
                </span>
                <button
                  onClick={() => handleToggleEngineerAvailability(e.agent_id, e.is_available)}
                  className={`btn btn-sm ${e.is_available ? 'btn-secondary' : 'btn-primary'}`}
                >
                  Toggle Availability
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tabs for Ticket Table, Audit Trail, Email Logs */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
        <button
          onClick={() => setActiveTab('tickets')}
          className={`btn ${activeTab === 'tickets' ? 'btn-primary' : 'btn-secondary'}`}
        >
          <Filter size={16} /> Master Ticket Table ({filteredTickets.length})
        </button>
        <button
          onClick={() => setActiveTab('emails')}
          className={`btn ${activeTab === 'emails' ? 'btn-primary' : 'btn-secondary'}`}
        >
          <Mail size={16} /> Live Email Logs ({emailLogs.length})
        </button>
        <button
          onClick={() => setActiveTab('audit')}
          className={`btn ${activeTab === 'audit' ? 'btn-primary' : 'btn-secondary'}`}
        >
          <History size={16} /> Audit Trail ({auditLogs.length})
        </button>
      </div>

      {/* Master Ticket Table Tab */}
      {activeTab === 'tickets' && (
        <div className="glass-card" style={{ padding: '24px' }}>
          {/* Filters */}
          <div style={{ display: 'flex', gap: '12px', marginBottom: '20px', flexWrap: 'wrap' }}>
            <div style={{ flex: 1, minWidth: '240px' }}>
              <input
                type="text"
                className="form-control"
                placeholder="Search ticket ID, subject, customer..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <select className="form-control" style={{ width: '160px' }} value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">All Statuses</option>
              <option value="New">New</option>
              <option value="Assigned">Assigned</option>
              <option value="In Progress">In Progress</option>
              <option value="Resolved">Resolved</option>
              <option value="Closed">Closed</option>
            </select>
            <select className="form-control" style={{ width: '160px' }} value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
              <option value="">All Priorities</option>
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
            </select>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '10px' }}>ID</th>
                  <th style={{ padding: '10px' }}>Customer</th>
                  <th style={{ padding: '10px' }}>Subject</th>
                  <th style={{ padding: '10px' }}>Verified Prio</th>
                  <th style={{ padding: '10px' }}>Category</th>
                  <th style={{ padding: '10px' }}>Target Level</th>
                  <th style={{ padding: '10px' }}>Assigned Agent</th>
                  <th style={{ padding: '10px' }}>Status</th>
                  <th style={{ padding: '10px' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredTickets.map(t => (
                  <tr key={t.ticket_id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '10px', color: 'var(--accent-secondary)', fontWeight: 700 }}>{t.ticket_id}</td>
                    <td style={{ padding: '10px' }}>{t.customer_name}</td>
                    <td style={{ padding: '10px' }}>{t.subject}</td>
                    <td style={{ padding: '10px' }}>
                      <span className={`badge badge-${t.resolved_priority.toLowerCase()}`}>{t.resolved_priority}</span>
                    </td>
                    <td style={{ padding: '10px' }}>{t.resolved_category}</td>
                    <td style={{ padding: '10px', fontWeight: 600 }}>{t.assigned_level}</td>
                    <td style={{ padding: '10px' }}>{t.assigned_agent_name || 'Queued'}</td>
                    <td style={{ padding: '10px' }}>
                      <span className={`badge badge-${t.status.toLowerCase().replace(' ', '')}`}>{t.status}</span>
                    </td>
                    <td style={{ padding: '10px' }}>
                      <button
                        onClick={() => setReassignModal({ open: true, ticketId: t.ticket_id, targetAgent: '' })}
                        className="btn btn-secondary btn-sm"
                      >
                        <UserPlus size={12} /> Reassign
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Live Email Logs Tab */}
      {activeTab === 'emails' && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px' }}>Persistent Mock Email Logs</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {emailLogs.map(em => (
              <div key={em.id} style={{ background: 'rgba(10, 13, 20, 0.6)', padding: '16px', borderRadius: '8px', borderLeft: '4px solid #6366f1' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.85rem' }}>
                  <div>
                    <span style={{ fontWeight: 700, color: '#a5b4fc' }}>TO:</span> {em.recipient_name} ({em.recipient_email}) &nbsp;|&nbsp;
                    <span style={{ fontWeight: 700, color: '#67e8f9' }}> ROLE:</span> {em.recipient_role}
                  </div>
                  <div style={{ color: 'var(--text-dim)' }}>{new Date(em.sent_at).toLocaleString()}</div>
                </div>
                <div style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '6px' }}>{em.subject}</div>
                <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', color: 'var(--text-muted)', fontSize: '0.825rem', background: 'rgba(0,0,0,0.3)', padding: '10px', borderRadius: '6px' }}>
                  {em.body}
                </pre>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Audit Trail Tab */}
      {activeTab === 'audit' && (
        <div className="glass-card" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '16px' }}>System Audit Trail</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {auditLogs.map(log => (
              <div key={log.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(10, 13, 20, 0.5)', padding: '10px 14px', borderRadius: '6px', fontSize: '0.85rem' }}>
                <div>
                  <span style={{ color: 'var(--accent-secondary)', fontWeight: 700 }}>[{log.ticket_id}]</span> &nbsp;
                  <span style={{ color: 'var(--accent-success)', fontWeight: 600 }}>{log.action}</span> by <strong>{log.actor}</strong>: {log.details}
                </div>
                <div style={{ color: 'var(--text-dim)', fontSize: '0.75rem' }}>{new Date(log.timestamp).toLocaleTimeString()}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reassign Modal */}
      {reassignModal.open && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="glass-card" style={{ width: '400px', padding: '24px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '16px' }}>Reassign Ticket {reassignModal.ticketId}</h3>
            <div className="form-group">
              <label>Select Target Support Agent</label>
              <select
                className="form-control"
                value={reassignModal.targetAgent}
                onChange={(e) => setReassignModal({ ...reassignModal, targetAgent: e.target.value })}
              >
                <option value="">-- Choose Agent --</option>
                {engineers
                  .filter(e => e.agent_id !== reassignTicketDetails?.assigned_agent_id)
                  .map(e => (
                  <option key={e.agent_id} value={e.agent_id}>
                    {e.name} ({e.agent_id}) - Level {e.level} [{e.current_load}/{e.max_capacity}]
                  </option>
                ))}
              </select>
            </div>
            <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
              <button onClick={handleExecuteReassign} className="btn btn-primary" style={{ flex: 1 }}>Confirm Reassign</button>
              <button onClick={() => setReassignModal({ open: false, ticketId: null, targetAgent: '' })} className="btn btn-secondary" style={{ flex: 1 }}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
