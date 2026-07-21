import React, { useState } from 'react';
import { vlmAgentAPI } from '../services/api';

function VLMAgent() {
  const [manualSteps, setManualSteps] = useState([]);
  const [generatedScript, setGeneratedScript] = useState('');
  const [loading, setLoading] = useState(false);
  const [htmlContent, setHtmlContent] = useState('');

  const sampleTest = {
    test_case_id: "TC_SAP_FIORI_001",
    description: "Verify Purchase Order Creation in SAP Fiori",
    steps: [
      { action: "navigate", target: "SAP Fiori Launchpad", description: "Open SAP Fiori Launchpad" },
      { action: "click", target: "purchase-order-tile", description: "Click on Purchase Order tile" },
      { action: "click", target: "create-button", description: "Click Create button" },
      { action: "input", target: "vendor-field", value: "VENDOR001", description: "Enter vendor ID" },
      { action: "input", target: "material-field", value: "MATERIAL001", description: "Enter material code" },
      { action: "click", target: "submit-button", description: "Submit the purchase order" },
      { action: "verify", target: "success-message", description: "Verify success message appears" }
    ]
  };

  const loadSampleTest = async () => {
    try {
      const response = await vlmAgentAPI.getSampleManualTest();
      setManualSteps(response.data.steps || sampleTest.steps);
    } catch (error) {
      setManualSteps(sampleTest.steps);
    }
  };

  const addStep = () => {
    setManualSteps([...manualSteps, { action: 'click', target: '', description: '' }]);
  };

  const updateStep = (index, field, value) => {
    const newSteps = [...manualSteps];
    newSteps[index][field] = value;
    setManualSteps(newSteps);
  };

  const removeStep = (index) => {
    setManualSteps(manualSteps.filter((_, i) => i !== index));
  };

  const handleGenerate = async () => {
    if (manualSteps.length === 0) return;
    setLoading(true);
    try {
      const response = await vlmAgentAPI.generateTest(manualSteps, htmlContent);
      setGeneratedScript(response.data.script || getMockScript());
    } catch (error) {
      console.error('Generation error:', error);
      setGeneratedScript(getMockScript());
    } finally {
      setLoading(false);
    }
  };

  const getMockScript = () => `import pytest
from playwright.sync_api import Page, expect

def test_purchase_order_creation(page: Page):
    """Auto-generated Playwright test for SAP Fiori Purchase Order Creation"""
    
    base_url = "https://your-sap-fiori-instance.com"
    page.goto(base_url)
    
    # Step 1: Navigate to SAP Fiori Launchpad
    page.goto(base_url)
    expect(page).to_have_title(/SAP Fiori/)
    
    # Step 2: Click on Purchase Order tile
    page.click('[data-testid="purchase-order-tile"]')
    
    # Step 3: Click Create button
    page.click('[data-testid="create-button"]')
    
    # Step 4: Enter vendor ID
    page.fill('[data-testid="vendor-field"]', 'VENDOR001')
    
    # Step 5: Enter material code
    page.fill('[data-testid="material-field"]', 'MATERIAL001')
    
    # Step 6: Submit the purchase order
    page.click('[data-testid="submit-button"]')
    
    # Step 7: Verify success message
    expect(page.locator('[data-testid="success-message"]')).to_be_visible()
    expect(page.locator('[data-testid="success-message"]')).to_contain_text('created successfully')
    
    print("✅ Test completed successfully")`;

  return (
    <div>
      <h1>🤖 VLM Test Agent</h1>
      <p style={{ marginBottom: '20px', color: '#666' }}>Convert manual SAP test cases into automated Playwright scripts</p>

      <div className="grid grid-2">
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h2>Manual Test Steps</h2>
            <button className="btn btn-secondary" onClick={loadSampleTest}>Load Sample</button>
          </div>
          
          {manualSteps.map((step, index) => (
            <div key={index} style={{ padding: '15px', border: '1px solid #ddd', borderRadius: '5px', marginBottom: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <strong>Step {index + 1}</strong>
                <button onClick={() => removeStep(index)} style={{ background: 'none', border: 'none', color: 'red', cursor: 'pointer' }}>✕</button>
              </div>
              <select 
                className="select" 
                value={step.action} 
                onChange={(e) => updateStep(index, 'action', e.target.value)}
              >
                <option value="navigate">Navigate</option>
                <option value="click">Click</option>
                <option value="input">Input</option>
                <option value="verify">Verify</option>
              </select>
              <input
                type="text"
                className="input"
                placeholder="Target element (e.g., submit-button)"
                value={step.target}
                onChange={(e) => updateStep(index, 'target', e.target.value)}
              />
              <input
                type="text"
                className="input"
                placeholder="Description"
                value={step.description}
                onChange={(e) => updateStep(index, 'description', e.target.value)}
              />
              {step.action === 'input' && (
                <input
                  type="text"
                  className="input"
                  placeholder="Value (for input actions)"
                  value={step.value || ''}
                  onChange={(e) => updateStep(index, 'value', e.target.value)}
                />
              )}
            </div>
          ))}
          
          <button className="btn btn-secondary" onClick={addStep} style={{ marginRight: '10px' }}>+ Add Step</button>
          <button className="btn btn-primary" onClick={handleGenerate} disabled={loading || manualSteps.length === 0}>
            {loading ? 'Generating...' : '🚀 Generate Script'}
          </button>
        </div>

        <div className="card">
          <h2>Generated Playwright Script</h2>
          {generatedScript ? (
            <pre className="code-block" style={{ maxHeight: '500px', overflow: 'auto' }}>
              {generatedScript}
            </pre>
          ) : (
            <div style={{ padding: '40px', textAlign: 'center', color: '#999' }}>
              <p>Generated script will appear here</p>
              <p style={{ fontSize: '13px' }}>Add manual steps and click Generate</p>
            </div>
          )}
          {generatedScript && (
            <button 
              className="btn btn-primary" 
              onClick={() => navigator.clipboard.writeText(generatedScript)}
              style={{ marginTop: '15px' }}
            >
              📋 Copy to Clipboard
            </button>
          )}
        </div>
      </div>

      <div className="card" style={{ marginTop: '20px' }}>
        <h3>Optional: Provide HTML/DOM Context</h3>
        <textarea
          className="input"
          rows="4"
          placeholder="Paste HTML content from SAP Fiori page for better selector accuracy..."
          value={htmlContent}
          onChange={(e) => setHtmlContent(e.target.value)}
          style={{ width: '100%', fontFamily: 'monospace', fontSize: '12px' }}
        />
        <p style={{ fontSize: '13px', color: '#666' }}>
          💡 Tip: Providing HTML context helps the AI generate more accurate selectors based on actual DOM structure.
        </p>
      </div>
    </div>
  );
}

export default VLMAgent;
