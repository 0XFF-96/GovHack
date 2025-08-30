'use client';

import { AIGovChatbot } from '../../components/chat/ai-gov-chatbot';

export default function ChatPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-6">
            <h1 className="text-3xl font-bold tracking-tight mb-2">
              AI Government Assistant
            </h1>
            <p className="text-muted-foreground">
              Ask questions about Australian government budgets, departments, and policies. 
              Get accurate, trustworthy answers powered by Google Gemini AI.
            </p>
          </div>
          
          <AIGovChatbot />
        </div>
      </div>
    </div>
  );
}