import React, { useState } from 'react';
import Navbar from './components/Navbar';
import CustomerPortal from './pages/CustomerPortal';
import SupportPortal from './pages/SupportPortal';
import AdminPortal from './pages/AdminPortal';

export default function App() {
  const [activeRole, setActiveRole] = useState('customer'); // customer, support, admin

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar activeRole={activeRole} setActiveRole={setActiveRole} />

      <main style={{ flex: 1 }}>
        {activeRole === 'customer' && <CustomerPortal />}
        {activeRole === 'support' && <SupportPortal />}
        {activeRole === 'admin' && <AdminPortal />}
      </main>

      <footer style={{
        textAlign: 'center',
        padding: '16px',
        fontSize: '0.8rem',
        color: 'var(--text-dim)',
        borderTop: '1px solid var(--border-color)',
        marginTop: '40px'
      }}>
        SwiftDesk — Automated Support Routing & Ticket Automation System © 2026
      </footer>
    </div>
  );
}
