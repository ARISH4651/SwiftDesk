import React from 'react';
import { Shield, Users, User, Activity, Sparkles, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar({ activeRole, setActiveRole }) {
  const { user, role, logout } = useAuth();

  const isCustomerAllowed = role === 'CUSTOMER' || role === 'ADMIN';
  const isSupportAllowed = role === 'SUPPORT' || role === 'ADMIN';
  const isAdminAllowed = role === 'ADMIN';

  return (
    <header style={{
      background: 'rgba(10, 13, 20, 0.85)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border-color)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      padding: '12px 24px'
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        {/* Brand Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #6366f1, #06b6d4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 15px rgba(99, 102, 241, 0.5)'
          }}>
            <Sparkles size={20} color="#ffffff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.3rem', fontWeight: 800, background: 'linear-gradient(90deg, #ffffff, #a5b4fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              SwiftDesk
            </h1>
            <p style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>Automated Support & JWT RBAC</p>
          </div>
        </div>

        {/* Role Navigation Switcher */}
        <div style={{
          display: 'flex',
          background: 'rgba(22, 28, 45, 0.8)',
          padding: '4px',
          borderRadius: '30px',
          border: '1px solid var(--border-color)'
        }}>
          {isCustomerAllowed && (
            <button
              onClick={() => setActiveRole('customer')}
              className="btn"
              style={{
                borderRadius: '20px',
                padding: '6px 16px',
                fontSize: '0.825rem',
                background: activeRole === 'customer' ? 'linear-gradient(135deg, #6366f1, #4f46e5)' : 'transparent',
                color: activeRole === 'customer' ? '#fff' : 'var(--text-muted)'
              }}
            >
              <User size={15} /> Customer Portal
            </button>
          )}

          {isSupportAllowed && (
            <button
              onClick={() => setActiveRole('support')}
              className="btn"
              style={{
                borderRadius: '20px',
                padding: '6px 16px',
                fontSize: '0.825rem',
                background: activeRole === 'support' ? 'linear-gradient(135deg, #06b6d4, #0891b2)' : 'transparent',
                color: activeRole === 'support' ? '#fff' : 'var(--text-muted)'
              }}
            >
              <Users size={15} /> Support Team Portal
            </button>
          )}

          {isAdminAllowed && (
            <button
              onClick={() => setActiveRole('admin')}
              className="btn"
              style={{
                borderRadius: '20px',
                padding: '6px 16px',
                fontSize: '0.825rem',
                background: activeRole === 'admin' ? 'linear-gradient(135deg, #10b981, #059669)' : 'transparent',
                color: activeRole === 'admin' ? '#fff' : 'var(--text-muted)'
              }}
            >
              <Shield size={15} /> Admin Dashboard
            </button>
          )}
        </div>

        {/* Auth User Details & Logout */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ textAlign: 'right', fontSize: '0.8rem' }}>
            <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>{user?.email}</div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '4px', marginTop: '2px' }}>
              <span className={`badge ${role === 'ADMIN' ? 'badge-high' : role === 'SUPPORT' ? 'badge-assigned' : 'badge-new'}`} style={{ fontSize: '0.65rem', padding: '2px 8px' }}>
                {role}
              </span>
            </div>
          </div>

          <button onClick={logout} className="btn btn-secondary btn-sm" title="Sign Out">
            <LogOut size={14} /> Logout
          </button>
        </div>
      </div>
    </header>
  );
}
