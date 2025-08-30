'use client';

import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import { api } from '../lib/api';
import type { 
  BudgetSummary, 
  BudgetTrend, 
  DataSearchRequest, 
  DataSearchResponse,
  Dataset,
  DatasetsResponse 
} from '../types/api';

// Query keys for React Query cache management
export const budgetQueryKeys = {
  all: ['budget'] as const,
  summary: (year?: string) => ['budget', 'summary', year] as const,
  trends: (years?: string[]) => ['budget', 'trends', years] as const,
  search: (params: DataSearchRequest) => ['budget', 'search', params] as const,
  datasets: () => ['datasets'] as const,
  dataset: (id: string) => ['datasets', id] as const,
};

/**
 * Hook to fetch budget summary data
 */
export const useBudgetSummary = (
  fiscalYear?: string,
  options?: UseQueryOptions<BudgetSummary>
) => {
  return useQuery({
    queryKey: budgetQueryKeys.summary(fiscalYear),
    queryFn: () => api.budget.getSummary(fiscalYear),
    staleTime: 5 * 60 * 1000, // 5 minutes
    ...options,
  });
};

/**
 * Hook to fetch budget trends for a specific entity
 */
export const useBudgetTrends = (
  entityType: 'portfolio' | 'department' = 'portfolio',
  entityName: string = 'Health and Aged Care',
  options?: UseQueryOptions<BudgetTrend[]>
) => {
  return useQuery({
    queryKey: budgetQueryKeys.trends([entityType, entityName]),
    queryFn: () => api.budget.getTrends(entityType, entityName),
    staleTime: 10 * 60 * 1000, // 10 minutes
    ...options,
  });
};

/**
 * Hook to search budget data with filters
 */
export const useBudgetSearch = (
  searchParams: DataSearchRequest,
  options?: UseQueryOptions<DataSearchResponse>
) => {
  return useQuery({
    queryKey: budgetQueryKeys.search(searchParams),
    queryFn: () => api.budget.search(searchParams),
    enabled: !!searchParams.query || !!Object.keys(searchParams.filters || {}).length,
    staleTime: 2 * 60 * 1000, // 2 minutes
    ...options,
  });
};

/**
 * Hook to fetch all available datasets
 */
export const useDatasets = (options?: UseQueryOptions<DatasetsResponse>) => {
  return useQuery({
    queryKey: budgetQueryKeys.datasets(),
    queryFn: () => api.datasets.getAll(),
    staleTime: 15 * 60 * 1000, // 15 minutes
    ...options,
  });
};

/**
 * Hook to fetch a specific dataset
 */
export const useDataset = (
  datasetId: string,
  options?: UseQueryOptions<Dataset>
) => {
  return useQuery({
    queryKey: budgetQueryKeys.dataset(datasetId),
    queryFn: () => api.datasets.getById(datasetId),
    enabled: !!datasetId,
    staleTime: 10 * 60 * 1000, // 10 minutes
    ...options,
  });
};

/**
 * Hook to get default budget dashboard data (summary + trends)
 */
export const useBudgetDashboard = (fiscalYear?: string) => {
  const summary = useBudgetSummary(fiscalYear);
  const trends = useBudgetTrends('portfolio', 'Health and Aged Care');
  const datasets = useDatasets();

  return {
    summary,
    trends,
    datasets,
    isLoading: summary.isLoading || trends.isLoading,
    isError: summary.isError || trends.isError,
    error: summary.error || trends.error,
  };
};