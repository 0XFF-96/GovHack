import { customAxiosInstance } from './axiosConfig';
import type {
  DatasetsResponse,
  Dataset,
  ChatQueryRequest,
  ChatQueryResponse,
  ChatSession,
  DataSearchRequest,
  DataSearchResponse,
} from '../types/api';

// API endpoints
const API_ENDPOINTS = {
  // Datasets
  datasets: '/v1/data/datasets/',
  datasetDetail: (id: string) => `/v1/data/datasets/${id}/`,
  dataSearch: '/v1/data/search/',
  
  // Chat
  chatQuery: '/v1/chat/query/',
  chatSessions: '/v1/chat/sessions/',
  chatSession: (sessionId: string) => `/v1/chat/sessions/${sessionId}/`,
  chatMessages: (sessionId: string) => `/v1/chat/sessions/${sessionId}/messages/`,
  
  // Trust scoring (if implemented)
  trustScore: '/v1/trust/score/',
} as const;

/**
 * Dataset API functions
 */
export const datasetsApi = {
  // Get all datasets
  getDatasets: async (): Promise<DatasetsResponse> => {
    const response = await customAxiosInstance.get(API_ENDPOINTS.datasets);
    return response.data;
  },

  // Get specific dataset details
  getDatasetDetail: async (datasetId: string): Promise<Dataset> => {
    const response = await customAxiosInstance.get(API_ENDPOINTS.datasetDetail(datasetId));
    return response.data;
  },

  // Search data across datasets
  searchData: async (searchParams: DataSearchRequest): Promise<DataSearchResponse> => {
    const response = await customAxiosInstance.post(API_ENDPOINTS.dataSearch, searchParams);
    return response.data;
  },
};

/**
 * Chat API functions
 */
export const chatApi = {
  // Send chat query
  sendQuery: async (queryData: ChatQueryRequest): Promise<ChatQueryResponse> => {
    const response = await customAxiosInstance.post(API_ENDPOINTS.chatQuery, queryData);
    return response.data;
  },

  // Get all chat sessions for user
  getSessions: async (): Promise<ChatSession[]> => {
    const response = await customAxiosInstance.get(API_ENDPOINTS.chatSessions);
    return response.data;
  },

  // Get specific chat session
  getSession: async (sessionId: string): Promise<ChatSession> => {
    const response = await customAxiosInstance.get(API_ENDPOINTS.chatSession(sessionId));
    return response.data;
  },

  // Update chat session (e.g., change title)
  updateSession: async (sessionId: string, updates: Partial<ChatSession>): Promise<ChatSession> => {
    const response = await customAxiosInstance.patch(API_ENDPOINTS.chatSession(sessionId), updates);
    return response.data;
  },

  // Delete chat session
  deleteSession: async (sessionId: string): Promise<void> => {
    await customAxiosInstance.delete(API_ENDPOINTS.chatSession(sessionId));
  },

  // Get messages for a chat session
  getMessages: async (sessionId: string): Promise<any[]> => {
    const response = await customAxiosInstance.get(API_ENDPOINTS.chatMessages(sessionId));
    return response.data;
  },
};

/**
 * Combined API object for easy importing
 */
export const api = {
  datasets: datasetsApi,
  chat: chatApi,
};

export default api;