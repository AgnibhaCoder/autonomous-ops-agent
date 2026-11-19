import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const createTask = async (prompt) => {
  const response = await apiClient.post('/tasks/', { prompt });
  return response.data;
};

export const getTasks = async () => {
  const response = await apiClient.get('/tasks/');
  return response.data;
};

export const getTaskById = async (taskId) => {
  const response = await apiClient.get(`/tasks/${taskId}`);
  return response.data;
};

export const submitApprovalDecision = async (taskId, approvalId, approved, reason = '') => {
  const response = await apiClient.post(`/tasks/${taskId}/approvals/${approvalId}`, {
    approved,
    reason,
  });
  return response.data;
};

export default apiClient;