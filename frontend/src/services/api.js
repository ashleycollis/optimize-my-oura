import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
  withCredentials: true, // Important for Django sessions
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API functions
export const apiService = {
  // Get metrics
  getMetrics: async () => {
    const response = await api.get('/metrics/');
    return response.data;
  },

  // Get coach summary
  getCoachSummary: async () => {
    const response = await api.post('/coach-summary/');
    return response.data;
  },

  // Get trend insight
  getTrendInsight: async () => {
    const response = await api.get('/trend-insight/');
    return response.data;
  },

  // Send chat message
  sendChatMessage: async (message) => {
    const response = await api.post('/chat/', { message });
    return response.data;
  },

  // Connect Oura account
  connectOura: async (token) => {
    const response = await api.post('/connect-oura/', { token });
    return response.data;
  },
};

export default api;

