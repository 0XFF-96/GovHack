'use client';

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  Legend,
  Area,
  AreaChart,
} from 'recharts';

interface BudgetChartProps {
  data: any[];
  type: 'bar' | 'line' | 'pie' | 'area';
  height?: number;
  dataKey: string;
  xAxisKey?: string;
  colors?: string[];
  title?: string;
}

const DEFAULT_COLORS = [
  '#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8',
  '#82CA9D', '#FFC658', '#FF7C7C', '#8DD1E1', '#D084D0'
];

const formatCurrency = (value: number) => {
  if (value >= 1000000000) {
    return `$${(value / 1000000000).toFixed(1)}B`;
  }
  if (value >= 1000000) {
    return `$${(value / 1000000).toFixed(1)}M`;
  }
  if (value >= 1000) {
    return `$${(value / 1000).toFixed(1)}K`;
  }
  return `$${value}`;
};

const formatNumber = (value: number) => {
  return value.toLocaleString();
};

const CustomTooltip = ({ active, payload, label, dataKey }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
        <p className="text-sm font-medium text-gray-900">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            {`${entry.name}: ${typeof entry.value === 'number' && dataKey === 'amount' 
              ? formatCurrency(entry.value) 
              : formatNumber(entry.value)}`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export const BudgetChart: React.FC<BudgetChartProps> = ({
  data,
  type,
  height = 300,
  dataKey,
  xAxisKey,
  colors = DEFAULT_COLORS,
  title,
}) => {
  if (!data || data.length === 0) {
    return (
      <div 
        className="flex items-center justify-center text-gray-500" 
        style={{ height }}
      >
        No data available
      </div>
    );
  }

  const renderChart = () => {
    switch (type) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey={xAxisKey || 'name'} 
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                tickFormatter={dataKey === 'amount' ? formatCurrency : formatNumber}
              />
              <Tooltip content={<CustomTooltip dataKey={dataKey} />} />
              <Bar dataKey={dataKey} fill={colors[0]} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey={xAxisKey || 'name'} 
                tick={{ fontSize: 12 }}
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                tickFormatter={dataKey === 'amount' ? formatCurrency : formatNumber}
              />
              <Tooltip content={<CustomTooltip dataKey={dataKey} />} />
              <Line 
                type="monotone" 
                dataKey={dataKey} 
                stroke={colors[0]} 
                strokeWidth={3}
                dot={{ fill: colors[0], strokeWidth: 2, r: 6 }}
                activeDot={{ r: 8 }}
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'area':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey={xAxisKey || 'name'} 
                tick={{ fontSize: 12 }}
              />
              <YAxis 
                tick={{ fontSize: 12 }}
                tickFormatter={dataKey === 'amount' ? formatCurrency : formatNumber}
              />
              <Tooltip content={<CustomTooltip dataKey={dataKey} />} />
              <Area 
                type="monotone" 
                dataKey={dataKey} 
                stroke={colors[0]} 
                fill={colors[0]}
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        );

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={height}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey={dataKey}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value: any) => [
                  dataKey === 'amount' ? formatCurrency(value) : formatNumber(value), 
                  'Value'
                ]}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        );

      default:
        return null;
    }
  };

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-lg font-medium mb-4 text-gray-900">{title}</h3>
      )}
      {renderChart()}
    </div>
  );
};