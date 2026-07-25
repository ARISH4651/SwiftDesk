import React from 'react';
import { ShieldAlert, ArrowLeft } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function UnauthorizedPage({ onNavigateHome }) {
  const { user, role } = useAuth();

  return (
    <div style={{
      maxWidth: '600px',
      margin: '60px auto',
      padding: '40px 24px',
      textAlign: 'center'
    }}>
      <div className="glass-card" style={{ padding: '40px 30px', borderLeft: '4px solid var(--accent-danger)' }}>
        <div style={{
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: 'rgba(239, 68, 68, 0.15)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 16px',
          color: 'var(--accent-danger)'
        }}>
          <ShieldAlert size={36} />
        </div>

        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '8px' }}>
          403 Forbidden Access
        </h2>

        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '20px', lineHeight: '1.6' }}>
          Your current JWT token role (<strong style={{ color: 'var(--accent-secondary)' }}>{role}</strong>) does not have authorization to access this view or resource.
        </p>

        <div style={{
          background: 'rgba(10, 13, 20, 0.6)',
          padding: '12px',
          borderRadius: '8px',
          fontSize: '0.8rem',
          color: 'var(--text-dim)',
          marginBottom: '24px'
        }}>
          Logged in as: <strong>{user?.email}</strong> &nbsp;|&nbsp; Role Claim: <strong>{role}</strong>
        </div>

        <button onClick={onNavigateHome} className="btn btn-primary">
          <ArrowLeft size={16} /> Return to Authorized Portal
        </button>
      </div>
    </div>
  );
}
