'use client';

import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Bot, User, Send, Loader2 } from 'lucide-react';
import { api } from '../../lib/api';

interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  trust_score?: number;
}

export function AIGovChatbot() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null); // Start with null, let backend create session

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: inputMessage,
      role: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const requestPayload: any = {
        query: inputMessage,
        context: {}
      };
      
      // Only include session_id if we have one (not for the first message)
      if (sessionId) {
        requestPayload.session_id = sessionId;
      }
      
      console.log('Sending request to API:');
      console.log('- URL: /api/v1/chat/query/');
      console.log('- Method: POST');
      console.log('- Request Object:', requestPayload);
      console.log('- Query value:', requestPayload.query);
      console.log('- Query type:', typeof requestPayload.query);
      console.log('- Session ID:', requestPayload.session_id || 'NOT_PROVIDED (new session)');
      
      const response = await api.chat.query(requestPayload);
      
      console.log('API Response:', response);

      // Store the session ID returned by the backend for subsequent messages
      if (!sessionId && response.session_id) {
        setSessionId(response.session_id);
        console.log('New session created:', response.session_id);
      }

      const assistantMessage: ChatMessage = {
        id: response.assistant_message.id.toString(),
        content: response.assistant_message.content,
        role: 'assistant',
        timestamp: response.assistant_message.timestamp,
        trust_score: response.trust_score
      };
      
      console.log('Processed assistant message:', assistantMessage);

      setMessages(prev => [...prev, assistantMessage]);

    } catch (err: any) {
      console.error('Chat error:', err);
      console.error('Error details:', {
        message: err.message,
        status: err.status,
        response: err.response?.data,
        config: err.config
      });
      
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        content: 'I apologize, but I encountered an error processing your request. Please try again.',
        role: 'assistant',
        timestamp: new Date().toISOString(),
        trust_score: 0.0
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-[600px] max-w-4xl mx-auto">
      <Card className="mb-4">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-blue-600" />
            Australian Government AI Assistant
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Ask questions about Australian government budgets, departments, and policies.
          </p>
        </CardHeader>
      </Card>

      <Card className="flex-1 flex flex-col">
        <div className="flex-1 p-4 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Bot className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">Welcome to GovHack AI Assistant</h3>
              <p className="text-muted-foreground mb-4 max-w-md">
                I can help you explore Australian government data, budgets, and policies.
              </p>
              <div className="space-y-2 text-sm text-muted-foreground">
                <p>• "What is the education department budget for 2024?"</p>
                <p>• "How much does health spending compare to defense?"</p>
                <p>• "Show me the largest government portfolios"</p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <Bot className="h-4 w-4 text-blue-600" />
                      </div>
                    </div>
                  )}
                  
                  <div className="max-w-[80%]">
                    <div
                      className={`p-3 rounded-lg ${
                        message.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    </div>
                    
                    {message.trust_score !== undefined && (
                      <div className="text-xs text-muted-foreground mt-1">
                        Trust Score: {(message.trust_score * 100).toFixed(0)}%
                      </div>
                    )}
                  </div>
                  
                  {message.role === 'user' && (
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                        <User className="h-4 w-4 text-white" />
                      </div>
                    </div>
                  )}
                </div>
              ))}
              
              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />
                    </div>
                  </div>
                  <div className="max-w-[80%]">
                    <div className="p-3 rounded-lg bg-gray-100">
                      <p className="text-muted-foreground">Processing your query...</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
        
        <div className="p-4 border-t">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about Australian government data..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button 
              type="submit"
              disabled={!inputMessage.trim() || isLoading}
              size="icon"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
          <p className="text-xs text-muted-foreground mt-2">
            Press Enter to send • Powered by Google Gemini AI
          </p>
        </div>
      </Card>
    </div>
  );
}