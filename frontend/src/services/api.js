import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Matchmaker API
export const matchmakerAPI = {
  searchConsultants: (query, topK = 5) => 
    api.post(`/matchmaker/search-consultants?query=${encodeURIComponent(query)}&top_k=${topK}`),
  
  generateSOW: (projectRequirements) => 
    api.post('/matchmaker/generate-sow', projectRequirements),
  
  listConsultants: () => 
    api.get('/matchmaker/consultants'),
  
  createConsultant: (data) => 
    api.post('/matchmaker/consultants', data),
  
  listProjects: () => 
    api.get('/matchmaker/projects'),
  
  createProject: (data) => 
    api.post('/matchmaker/projects', data),
};

// VLM Agent API
export const vlmAgentAPI = {
  generateTest: (manualSteps, htmlContent = null, screenshotB64 = null) =>
    api.post('/vlm-agent/generate-test', { manual_steps: manualSteps, html_content: htmlContent, screenshot_b64: screenshotB64 }),
  
  extractDOM: (htmlContent) =>
    api.post('/vlm-agent/extract-dom', { html_content: htmlContent }),
  
  getSampleManualTest: () =>
    api.get('/vlm-agent/sample-manual-test'),
};

// Self-Healing API
export const selfHealingAPI = {
  healTest: (testCaseId, errorMessage, domTree = null, screenshotB64 = null) =>
    api.post('/self-healing/heal', { test_case_id: testCaseId, error_message: errorMessage, dom_tree: domTree, screenshot_b64: screenshotB64 }),
  
  getSampleError: () =>
    api.get('/self-healing/sample-error'),
  
  healthCheck: () =>
    api.get('/self-healing/health-check'),
};

export default api;
