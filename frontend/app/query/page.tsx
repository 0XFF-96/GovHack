'use client';

import { BudgetLayout } from '@/components/layout/budget-layout';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { api } from '@/lib/api';
import { useMutation } from '@tanstack/react-query';
import {
    CheckCircle,
    Code,
    Copy,
    Database,
    History,
    Loader2,
    Mic,
    Search,
    Settings
} from 'lucide-react';
import React, { useState } from 'react';

interface QueryResult {
  answer: string;
  confidence: number;
  method: 'SQL' | 'RAG';
  executedQuery?: string;
  dataSources: string[];
  metadata: {
    rows: number;
    timestamp: string;
    auditId: string;
  };
  tableData?: Array<{ [key: string]: any }>;
  summary?: {
    totalAmount: number;
    breakdown: Array<{ department: string; amount: number; percentage: number }>;
  };
}

interface RecentQuery {
  id: string;
  query: string;
  method: 'SQL' | 'RAG';
  timestamp: string;
}

export default function QueryPage() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<QueryResult | null>(null);
  const [recentQueries] = useState<RecentQuery[]>([
    { id: '1', query: 'What is the total budget for education?', method: 'SQL', timestamp: '2 mins ago' },
    { id: '2', query: "Find details about John Smith's employment record", method: 'RAG', timestamp: '5 mins ago' },
    { id: '3', query: 'Average salary by department', method: 'SQL', timestamp: '12 mins ago' },
    { id: '4', query: 'Show top 10 highest expenses', method: 'SQL', timestamp: '1 hour ago' },
  ]);

  const queryMutation = useMutation({
    mutationFn: async (queryText: string) => {
      // 调用后端AI查询接口
      return api.chat.sendMessage(queryText);
    },
    onSuccess: (data) => {
      try {
        // 解析后端返回的AI结果
        let aiResponse;
        if (data.assistant_message?.content) {
          try {
            aiResponse = JSON.parse(data.assistant_message.content);
          } catch {
            // 如果不是JSON格式，使用原始内容
            aiResponse = {
              answer: data.assistant_message.content,
              method: 'RAG',
              confidence: data.trust_score || 0.5
            };
          }
        }

        const result: QueryResult = {
          answer: aiResponse?.answer || query,
          confidence: aiResponse?.confidence || data.trust_score || 0.5,
          method: aiResponse?.method || 'SQL',
          executedQuery: aiResponse?.executed_query,
          dataSources: aiResponse?.data_sources || ['government_datasets'],
          metadata: {
            rows: aiResponse?.metadata?.rows || 0,
            timestamp: aiResponse?.metadata?.timestamp || new Date().toISOString(),
            auditId: aiResponse?.metadata?.audit_id || `AUD-${Date.now()}`
          },
          tableData: aiResponse?.table_data || [],
          summary: aiResponse?.summary || { totalAmount: 0, breakdown: [] }
        };
        
        setResult(result);
      } catch (error) {
        console.error('Error processing AI response:', error);
        // 回退到基础响应
        setResult({
          answer: query,
          confidence: 0.3,
          method: 'SQL',
          dataSources: ['error_fallback'],
          metadata: {
            rows: 0,
            timestamp: new Date().toISOString(),
            auditId: `ERR-${Date.now()}`
          }
        });
      }
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      queryMutation.mutate(query.trim());
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <BudgetLayout>
      <div className="flex h-[calc(100vh-4rem)]">
        {/* Left Sidebar */}
        <div className="w-80 border-r bg-gray-50 p-4 space-y-4">
          {/* Navigation */}
          <div className="space-y-2">
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
          </div>

          <Separator />

          {/* Recent Queries */}
          <div>
            <h3 className="font-medium text-sm text-gray-700 mb-3">Recent Queries</h3>
            <div className="space-y-2">
              {recentQueries.map((item) => (
                <div
                  key={item.id}
                  className="p-3 bg-white rounded border hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => setQuery(item.query)}
                >
                  <div className="text-sm font-medium text-gray-900 mb-1">
                    {item.query}
                  </div>
                  <div className="flex items-center justify-between">
                    <Badge variant={item.method === 'SQL' ? 'default' : 'secondary'} className="text-xs">
                      {item.method}
                    </Badge>
                    <span className="text-xs text-gray-500">{item.timestamp}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex">
          {/* Query Interface */}
          <div className="flex-1 p-6">
            {/* Header */}
            <div className="mb-6">
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Ask a question about government data
              </h1>
              
              {/* Query Input */}
              <form onSubmit={handleSubmit} className="flex gap-2 mb-4">
                <div className="flex-1 relative">
                  <Input
                    placeholder="e.g., What is the total education budget for 2024?"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="pr-10"
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
                  disabled={!query.trim() || queryMutation.isPending}
                  className="px-6"
                >
                  {queryMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <Search className="h-4 w-4 mr-2" />
                  )}
                  Query
                </Button>
              </form>

              {/* Query Type Indicators */}
              <div className="flex gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  <span>SQL: total, sum, average, top, group, anomalies</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
                  <span>RAG: specific records, entities, details</span>
                </div>
              </div>
            </div>

            {/* Query Results */}
            {result && (
              <div className="space-y-6">
                {/* Result Header */}
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold">Query Results</h2>
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant={result.method === 'SQL' ? 'default' : 'secondary'}
                      className="flex items-center gap-1"
                    >
                      {result.method} Path
                    </Badge>
                    <Badge variant="outline" className="flex items-center gap-1">
                      <CheckCircle className="h-3 w-3" />
                      Confidence: {result.confidence}
                    </Badge>
                  </div>
                </div>

                <p className="text-gray-600">{result.answer}</p>

                {/* Main Result */}
                <Card>
                  <CardContent className="p-6">
                    <div className="text-center">
                      <div className="text-4xl font-bold text-blue-600 mb-2">
                        {formatCurrency(result.summary?.totalAmount || 0)}
                      </div>
                      <div className="text-gray-600">Total Education Budget for FY 2024</div>
                    </div>

                    {/* Breakdown Table */}
                    {result.tableData && (
                      <div className="mt-6">
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Department</TableHead>
                              <TableHead className="text-right">Amount</TableHead>
                              <TableHead className="text-right">Percentage</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {result.tableData.map((row, index) => (
                              <TableRow key={index}>
                                <TableCell className="font-medium">{row.department}</TableCell>
                                <TableCell className="text-right">
                                  {formatCurrency(row.amount)}
                                </TableCell>
                                <TableCell className="text-right">{row.percentage}%</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </div>
                    )}

                    {/* Metadata */}
                    <div className="mt-6 grid grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">847</div>
                        <div className="text-sm text-gray-600">Records Found</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">3</div>
                        <div className="text-sm text-gray-600">Data Sources</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-orange-600">v2.1</div>
                        <div className="text-sm text-gray-600">Schema Version</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-600">0.95</div>
                        <div className="text-sm text-gray-600">Confidence</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>

          {/* Right Panel - Evidence Package */}
          <div className="w-96 border-l bg-gray-50 p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-semibold">Evidence Package</h2>
              <Button variant="outline" size="sm">
                <Copy className="h-4 w-4 mr-1" />
                Copy
              </Button>
            </div>

            {result && (
              <div className="space-y-4">
                {/* Query Info */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Query:</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="text-sm text-gray-600">{result.answer}</p>
                  </CardContent>
                </Card>

                {/* Method */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Method:</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <Badge>{result.method}</Badge>
                  </CardContent>
                </Card>

                {/* Executed Query */}
                {result.executedQuery && (
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm flex items-center gap-1">
                        <Code className="h-4 w-4" />
                        Executed Query:
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <pre className="text-xs bg-gray-100 p-2 rounded overflow-x-auto">
                        {result.executedQuery}
                      </pre>
                    </CardContent>
                  </Card>
                )}

                {/* Data Sources */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Data Sources:</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <ul className="text-sm space-y-1">
                      {result.dataSources.map((source, index) => (
                        <li key={index} className="flex items-center gap-1">
                          <Database className="h-3 w-3" />
                          {source}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>

                {/* Metadata */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Metadata:</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0 space-y-2">
                    <div className="text-xs">
                      <span className="font-medium">Rows:</span> {result.metadata.rows}
                    </div>
                    <div className="text-xs">
                      <span className="font-medium">Confidence:</span> {result.confidence}
                    </div>
                    <div className="text-xs">
                      <span className="font-medium">Timestamp:</span> {result.metadata.timestamp}
                    </div>
                    <div className="text-xs">
                      <span className="font-medium">Audit ID:</span> {result.metadata.auditId}
                    </div>
                  </CardContent>
                </Card>

                {/* Answer Snapshot */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Answer Snapshot:</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <p className="text-sm font-medium">
                      {formatCurrency(result.summary?.totalAmount || 0)}
                    </p>
                  </CardContent>
                </Card>

                {/* Audit Trail */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Audit Trail</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-mono">{result.metadata.auditId}</span>
                      <span>{result.metadata.timestamp.split(' ')[1]}</span>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </div>
      </div>
    </BudgetLayout>
  );
}
