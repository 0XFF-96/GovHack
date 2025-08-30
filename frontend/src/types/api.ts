// API Type definitions based on Django backend

export interface Dataset {
  id: string;
  name: string;
  description: string;
  size: number;
  last_updated: string;
  record_count: number;
  portfolios?: number;
  departments?: number;
}

export interface DatasetsResponse {
  datasets: Dataset[];
}

export interface ChatMessage {
  id: number;
  message_type: 'user' | 'assistant';
  content: string;
  metadata?: Record<string, any>;
  trust_score?: number | null;
  timestamp: string;
  context?: QueryContext | null;
}

export interface QueryContext {
  extracted_entities: Record<string, any>;
  intent: string;
  data_sources: string[];
  processing_time: number;
}

export interface ChatQueryRequest {
  query: string;
  context?: Record<string, any>;
  session_id?: string;
}

export interface ProcessingInfo {
  processing_time: number;
  data_sources_used: string[];
  intent_detected: string;
}

export interface ChatQueryResponse {
  session_id: string;
  user_message: ChatMessage;
  assistant_message: ChatMessage;
  processing_info: ProcessingInfo;
  trust_score: number;
}

export interface ChatSession {
  id: number;
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface DataSearchRequest {
  query: string;
  filters?: {
    department?: string;
    category?: string;
    min_amount?: number;
    max_amount?: number;
  };
  limit?: number;
}

export interface SearchResult {
  department: string;
  program: string;
  amount: number;
  category: string;
  description: string;
}

export interface DataSearchResponse {
  results: SearchResult[];
  total: number;
  query_time: number;
}

export interface BudgetExpense {
  portfolio: string;
  department: string;
  program: string;
  expense_type: string;
  amount_2024_25?: number;
  amount_2023_24?: number;
  amount_2025_26?: number;
  amount_2026_27?: number;
  amount_2027_28?: number;
}

export interface ApiError {
  error?: string;
  detail?: string;
  message?: string;
}