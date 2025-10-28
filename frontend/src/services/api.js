import axios from 'axios';

// Use relative URL to leverage Vite proxy
const API_BASE_URL = '/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds for AI API calls
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
  getMetrics: async (force = false) => {
    const url = force ? '/metrics/?force=true' : '/metrics/';
    const response = await api.get(url);
    return response.data;
  },

  // Get workouts
  getWorkouts: async (force = false) => {
    const url = force ? '/workouts/?force=true' : '/workouts/';
    const response = await api.get(url);
    return response.data;
  },

  // Get coach summary
  getCoachSummary: async (force = false) => {
    const response = await api.post('/coach-summary/', { force });
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

