import React, { useState, useEffect } from 'react';
import { matchmakerAPI } from '../services/api';

function Matchmaker() {
  const [searchQuery, setSearchQuery] = useState('');
  const [consultants, setConsultants] = useState([]);
  const [sowResult, setSowResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [projectRequirements, setProjectRequirements] = useState({
    client_name: '',
    project_type: 'S/4HANA Migration',
    sap_modules: [],
    timeline_weeks: 24,
    budget: ''
  });

  const sapModules = ['FICO', 'MM', 'SD', 'PP', 'QM', 'PM', 'PS', 'BW', 'S/4HANA', 'Fiori', 'Basis'];

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    try {
      const response = await matchmakerAPI.searchConsultants(searchQuery);
      setConsultants(response.data.data || []);
    } catch (error) {
      console.error('Search error:', error);
      // Use mock data for demo
      setConsultants(getMockConsultants());
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateSOW = async () => {
    setLoading(true);
    try {
      const response = await matchmakerAPI.generateSOW(projectRequirements);
      setSowResult(response.data.data || response.data);
    } catch (error) {
      console.error('SOW generation error:', error);
      setSowResult(getMockSOW());
    } finally {
      setLoading(false);
    }
  };

  const toggleModule = (module) => {
    setProjectRequirements(prev => ({
      ...prev,
      sap_modules: prev.sap_modules.includes(module)
        ? prev.sap_modules.filter(m => m !== module)
        : [...prev.sap_modules, module]
    }));
  };

  const getMockConsultants = () => [
    { id: 1, name: 'Rajesh Kumar', email: 'rajesh.k@example.com', experience_years: 12, sap_modules: ['FICO', 'S/4HANA'], rate_per_hour: 175, match_score: 95 },
    { id: 2, name: 'Maria Santos', email: 'maria.s@example.com', experience_years: 8, sap_modules: ['MM', 'SD'], rate_per_hour: 150, match_score: 85 },
    { id: 3, name: 'Thomas Mueller', email: 'thomas.m@example.com', experience_years: 10, sap_modules: ['SD', 'Fiori'], rate_per_hour: 165, match_score: 80 },
  ];

  const getMockSOW = () => ({
    project_title: `SAP S/4HANA Migration - ${projectRequirements.client_name || 'Client'}`,
    executive_summary: 'Comprehensive S/4HANA migration project covering finance, logistics, and user experience modernization.',
    scope_of_work: ['Current state assessment', 'Gap analysis', 'System design', 'Configuration', 'Data migration', 'Testing', 'Go-live support'],
    timeline_weeks: 24,
    estimated_cost: 450000,
    key_milestones: ['Kickoff', 'Blueprint sign-off', 'Realization complete', 'UAT complete', 'Go-live']
  });

  return (
    <div>
      <h1>🎯 Intelligent Matchmaker</h1>
      <p style={{ marginBottom: '20px', color: '#666' }}>Find the perfect SAP consultants and generate winning proposals</p>

      <div className="grid grid-2">
        <div className="card">
          <h2>Search Consultants</h2>
          <input
            type="text"
            className="input"
            placeholder="Search by SAP module (e.g., FICO, MM, S/4HANA)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button className="btn btn-primary" onClick={handleSearch} disabled={loading}>
            {loading ? 'Searching...' : '🔍 Search'}
          </button>

          {consultants.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h3>Top Matches</h3>
              {consultants.map((consultant) => (
                <div key={consultant.id} style={{ padding: '15px', borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <strong>{consultant.name}</strong>
                    <div style={{ fontSize: '13px', color: '#666' }}>{consultant.email}</div>
                    <div style={{ fontSize: '13px', color: '#0070d2' }}>
                      {consultant.sap_modules?.join(', ')} • {consultant.experience_years} yrs • ${consultant.rate_per_hour}/hr
                    </div>
                  </div>
                  <span className="badge badge-success">Match: {consultant.match_score || 85}%</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <h2>Generate Statement of Work</h2>
          <input
            type="text"
            className="input"
            placeholder="Client Name"
            value={projectRequirements.client_name}
            onChange={(e) => setProjectRequirements({...projectRequirements, client_name: e.target.value})}
          />
          
          <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>SAP Modules:</label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '15px' }}>
            {sapModules.map((module) => (
              <button
                key={module}
                className={`badge ${projectRequirements.sap_modules.includes(module) ? 'badge-info' : 'badge-warning'}`}
                style={{ cursor: 'pointer', padding: '8px 12px' }}
                onClick={() => toggleModule(module)}
              >
                {module}
              </button>
            ))}
          </div>

          <button className="btn btn-primary" onClick={handleGenerateSOW} disabled={loading}>
            {loading ? 'Generating...' : '📄 Generate SoW'}
          </button>

          {sowResult && (
            <div style={{ marginTop: '20px', padding: '15px', background: '#f8f9fa', borderRadius: '5px' }}>
              <h3>{sowResult.project_title}</h3>
              <p style={{ color: '#666', marginBottom: '15px' }}>{sowResult.executive_summary}</p>
              <div><strong>Timeline:</strong> {sowResult.timeline_weeks} weeks</div>
              <div><strong>Estimated Cost:</strong> ${sowResult.estimated_cost?.toLocaleString()}</div>
              <div style={{ marginTop: '10px' }}><strong>Milestones:</strong> {sowResult.key_milestones?.join(' → ')}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Matchmaker;
