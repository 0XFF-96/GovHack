'use client';

import { BudgetLayout } from '../../components/layout/budget-layout';
import { SmartQueryInterface } from '../../components/query/smart-query-interface';

export default function QueryPage() {
  return (
    <BudgetLayout>
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto py-8 px-6">
          <div className="max-w-7xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold tracking-tight mb-3 text-gray-900">
                🔍 Smart Government Data Query
              </h1>
              <p className="text-lg text-gray-600 leading-relaxed">
                Intelligent routing system that automatically determines the best approach for your government data queries.
                Get comprehensive results with full transparency and audit trails.
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                  🟢 SQL: Numerical Analysis
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                  🟡 RAG: Document Retrieval
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                  🔵 Hybrid: Combined Analysis
                </span>
              </div>
            </div>
            
            <SmartQueryInterface />
          </div>
        </div>
      </div>
    </BudgetLayout>
  );
}
