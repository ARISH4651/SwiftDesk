import React from 'react';
import { Shield, Users, User, Activity, Sparkles } from 'lucide-react';

export default function Navbar({ activeRole, setActiveRole }) {
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
        justifyContent: 'space-between'
      }}>
        {/* Brand Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #6366f1, #06b6d4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 15px rgba(99, 102, 241, 0.5)'
          }}>
            <Sparkles size={22} color="#ffffff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.4rem', fontWeight: 800, background: 'linear-gradient(90deg, #ffffff, #a5b4fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              SwiftDesk
            </h1>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Automation & AI Routing Platform</p>
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
          <button
            onClick={() => setActiveRole('customer')}
            className="btn"
            style={{
              borderRadius: '20px',
              padding: '8px 18px',
              fontSize: '0.85rem',
              background: activeRole === 'customer' ? 'linear-gradient(135deg, #6366f1, #4f46e5)' : 'transparent',
              color: activeRole === 'customer' ? '#fff' : 'var(--text-muted)'
            }}
          >
            <User size={16} /> Customer Portal
          </button>

          <button
            onClick={() => setActiveRole('support')}
            className="btn"
            style={{
              borderRadius: '20px',
              padding: '8px 18px',
              fontSize: '0.85rem',
              background: activeRole === 'support' ? 'linear-gradient(135deg, #06b6d4, #0891b2)' : 'transparent',
              color: activeRole === 'support' ? '#fff' : 'var(--text-muted)'
            }}
          >
            <Users size={16} /> Support Team Portal
          </button>

          <button
            onClick={() => setActiveRole('admin')}
            className="btn"
            style={{
              borderRadius: '20px',
              padding: '8px 18px',
              fontSize: '0.85rem',
              background: activeRole === 'admin' ? 'linear-gradient(135deg, #10b981, #059669)' : 'transparent',
              color: activeRole === 'admin' ? '#fff' : 'var(--text-muted)'
            }}
          >
            <Shield size={16} /> Admin Dashboard
          </button>
        </div>

        {/* Status indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: '#10b981' }}>
          <Activity size={16} className="animate-pulse" />
          <span>API Engine Online</span>
        </div>
      </div>
    </header>
  );
}
