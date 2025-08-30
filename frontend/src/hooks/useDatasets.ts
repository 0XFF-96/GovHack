import { useState, useEffect } from 'react';
import { message } from 'antd';
import { datasetsApi } from '../services/api';
import type { Dataset } from '../types/api';

interface UseDatasetsReturn {
  datasets: Dataset[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export const useDatasets = (): UseDatasetsReturn => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await datasetsApi.getDatasets();
      setDatasets(response.datasets);
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || '获取数据集失败';
      setError(errorMessage);
      message.error(errorMessage);
      console.error('Error fetching datasets:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  return {
    datasets,
    loading,
    error,
    refetch: fetchDatasets,
  };
};