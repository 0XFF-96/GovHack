'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

interface StatsCardProps {
  title: string;
  value?: number;
  icon?: React.ReactNode;
  format?: 'currency' | 'number' | 'percentage';
  loading?: boolean;
  subtitle?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

const formatValue = (value: number, format?: string) => {
  switch (format) {
    case 'currency':
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
    
    case 'percentage':
      return `${value.toFixed(1)}%`;
    
    case 'number':
    default:
      return value.toLocaleString();
  }
};

export const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  icon,
  format,
  loading = false,
  subtitle,
  trend,
}) => {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          {title}
        </CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-2">
            <Skeleton className="h-8 w-[100px]" />
            {subtitle && <Skeleton className="h-4 w-[80px]" />}
          </div>
        ) : (
          <>
            <div className="text-2xl font-bold">
              {value !== undefined ? formatValue(value, format) : 'N/A'}
            </div>
            {subtitle && (
              <p className="text-xs text-muted-foreground">
                {subtitle}
              </p>
            )}
            {trend && (
              <div className={`flex items-center text-xs ${
                trend.isPositive ? 'text-green-600' : 'text-red-600'
              }`}>
                <span>
                  {trend.isPositive ? '↗' : '↘'} {Math.abs(trend.value)}%
                </span>
                <span className="text-muted-foreground ml-1">vs last period</span>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
};