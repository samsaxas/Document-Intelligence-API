import axios from 'axios';

const API_BASE = '/api';

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 45000,
});

export const apiService = {
  // Document Operations
  processDocument: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/documents/process', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  processPreset: async (presetName) => {
    const response = await apiClient.post(`/documents/process-preset/${presetName}`);
    return response.data;
  },

  listDocuments: async (status = null, limit = 50, offset = 0) => {
    const params = { limit, offset };
    if (status && status !== 'ALL') params.status = status;
    const response = await apiClient.get('/documents', { params });
    return response.data;
  },

  getDocument: async (docId) => {
    const response = await apiClient.get(`/documents/${docId}`);
    return response.data;
  },

  seedSamples: async () => {
    const response = await apiClient.post('/documents/seed-samples');
    return response.data;
  },

  // Manual Review Queue
  getReviewQueue: async (status = 'NEEDS_REVIEW') => {
    const response = await apiClient.get('/review-queue', {
      params: { status }
    });
    return response.data;
  },

  submitReviewDecision: async (docId, submission) => {
    const response = await apiClient.post(`/review-queue/${docId}/submit`, submission);
    return response.data;
  },

  // Benchmarking
  runBenchmark: async () => {
    const response = await apiClient.post('/benchmark/run');
    return response.data;
  },

  getBenchmarkHistory: async () => {
    const response = await apiClient.get('/benchmark/history');
    return response.data;
  },

  // PII Redaction
  redactText: async (text) => {
    const response = await apiClient.post('/pii/redact', { text });
    return response.data;
  },

  // System
  getStats: async () => {
    const response = await apiClient.get('/stats');
    return response.data;
  },

  getHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  }
};
