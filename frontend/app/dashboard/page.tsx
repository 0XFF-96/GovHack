'use client';

import React, { useState } from 'react';
import { BudgetLayout } from '@/components/layout/budget-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  DollarSign, 
  TrendingUp, 
  TrendingDown, 
  Building2, 
  FileText, 
  AlertCircle,
  BarChart3,
  PieChart,
  Activity
} from 'lucide-react';
import { useBudgetDashboard } from '@/hooks/use-budget-data';
import { BudgetChart } from '@/components/budget-chart';
import { StatsCard } from '@/components/stats-card';
import { ChatSidebar } from '@/components/chat/chat-sidebar';

export default function DashboardPage() {
  const { summary, trends, datasets, isLoading, isError, error } = useBudgetDashboard('2024-25');
  const [isChatOpen, setIsChatOpen] = useState(false);

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  if (isError) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Alert className="max-w-md">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Error loading dashboard data: {error?.message || 'Unknown error'}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <BudgetLayout>
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      {/* Header */}
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Budget Dashboard</h2>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="flex items-center gap-1">
            <Activity className="h-3 w-3" />
            {isLoading ? 'Loading...' : 'Live Data'}
          </Badge>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Budget"
          value={summary.data?.total_budget}
          icon={<DollarSign className="h-4 w-4 text-muted-foreground" />}
          format="currency"
          loading={summary.isLoading}
        />
        <StatsCard
          title="Portfolios"
          value={summary.data?.portfolio_count}
          icon={<Building2 className="h-4 w-4 text-muted-foreground" />}
          loading={summary.isLoading}
        />
        <StatsCard
          title="Departments"
          value={summary.data?.department_count}
          icon={<TrendingDown className="h-4 w-4 text-muted-foreground" />}
          loading={summary.isLoading}
        />
        <StatsCard
          title="Data Sources"
          value={datasets.data?.datasets?.length}
          icon={<FileText className="h-4 w-4 text-muted-foreground" />}
          loading={datasets.isLoading}
        />
      </div>

      {/* Charts Section */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {/* Budget Trends */}
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Budget Trends (2020-2024)
            </CardTitle>
            <CardDescription>
              Total budget allocation over the past 5 years
            </CardDescription>
          </CardHeader>
          <CardContent className="pl-2">
            {trends.isLoading ? (
              <Skeleton className="h-[300px] w-full" />
            ) : (
              <BudgetChart 
                data={trends.data?.trend_data || []} 
                type="line" 
                height={300}
                dataKey="total_amount"
                xAxisKey="fiscal_year"
              />
            )}
          </CardContent>
        </Card>

        {/* Top Departments */}
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="h-5 w-5" />
              Top Portfolios
            </CardTitle>
            <CardDescription>
              Budget allocation by portfolio (2024-25)
            </CardDescription>
          </CardHeader>
          <CardContent>
            {summary.isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Skeleton key={i} className="h-8 w-full" />
                ))}
              </div>
            ) : (
              <div className="space-y-3">
                {summary.data?.top_portfolios?.slice(0, 5).map((portfolio, index) => (
                  <div key={portfolio.name} className="flex items-center">
                    <div className="flex items-center space-x-2 flex-1">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-xs font-medium">
                        {index + 1}
                      </div>
                      <div className="grid gap-1">
                        <p className="text-sm font-medium leading-none">
                          {portfolio.name}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Portfolio
                        </p>
                      </div>
                    </div>
                    <div className="text-sm font-medium">
                      ${(portfolio.amount / 1000000000).toFixed(1)}B
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Department Comparison Chart */}
      <div className="grid gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              Portfolio Budget Comparison
            </CardTitle>
            <CardDescription>
              Compare budget allocations across government portfolios
            </CardDescription>
          </CardHeader>
          <CardContent>
            {summary.isLoading ? (
              <Skeleton className="h-[400px] w-full" />
            ) : (
              <BudgetChart 
                data={summary.data?.top_portfolios || []} 
                type="bar" 
                height={400}
                dataKey="amount"
                xAxisKey="name"
              />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Data Sources Overview */}
      <div className="grid gap-4 md:grid-cols-3">
        {datasets.data?.datasets?.slice(0, 3).map((dataset) => (
          <Card key={dataset.id}>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">{dataset.name}</CardTitle>
              <CardDescription className="text-xs">
                {dataset.description}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <Badge variant="default">
                    Active
                  </Badge>
                  {dataset.portfolios && (
                    <span className="text-xs text-muted-foreground">
                      {dataset.portfolios} portfolios
                    </span>
                  )}
                </div>
                <span className="text-muted-foreground">
                  {dataset.record_count?.toLocaleString()} records
                </span>
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                Updated: {new Date(dataset.last_updated).toLocaleDateString()}
              </div>
            </CardContent>
          </Card>
        ))}
        </div>
      </div>

      {/* Chat Sidebar */}
      <ChatSidebar 
        isOpen={isChatOpen} 
        onToggle={toggleChat}
      />
    </BudgetLayout>
  );
}
