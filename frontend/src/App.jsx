import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import CustomerPortal from './pages/CustomerPortal';
import SupportPortal from './pages/SupportPortal';
import AdminPortal from './pages/AdminPortal';
import LoginPage from './pages/LoginPage';
import UnauthorizedPage from './pages/UnauthorizedPage';

function MainApp() {
  const { isAuthenticated, role } = useAuth();

  // Determine default portal based on JWT role
  const getDefaultPortal = (userRole) => {
    if (userRole === 'SUPPORT') return 'support';
    if (userRole === 'ADMIN') return 'admin';
    return 'customer';
  };

  const [activeRole, setActiveRole] = useState(() => getDefaultPortal(role));

  // Sync default portal when user logs in or switches
  useEffect(() => {
    if (role) {
      setActiveRole(getDefaultPortal(role));
    }
  }, [role]);

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  // Check Role Authorization for Active Portal
  const isAuthorized = () => {
    if (role === 'ADMIN') return true;
    if (role === 'CUSTOMER' && activeRole === 'customer') return true;
    if (role === 'SUPPORT' && activeRole === 'support') return true;
    return false;
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar activeRole={activeRole} setActiveRole={setActiveRole} />

      <main style={{ flex: 1 }}>
        {!isAuthorized() ? (
          <UnauthorizedPage onNavigateHome={() => setActiveRole(getDefaultPortal(role))} />
        ) : (
          <>
            {activeRole === 'customer' && <CustomerPortal />}
            {activeRole === 'support' && <SupportPortal />}
            {activeRole === 'admin' && <AdminPortal />}
          </>
        )}
      </main>

      <footer style={{
        textAlign: 'center',
        padding: '16px',
        fontSize: '0.8rem',
        color: 'var(--text-dim)',
        borderTop: '1px solid var(--border-color)',
        marginTop: '40px'
      }}>
        SwiftDesk — Support Routing System with JWT Auth & RBAC © 2026
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}
