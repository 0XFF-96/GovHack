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

// Chat types
export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  created_at: string;
  trust_score?: number;
  sources?: Array<{
    dataset: string;
    table: string;
    rows: number[];
  }>;
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message?: ChatMessage;
}

export interface ChatQueryRequest {
  query: string;
  session_id?: string;
  context?: {
    fiscal_year?: string;
    department?: string;
    filters?: Record<string, any>;
  };
  options?: {
    include_confidence?: boolean;
    include_sources?: boolean;
    max_results?: number;
  };
}

export interface ChatQueryResponse {
  answer: string;
  confidence_score?: number;
  sources?: Array<{
    dataset: string;
    table: string;
    rows: number[];
  }>;
  suggested_followups?: string[];
  session_id: string;
  message_id: string;
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