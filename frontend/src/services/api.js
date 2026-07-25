import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const createTicket = (ticketData) => api.post('/api/tickets', ticketData);
export const getTickets = (params) => api.get('/api/tickets', { params });
export const getTicketById = (ticketId) => api.get(`/api/tickets/${ticketId}`);
export const updateTicketStatus = (ticketId, statusData) => api.patch(`/api/tickets/${ticketId}/status`, statusData);

export const getEngineers = () => api.get('/api/engineers');
export const updateEngineerAvailability = (agentId, isAvailable) => api.patch(`/api/engineers/${agentId}/availability`, { is_available: isAvailable });

export const getDashboardStats = () => api.get('/api/admin/dashboard');
export const reassignTicket = (ticketId, agentId, reason = 'Admin reassignment') => api.post(`/api/admin/reassign-ticket/${ticketId}`, { agent_id: agentId, reason });

export const getAuditLogs = (ticketId) => api.get('/api/admin/audit-logs', { params: { ticket_id: ticketId } });
export const getEmailLogs = (ticketId) => api.get('/api/admin/email-logs', { params: { ticket_id: ticketId } });

export const triggerSLA = () => api.post('/api/admin/trigger-sla');
export const triggerEODSummary = () => api.post('/api/admin/trigger-eod-summary');
export const ingestSampleBatch = () => api.post('/api/batch/ingest-sample-data');

export default api;
