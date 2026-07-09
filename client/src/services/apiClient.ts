import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient: AxiosInstance = axios.create({
  baseURL: `${baseURL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 35000, // 35s client timeout (5s buffer above server 30s)
});

// Retry interceptor: retries on 408, 429, and 5xx
let retryCount = 0;
const MAX_RETRIES = 3;

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as InternalAxiosRequestConfig & { retryCount?: number };

    if (!config) {
      return Promise.reject(error);
    }

    config.retryCount = config.retryCount || 0;

    const shouldRetry =
      config.retryCount < MAX_RETRIES &&
      (error.status === 408 ||
        error.status === 429 ||
        (error.status !== undefined && error.status >= 500));

    if (shouldRetry) {
      config.retryCount += 1;
      // Exponential backoff: 1s, 2s, 4s
      const delay = Math.pow(2, config.retryCount - 1) * 1000;
      await new Promise((resolve) => setTimeout(resolve, delay));
      return apiClient(config);
    }

    return Promise.reject(error);
  }
);

export default apiClient;
