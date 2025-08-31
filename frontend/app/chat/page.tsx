'use client';

import { AIGovChatbot } from '../../components/chat/ai-gov-chatbot';
import { BudgetLayout } from '../../components/layout/budget-layout';

export default function ChatPage() {
  return (
    <BudgetLayout>
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto py-8 px-6">
          <div className="max-w-4xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold tracking-tight mb-3 text-gray-900">
                🤖 AI Government Assistant
              </h1>
              <p className="text-lg text-gray-600 leading-relaxed">
                Ask questions about Australian government budgets, departments, and policies. 
                Get accurate, trustworthy answers powered by our hybrid AI system.
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                  💬 Natural Language
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                  🧠 Smart Routing
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                  📊 Evidence Package
                </span>
              </div>
            </div>
            
            <AIGovChatbot />
          </div>
        </div>
      </div>
    </BudgetLayout>
  );
}