'use client';

import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { 
  Search, 
  Database, 
  History, 
  Settings, 
  Copy, 
  Code, 
  CheckCircle, 
  Loader2,
  Mic,
  BarChart3,
  FileText,
  TrendingUp
} from 'lucide-react';
import { api } from '../../lib/api';

interface QueryResult {
  success: boolean;
  method: 'SQL' | 'RAG' | 'HYBRID';
  query: string;
  result: any;
  evidence_package: any;
  audit_info: any;
  confidence_score: number;
  processing_time: number;
}

interface RecentQuery {
  id: string;
  query: string;
  method: 'SQL' | 'RAG' | 'HYBRID';
  timestamp: string;
  confidence: number;
}

export function SmartQueryInterface() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<QueryResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [recentQueries, setRecentQueries] = useState<RecentQuery[]>([]);
  const [methodPreference, setMethodPreference] = useState<'auto' | 'sql' | 'rag'>('auto');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/data-processing/smart-query/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          context: {},
          method_preference: methodPreference
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);

      // 添加到最近查询
      const newQuery: RecentQuery = {
        id: Date.now().toString(),
        query: query.trim(),
        method: data.method,
        timestamp: 'Just now',
        confidence: data.confidence_score
      };
      setRecentQueries(prev => [newQuery, ...prev.slice(0, 9)]); // 保持最多10条

    } catch (error) {
      console.error('Query error:', error);
      setResult({
        success: false,
        method: 'SQL',
        query: query.trim(),
        result: null,
        evidence_package: null,
        audit_info: null,
        confidence_score: 0,
        processing_time: 0
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'AUD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getMethodColor = (method: string) => {
    switch (method) {
      case 'SQL': return 'bg-green-100 text-green-800';
      case 'RAG': return 'bg-yellow-100 text-yellow-800';
      case 'HYBRID': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getMethodIcon = (method: string) => {
    switch (method) {
      case 'SQL': return <BarChart3 className="h-4 w-4" />;
      case 'RAG': return <FileText className="h-4 w-4" />;
      case 'HYBRID': return <TrendingUp className="h-4 w-4" />;
      default: return <Search className="h-4 w-4" />;
    }
  };

  return (
    <div className="flex h-[calc(100vh-12rem)] gap-6">
      {/* Left Sidebar */}
      <div className="w-80 space-y-6">
        {/* Navigation */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Navigation</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button variant="default" className="w-full justify-start">
              <Search className="h-4 w-4 mr-2" />
              Query Interface
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              <Database className="h-4 w-4 mr-2" />
              Data Sources
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              <History className="h-4 w-4 mr-2" />
              Audit Logs
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
          </CardContent>
        </Card>

        {/* Method Preference */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Query Method</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button
              variant={methodPreference === 'auto' ? 'default' : 'outline'}
              className="w-full justify-start"
              onClick={() => setMethodPreference('auto')}
            >
              <Search className="h-4 w-4 mr-2" />
              Auto (Recommended)
            </Button>
            <Button
              variant={methodPreference === 'sql' ? 'default' : 'outline'}
              className="w-full justify-start"
              onClick={() => setMethodPreference('sql')}
            >
              <BarChart3 className="h-4 w-4 mr-2" />
              SQL Analysis
            </Button>
            <Button
              variant={methodPreference === 'rag' ? 'default' : 'outline'}
              className="w-full justify-start"
              onClick={() => setMethodPreference('rag')}
            >
              <FileText className="h-4 w-4 mr-2" />
              RAG Retrieval
            </Button>
          </CardContent>
        </Card>

        {/* Recent Queries */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Recent Queries</CardTitle>
          </CardHeader>
          <CardContent>
            {recentQueries.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-4">
                No recent queries
              </p>
            ) : (
              <div className="space-y-2">
                {recentQueries.map((item) => (
                  <div
                    key={item.id}
                    className="p-3 bg-gray-50 rounded border hover:bg-gray-100 cursor-pointer transition-colors"
                    onClick={() => setQuery(item.query)}
                  >
                    <div className="text-sm font-medium text-gray-900 mb-2 line-clamp-2">
                      {item.query}
                    </div>
                    <div className="flex items-center justify-between">
                      <Badge className={`text-xs ${getMethodColor(item.method)}`}>
                        {getMethodIcon(item.method)}
                        <span className="ml-1">{item.method}</span>
                      </Badge>
                      <span className="text-xs text-gray-500">{item.timestamp}</span>
                    </div>
                    <div className="mt-1 text-xs text-gray-500">
                      Confidence: {(item.confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="flex-1 space-y-6">
        {/* Query Interface */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Ask a question about government data</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <Input
                    placeholder="e.g., What is the total education budget for 2024?"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="pr-10"
                    disabled={isLoading}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-2 top-1/2 transform -translate-y-1/2"
                  >
                    <Mic className="h-4 w-4" />
                  </Button>
                </div>
                <Button 
                  type="submit" 
                  disabled={!query.trim() || isLoading}
                  className="px-6"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <Search className="h-4 w-4 mr-2" />
                  )}
                  Query
                </Button>
              </div>

              {/* Query Type Indicators */}
              <div className="flex gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  <span>SQL: total, sum, average, top, group, anomalies</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
                  <span>RAG: specific records, entities, details</span>
                </div>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Query Results */}
        {result && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-xl">Query Results</CardTitle>
                <div className="flex items-center gap-2">
                  <Badge className={`${getMethodColor(result.method)}`}>
                    {getMethodIcon(result.method)}
                    <span className="ml-1">{result.method} Path</span>
                  </Badge>
                  <Badge variant="outline" className="flex items-center gap-1">
                    <CheckCircle className="h-3 w-3" />
                    Confidence: {(result.confidence_score * 100).toFixed(0)}%
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Result Summary */}
              {result.result && (
                <div className="space-y-4">
                  <div className="text-center p-6 bg-blue-50 rounded-lg">
                    <div className="text-3xl font-bold text-blue-600 mb-2">
                      {result.result.type === 'sql_analysis' && result.result.data?.total_budget
                        ? formatCurrency(result.result.data.total_budget)
                        : result.result.type === 'sql_analysis' && result.result.data?.total_amount
                        ? formatCurrency(result.result.data.total_amount)
                        : result.result.summary || 'Analysis Complete'}
                    </div>
                    <div className="text-gray-600">{result.result.summary}</div>
                  </div>

                  {/* Breakdown Table */}
                  {result.result.breakdown && result.result.breakdown.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold mb-3">Detailed Breakdown</h3>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Portfolio/Department</TableHead>
                            <TableHead className="text-right">Amount</TableHead>
                            <TableHead className="text-right">Percentage</TableHead>
                            <TableHead className="text-right">Programs</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {result.result.breakdown.map((item: any, index: number) => (
                            <TableRow key={index}>
                              <TableCell className="font-medium">
                                {item.portfolio || item.department || 'Unknown'}
                              </TableCell>
                              <TableCell className="text-right">
                                {formatCurrency(item.amount || item.average_amount || 0)}
                              </TableCell>
                              <TableCell className="text-right">
                                {item.percentage ? `${item.percentage}%` : '-'}
                              </TableCell>
                              <TableCell className="text-right">
                                {item.program_count || '-'}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  )}

                  {/* Metadata */}
                  <div className="grid grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {result.result.record_count || result.result.total_records || 0}
                      </div>
                      <div className="text-sm text-gray-600">Records Found</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {result.result.data_sources?.length || 0}
                      </div>
                      <div className="text-sm text-gray-600">Data Sources</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-600">
                        {result.processing_time?.toFixed(3) || '0.000'}s
                      </div>
                      <div className="text-sm text-gray-600">Processing Time</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {(result.confidence_score * 100).toFixed(0)}%
                      </div>
                      <div className="text-sm text-gray-600">Confidence</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Error State */}
              {!result.success && (
                <div className="text-center p-6 bg-red-50 rounded-lg">
                  <div className="text-red-600 font-medium">Query failed</div>
                  <div className="text-sm text-red-500 mt-1">Please try again or check your query</div>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      {/* Right Panel - Evidence Package */}
      <div className="w-96 space-y-6">
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Evidence Package</CardTitle>
              {result && (
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => handleCopy(JSON.stringify(result.evidence_package, null, 2))}
                >
                  <Copy className="h-4 w-4 mr-1" />
                  Copy
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {result && result.evidence_package ? (
              <div className="space-y-4">
                {/* Query Info */}
                <div className="space-y-2">
                  <div className="text-sm font-medium text-gray-700">Query:</div>
                  <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                    {result.evidence_package.query}
                  </div>
                </div>

                {/* Method */}
                <div className="space-y-2">
                  <div className="text-sm font-medium text-gray-700">Method:</div>
                  <Badge className={getMethodColor(result.evidence_package.method)}>
                    {result.evidence_package.method}
                  </Badge>
                </div>

                {/* SQL Query */}
                {result.evidence_package.sql_query && (
                  <div className="space-y-2">
                    <div className="text-sm font-medium text-gray-700 flex items-center gap-1">
                      <Code className="h-4 w-4" />
                      Executed Query:
                    </div>
                    <pre className="text-xs bg-gray-100 p-2 rounded overflow-x-auto">
                      {result.evidence_package.sql_query}
                    </pre>
                  </div>
                )}

                {/* Data Sources */}
                <div className="space-y-2">
                  <div className="text-sm font-medium text-gray-700">Data Sources:</div>
                  <ul className="text-sm space-y-1">
                    {result.evidence_package.data_sources?.map((source: string, index: number) => (
                      <li key={index} className="flex items-center gap-1">
                        <Database className="h-3 w-3" />
                        {source}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Metadata */}
                <div className="space-y-2">
                  <div className="text-sm font-medium text-gray-700">Metadata:</div>
                  <div className="space-y-1 text-xs">
                    <div><span className="font-medium">Rows:</span> {result.evidence_package.record_count}</div>
                    <div><span className="font-medium">Processing Time:</span> {result.processing_time?.toFixed(3)}s</div>
                    <div><span className="font-medium">Timestamp:</span> {formatTimestamp(result.evidence_package.timestamp)}</div>
                    <div><span className="font-medium">Audit ID:</span> {result.evidence_package.audit_id}</div>
                  </div>
                </div>

                {/* Result Summary */}
                <div className="space-y-2">
                  <div className="text-sm font-medium text-gray-700">Result Summary:</div>
                  <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                    {result.evidence_package.result_summary}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <FileText className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                <p>No evidence package available</p>
                <p className="text-sm">Run a query to see the evidence package</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Audit Log */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Audit Log</CardTitle>
          </CardHeader>
          <CardContent>
            {result && result.audit_info ? (
              <div className="space-y-3">
                <div className="text-xs space-y-1">
                  <div><span className="font-medium">Audit ID:</span> {result.audit_info.audit_id}</div>
                  <div><span className="font-medium">Method:</span> {result.audit_info.method}</div>
                  <div><span className="font-medium">Processing Time:</span> {result.audit_info.processing_time?.toFixed(3)}s</div>
                  <div><span className="font-medium">Data Sources:</span> {result.audit_info.data_sources?.length || 0}</div>
                  <div><span className="font-medium">Record Count:</span> {result.audit_info.record_count}</div>
                  <div><span className="font-medium">Timestamp:</span> {formatTimestamp(result.audit_info.timestamp)}</div>
                </div>
              </div>
            ) : (
              <div className="text-center py-6 text-gray-500">
                <History className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                <p className="text-sm">No audit information available</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
