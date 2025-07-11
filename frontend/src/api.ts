import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

export async function fetchDailySleep(params?: { start_date?: string; end_date?: string }) {
  const { data } = await api.get('/sleep/daily', { params });
  return data;
}

export async function fetchDailyActivity(params?: { start_date?: string; end_date?: string }) {
  const { data } = await api.get('/activity/daily', { params });
  return data;
}

export async function fetchDailyReadiness(params?: { start_date?: string; end_date?: string }) {
  const { data } = await api.get('/readiness/daily', { params });
  return data;
}


