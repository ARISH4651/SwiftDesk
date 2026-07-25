import React, { useState } from 'react';
import { Lock, Mail, Shield, Sparkles, UserCheck, KeyRound, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const { login } = useAuth();
  
  const [email, setEmail] = useState('customer@swiftdesk.com');
  const [password, setPassword] = useState('customer123');
  const [role, setRole] = useState('CUSTOMER');
  
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);

    try {
      await login(email, password, role);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const fillCredentials = (type) => {
    setErrorMsg(null);
    if (type === 'CUSTOMER') {
      setEmail('customer@swiftdesk.com');
      setPassword('customer123');
      setRole('CUSTOMER');
    } else if (type === 'SUPPORT') {
      setEmail('support@swiftdesk.com');
      setPassword('support123');
      setRole('SUPPORT');
    } else if (type === 'ADMIN') {
      setEmail('admin@swiftdesk.com');
      setPassword('admin123');
      setRole('ADMIN');
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      background: 'radial-gradient(circle at center, rgba(99, 102, 241, 0.15) 0%, rgba(10, 13, 20, 0.95) 70%)'
    }}>
      <div className="glass-card" style={{ width: '100%', maxWidth: '440px', padding: '32px' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div style={{
            width: '50px',
            height: '50px',
            borderRadius: '14px',
            background: 'linear-gradient(135deg, #6366f1, #06b6d4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 12px',
            boxShadow: '0 0 20px rgba(99, 102, 241, 0.6)'
          }}>
            <Sparkles size={28} color="#ffffff" />
          </div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800 }}>SwiftDesk Portal</h1>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            JWT Authentication & Role-Based Access Control
          </p>
        </div>

        {/* Quick Pre-fill Credentials */}
        <div style={{ display: 'flex', gap: '6px', marginBottom: '20px' }}>
          <button
            type="button"
            onClick={() => fillCredentials('CUSTOMER')}
            className={`btn btn-sm ${role === 'CUSTOMER' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ flex: 1, fontSize: '0.75rem' }}
          >
            Customer
          </button>
          <button
            type="button"
            onClick={() => fillCredentials('SUPPORT')}
            className={`btn btn-sm ${role === 'SUPPORT' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ flex: 1, fontSize: '0.75rem' }}
          >
            Support
          </button>
          <button
            type="button"
            onClick={() => fillCredentials('ADMIN')}
            className={`btn btn-sm ${role === 'ADMIN' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ flex: 1, fontSize: '0.75rem' }}
          >
            Admin
          </button>
        </div>

        {errorMsg && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            color: '#fca5a5',
            padding: '12px',
            borderRadius: '8px',
            fontSize: '0.85rem',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email Address</label>
            <div style={{ position: 'relative' }}>
              <input
                type="email"
                className="form-control"
                style={{ paddingLeft: '38px' }}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <Mail size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            </div>
          </div>

          <div className="form-group">
            <label>Password</label>
            <div style={{ position: 'relative' }}>
              <input
                type="password"
                className="form-control"
                style={{ paddingLeft: '38px' }}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <KeyRound size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            </div>
          </div>

          <div className="form-group" style={{ marginBottom: '20px' }}>
            <label>Select Role</label>
            <select
              className="form-control"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              required
            >
              <option value="CUSTOMER">CUSTOMER (Customer Portal Only)</option>
              <option value="SUPPORT">SUPPORT (Support Team Portal Only)</option>
              <option value="ADMIN">ADMIN (Full Operations Access)</option>
            </select>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '12px', fontSize: '0.95rem', fontWeight: 700 }}
            disabled={loading}
          >
            {loading ? 'Authenticating...' : 'Sign In to SwiftDesk'}
          </button>
        </form>
      </div>
    </div>
  );
}
