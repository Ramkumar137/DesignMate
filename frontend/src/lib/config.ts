// API Configuration
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000');

export const API_ENDPOINTS = {
  GENERATE: `${API_BASE_URL}/generate/run`,
  AI_ASSISTANT: `${API_BASE_URL}/ai-assistant/chat`,
  UPLOAD: `${API_BASE_URL}/upload/sketch`,
  HEALTH: `${API_BASE_URL}/health`,
} as const;

export default API_ENDPOINTS;

