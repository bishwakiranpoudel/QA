import React from 'react';
import { Link } from 'react-router-dom';

function Dashboard() {
  const features = [
    {
      title: "🎯 Matchmaker",
      description: "Find the perfect SAP consultants for your projects using hybrid search. Auto-generate Statements of Work (SoW) to win deals faster.",
      link: "/matchmaker",
      color: "#0070d2"
    },
    {
      title: "🤖 VLM Agent",
      description: "Convert manual SAP test cases into automated Playwright scripts using AI. Supports SAP Fiori with hybrid DOM + Vision analysis.",
      link: "/vlm-agent",
      color: "#28a745"
    },
    {
      title: "🔧 Self-Healing",
      description: "Automatically fix broken test scripts when SAP UI changes. AST-based surgical patching preserves test logic while updating selectors.",
      link: "/self-healing",
      color: "#dc3545"
    }
  ];

  return (
    <div>
      <div className="card" style={{ textAlign: 'center', padding: '40px 20px' }}>
        <h1 style={{ fontSize: '32px', marginBottom: '10px' }}>Welcome to SAP TestOS</h1>
        <p style={{ fontSize: '18px', color: '#666', maxWidth: '600px', margin: '0 auto' }}>
          The intelligent platform for SAP consulting lifecycle - from pre-sales to operations
        </p>
      </div>

      <div className="grid grid-3">
        {features.map((feature, index) => (
          <div key={index} className="card" style={{ borderTop: `4px solid ${feature.color}` }}>
            <h2 style={{ color: feature.color }}>{feature.title}</h2>
            <p style={{ marginBottom: '20px', color: '#555' }}>{feature.description}</p>
            <Link to={feature.link} className="btn btn-primary" style={{ backgroundColor: feature.color }}>
              Get Started →
            </Link>
          </div>
        ))}
      </div>

      <div className="card" style={{ marginTop: '20px' }}>
        <h2>📊 Platform Capabilities</h2>
        <div className="grid grid-2" style={{ marginTop: '20px' }}>
          <div>
            <h3>Pre-Sales Acceleration</h3>
            <ul style={{ marginLeft: '20px', color: '#555' }}>
              <li>Hybrid search for SAP talent (semantic + keyword)</li>
              <li>Auto-generate professional SoW documents</li>
              <li>Match niche SAP QA talent to projects</li>
              <li>Win S/4HANA migration contracts faster</li>
            </ul>
          </div>
          <div>
            <h3>Test Automation</h3>
            <ul style={{ marginLeft: '20px', color: '#555' }}>
              <li>Convert manual tests to Playwright scripts</li>
              <li>Hybrid DOM + Vision for SAP Fiori</li>
              <li>Self-healing tests reduce maintenance by 70%</li>
              <li>AST-based surgical code patching</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: '20px', background: 'linear-gradient(135deg, #0070d2 0%, #005a9e 100%)', color: 'white' }}>
        <h2 style={{ color: 'white' }}>🚀 Ready to Transform Your SAP Testing?</h2>
        <p style={{ marginBottom: '20px' }}>Start with any module above or explore the full platform capabilities.</p>
      </div>
    </div>
  );
}

export default Dashboard;
