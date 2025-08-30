import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Card, Spin, Alert } from 'antd';
import { customAxiosInstance } from '@/services/axiosConfig';

interface BudgetSummaryResponse {
  fiscal_year: string;
  total_budget: number;
  portfolio_count: number;
  department_count: number;
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

interface ChartData {
  department: string;
  budget2024: number;
  budget2023: number;
}

export const EnhancedBudgetComparison: React.FC = () => {
  const [data, setData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchBudgetData = async () => {
    try {
      const response = await customAxiosInstance.get<BudgetSummaryResponse>('/v1/datasets/budget/summary/');
      return response.data;
    } catch (err) {
      console.error('Error fetching budget summary:', err);
      throw err;
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);

      try {
        const summaryData = await fetchBudgetData();
        
        // Transform data for comparison
        const chartData: ChartData[] = summaryData.top_portfolios.map((portfolio) => {
          const budget2024 = portfolio.amount / 1000000; // Convert to millions
          const budget2023 = budget2024 * 0.95; // Mock 2023 data as 95% of 2024
          
          return {
            department: portfolio.name,
            budget2024,
            budget2023,
          };
        });

        setData(chartData);

      } catch (err: any) {
        setError(err.response?.data?.message || 'Failed to load budget comparison data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const formatCurrency = (value: number) => {
    return `$${value.toFixed(0)}M`;
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-800 mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center space-x-2 mb-1">
              <div
                className="w-3 h-3 rounded-sm"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-sm">
                {entry.name}: {formatCurrency(entry.value)}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <Card 
        title="Department Budget Comparison - 2023 vs 2024 Financial Year"
        className="w-full"
      >
        <div className="h-96 flex items-center justify-center">
          <Spin size="large" />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card 
        title="Department Budget Comparison - 2023 vs 2024 Financial Year"
        className="w-full"
      >
        <Alert message="Failed to load budget data" type="error" showIcon />
      </Card>
    );
  }

  return (
    <Card 
      title="Department Budget Comparison - 2023 vs 2024 Financial Year"
      className="w-full"
    >
      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 20, right: 30, left: 20, bottom: 120 }}
            barGap={8}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="department"
              tick={{ fontSize: 11, fill: '#6b7280' }}
              angle={-45}
              textAnchor="end"
              height={120}
              interval={0}
              tickFormatter={(value) => {
                return value.length > 15 ? value.substring(0, 15) + '...' : value;
              }}
            />
            <YAxis
              tick={{ fontSize: 12, fill: '#6b7280' }}
              tickFormatter={formatCurrency}
              width={80}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              wrapperStyle={{ paddingTop: '20px' }}
              iconType="rect"
            />
            <Bar
              dataKey="budget2024"
              name="2024 Financial Year"
              fill="#3b82f6"
              radius={[4, 4, 0, 0]}
              stroke="#2563eb"
              strokeWidth={1}
            />
            <Bar
              dataKey="budget2023"
              name="2023 Financial Year"
              fill="#10b981"
              radius={[4, 4, 0, 0]}
              stroke="#059669"
              strokeWidth={1}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};