import axios from 'axios';
import { message } from 'antd';

type AxiosRequestConfig = Parameters<typeof axios>[0];

// Create axios instance with custom configuration
export const customAxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
customAxiosInstance.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add request timestamp for debugging
    (config as any).metadata = { startTime: new Date().getTime() };
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
customAxiosInstance.interceptors.response.use(
  (response) => {
    // Calculate request duration
    const endTime = new Date().getTime();
    const duration = endTime - ((response.config as any).metadata?.startTime || endTime);
    
    // Log performance in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`API ${response.config.method?.toUpperCase()} ${response.config.url} - ${duration}ms`);
    }
    
    return response;
  },
  (error) => {
    // Handle different error types
    if (error.response) {
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          message.error('认证失败，请重新登录');
          // Clear auth token and redirect to login
          localStorage.removeItem('auth_token');
          // window.location.href = '/login';
          break;
        case 403:
          message.error('没有权限访问此资源');
          break;
        case 404:
          message.error('请求的资源不存在');
          break;
        case 500:
          message.error('服务器内部错误，请稍后重试');
          break;
        default:
          message.error(data?.message || data?.detail || '请求失败');
      }
    } else if (error.request) {
      message.error('网络连接失败，请检查网络');
    } else {
      message.error('请求配置错误');
    }
    
    return Promise.reject(error);
  }
);

// Custom axios instance for orval
export default <T = any>(config: AxiosRequestConfig): Promise<T> => {
  return customAxiosInstance(config).then(response => response.data);
};