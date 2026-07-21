import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Matchmaker from './pages/Matchmaker';
import VLMAgent from './pages/VLMAgent';
import SelfHealing from './pages/SelfHealing';

function Navigation() {
  const location = useLocation();
  
  return (
    <nav className="navbar">
      <a href="/" className="navbar-brand">🚀 SAP TestOS</a>
      <ul className="navbar-nav">
        <li><Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>Dashboard</Link></li>
        <li><Link to="/matchmaker" className={`nav-link ${location.pathname === '/matchmaker' ? 'active' : ''}`}>Matchmaker</Link></li>
        <li><Link to="/vlm-agent" className={`nav-link ${location.pathname === '/vlm-agent' ? 'active' : ''}`}>VLM Agent</Link></li>
        <li><Link to="/self-healing" className={`nav-link ${location.pathname === '/self-healing' ? 'active' : ''}`}>Self-Healing</Link></li>
      </ul>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        <main className="container">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/matchmaker" element={<Matchmaker />} />
            <Route path="/vlm-agent" element={<VLMAgent />} />
            <Route path="/self-healing" element={<SelfHealing />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
