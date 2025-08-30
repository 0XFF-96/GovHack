// API Response types based on backend structure

// Base response structure
export interface ApiResponse<T = any> {
  status: 'success' | 'error';
  data: T;
  message?: string;
  metadata?: {
    query_id?: string;
    processing_time?: number;
    timestamp?: string;
  };
}

// Dataset types - matching actual backend response
export interface Dataset {
  id: string;
  name: string;
  description: string;
  size: number;
  last_updated: string;
  record_count: number;
  portfolios?: number;
  departments?: number;
  status?: 'active' | 'processing' | 'error';
}

export interface DatasetsResponse {
  datasets: Dataset[];
  count?: number;
  next?: string;
  previous?: string;
}

// Budget data types - matching backend serializers
export interface BudgetRecord {
  id: string;
  department: string;
  portfolio: string;
  program: string;
  outcome: string;
  amount_2023_24?: number;
  amount_2024_25?: number;
  amount_2025_26?: number;
  amount_2026_27?: number;
  amount_2027_28?: number;
  expense_type: string;
  appropriation_type: string;
  description?: string;
  created_at: string;
}

export interface BudgetSummary {
  fiscal_year: string;
  total_budget: number;
  portfolio_count: number;
  department_count: number;
  program_count: number;
  top_portfolios: Array<{
    name: string;
    amount: number;
  }>;
  expense_breakdown: Array<{
    type: string;
    amount: number;
    count: number;
  }>;
}

export interface BudgetTrend {
  entity_type: 'portfolio' | 'department';
  entity_name: string;
  trend_data: Array<{
    fiscal_year: string;
    total_amount: number;
    year_over_year_change?: number;
  }>;
  summary?: {
    avg_growth_rate: number;
    total_change_5_year: number;
    peak_year: string;
    lowest_year: string;
  };
}

// Chat types - matching actual backend response
export interface ChatMessage {
  id: string;
  message_type: 'user' | 'assistant' | 'system';
  content: string;
  metadata?: any;
  trust_score?: number;
  timestamp: string;
  context?: any;
}

export interface ChatSession {
  id: string;
  session_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  message_count: number;
}

export interface ChatQueryRequest {
  query: string;
  session_id?: string;
  context?: {
    fiscal_year?: string;
    department?: string;
    filters?: Record<string, any>;
  };
}

export interface ChatQueryResponse {
  session_id: string;
  user_message: ChatMessage;
  assistant_message: ChatMessage;
  processing_info: {
    processing_time: number;
    data_sources_used: string[];
    intent_detected: string;
    model_used: string;
  };
  trust_score: number;
}

// Trust scoring types
export interface TrustScore {
  overall_score: number;
  dimensions: {
    source_reliability: number;
    query_match: number;
    data_completeness: number;
    historical_accuracy: number;
  };
  explanation: string;
  level: 'high' | 'medium' | 'low';
}

// Data search types
export interface DataSearchRequest {
  query?: string;
  filters?: {
    dataset_id?: string;
    fiscal_year?: string;
    department?: string;
    amount_min?: number;
    amount_max?: number;
    category?: string;
  };
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  page?: number;
  page_size?: number;
}

export interface DataSearchResponse {
  results: BudgetRecord[];
  count: number;
  summary: BudgetSummary;
  aggregations?: {
    by_department: Array<{ department: string; total: number }>;
    by_year: Array<{ year: string; total: number }>;
    by_category: Array<{ category: string; total: number }>;
  };
}

// Error types
export interface ApiError {
  message: string;
  status?: number;
  data?: any;
  originalError?: any;
}