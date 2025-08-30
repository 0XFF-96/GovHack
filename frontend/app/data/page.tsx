'use client';

import React, { useState } from 'react';
import { BudgetLayout } from '@/components/layout/budget-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  Database, 
  Search, 
  Download, 
  Filter, 
  RefreshCw, 
  AlertCircle,
  FileText,
  Building2,
  DollarSign
} from 'lucide-react';
import { useDatasets, useBudgetSearch } from '@/hooks/use-budget-data';
import type { DataSearchRequest } from '@/types/api';

export default function DataPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchFilters, setSearchFilters] = useState<DataSearchRequest>({
    query: '',
    filters: {},
    page: 1,
    page_size: 20,
  });
  
  const { data: datasets, isLoading: datasetsLoading, error: datasetsError } = useDatasets();
  const { data: searchResults, isLoading: searchLoading, error: searchError } = useBudgetSearch(
    searchFilters,
    { enabled: !!searchFilters.query || Object.keys(searchFilters.filters || {}).length > 0 }
  );

  const handleSearch = () => {
    setSearchFilters(prev => ({
      ...prev,
      query: searchQuery,
      page: 1,
    }));
  };

  const handleFilterChange = (key: string, value: string) => {
    setSearchFilters(prev => ({
      ...prev,
      filters: {
        ...prev.filters,
        [key]: value || undefined,
      },
      page: 1,
    }));
  };

  const handleExport = () => {
    // Implementation for data export
    alert('Export functionality will be implemented');
  };

  if (datasetsError) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Alert className="max-w-md">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Error loading datasets: {datasetsError?.message || 'Unknown error'}
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
        <h2 className="text-3xl font-bold tracking-tight">Data Management</h2>
        <div className="flex items-center space-x-2">
          <Button onClick={handleExport} variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export Data
          </Button>
          <Button 
            onClick={() => window.location.reload()} 
            variant="outline" 
            size="sm"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Search Budget Data
          </CardTitle>
          <CardDescription>
            Search across all government budget datasets with advanced filtering
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Search for departments, programs, or budget items..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1"
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button onClick={handleSearch}>
              <Search className="h-4 w-4 mr-2" />
              Search
            </Button>
          </div>

          {/* Filters */}
          <div className="grid gap-4 md:grid-cols-4">
            <Select onValueChange={(value) => handleFilterChange('fiscal_year', value === 'all' ? '' : value)}>
              <SelectTrigger>
                <SelectValue placeholder="Fiscal Year" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Years</SelectItem>
                <SelectItem value="2024-25">2024-25</SelectItem>
                <SelectItem value="2023-24">2023-24</SelectItem>
                <SelectItem value="2022-23">2022-23</SelectItem>
              </SelectContent>
            </Select>

            <Select onValueChange={(value) => handleFilterChange('department', value === 'all' ? '' : value)}>
              <SelectTrigger>
                <SelectValue placeholder="Department" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Departments</SelectItem>
                <SelectItem value="Education">Education</SelectItem>
                <SelectItem value="Health">Health</SelectItem>
                <SelectItem value="Defence">Defence</SelectItem>
                <SelectItem value="Treasury">Treasury</SelectItem>
              </SelectContent>
            </Select>

            <Input
              type="number"
              placeholder="Min Amount"
              onChange={(e) => handleFilterChange('amount_min', e.target.value)}
            />

            <Input
              type="number"
              placeholder="Max Amount"
              onChange={(e) => handleFilterChange('amount_max', e.target.value)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Available Datasets */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Available Datasets
          </CardTitle>
          <CardDescription>
            Government datasets available for analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          {datasetsLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center space-x-4 p-4 border rounded">
                  <Skeleton className="h-10 w-10" />
                  <div className="space-y-2 flex-1">
                    <Skeleton className="h-4 w-[200px]" />
                    <Skeleton className="h-3 w-[300px]" />
                  </div>
                  <Skeleton className="h-8 w-20" />
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {datasets?.datasets?.map((dataset) => (
                <div key={dataset.id} className="flex items-center space-x-4 p-4 border rounded hover:bg-gray-50">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                    <FileText className="h-5 w-5 text-primary" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium">{dataset.name}</h3>
                    <p className="text-sm text-gray-600">{dataset.description}</p>
                    <div className="flex items-center space-x-4 mt-1">
                      <span className="text-xs text-gray-500">
                        {dataset.record_count?.toLocaleString()} records
                      </span>
                      <span className="text-xs text-gray-500">
                        Updated: {new Date(dataset.last_updated).toLocaleDateString()}
                      </span>
                      {dataset.portfolios && (
                        <span className="text-xs text-gray-500">
                          {dataset.portfolios} portfolios
                        </span>
                      )}
                      {dataset.departments && (
                        <span className="text-xs text-gray-500">
                          {dataset.departments} departments
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant="default">
                      Active
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Search Results */}
      {(searchResults || searchLoading) && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Filter className="h-5 w-5" />
              Search Results
            </CardTitle>
            <CardDescription>
              {searchResults && `Found ${searchResults.count} records`}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {searchLoading ? (
              <div className="space-y-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : searchError ? (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  Error searching data: {searchError?.message || 'Unknown error'}
                </AlertDescription>
              </Alert>
            ) : (
              <>
                {/* Summary */}
                {searchResults?.summary && (
                  <div className="grid gap-4 md:grid-cols-3 mb-6">
                    <div className="flex items-center space-x-3 p-3 border rounded">
                      <DollarSign className="h-8 w-8 text-green-600" />
                      <div>
                        <p className="text-sm text-gray-600">Total Budget</p>
                        <p className="text-lg font-semibold">
                          ${(searchResults.summary.total_budget / 1000000000).toFixed(1)}B
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3 p-3 border rounded">
                      <Building2 className="h-8 w-8 text-blue-600" />
                      <div>
                        <p className="text-sm text-gray-600">Departments</p>
                        <p className="text-lg font-semibold">
                          {searchResults.summary.department_count}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3 p-3 border rounded">
                      <FileText className="h-8 w-8 text-purple-600" />
                      <div>
                        <p className="text-sm text-gray-600">Records</p>
                        <p className="text-lg font-semibold">
                          {searchResults.count.toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Results Table */}
                <div className="border rounded-lg overflow-hidden">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Portfolio</TableHead>
                        <TableHead>Department</TableHead>
                        <TableHead>Program</TableHead>
                        <TableHead>Expense Type</TableHead>
                        <TableHead className="text-right">Amount (2024-25)</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {searchResults?.results?.slice(0, 10).map((record) => (
                        <TableRow key={record.id}>
                          <TableCell className="font-medium">{record.portfolio}</TableCell>
                          <TableCell>{record.department}</TableCell>
                          <TableCell>{record.program}</TableCell>
                          <TableCell>
                            <Badge variant="outline">{record.expense_type}</Badge>
                          </TableCell>
                          <TableCell className="text-right font-medium">
                            ${(record.amount_2024_25 || 0).toLocaleString()}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>

                {searchResults && searchResults.count > 10 && (
                  <div className="flex justify-center mt-4">
                    <p className="text-sm text-gray-500">
                      Showing 10 of {searchResults.count} results
                    </p>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      )}
      </div>
    </BudgetLayout>
  );
}