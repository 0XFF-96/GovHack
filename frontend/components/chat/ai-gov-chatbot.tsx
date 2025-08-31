'use client';

import { Bot, Loader2, Send, User } from 'lucide-react';
import React, { useState } from 'react';
import { api } from '../../lib/api';
import { Button } from '../ui/button';
import { Card, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';

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
      const response = await api.chat.sendMessage(inputMessage, sessionId || undefined, {});
      
      console.log('API Response:', response);

      // Store the session ID returned by the backend for subsequent messages
      if (!sessionId && response.session_id) {
        setSessionId(response.session_id);
        console.log('New session created:', response.session_id);
      }

      const assistantMessage: ChatMessage = {
        id: response.assistant_message?.id?.toString() || Date.now().toString(),
        content: response.assistant_message?.content || 'No response content',
        role: 'assistant',
        timestamp: response.assistant_message?.timestamp || new Date().toISOString(),
        trust_score: response.trust_score || 0.5
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
    <div className="flex flex-col h-[700px] max-w-4xl mx-auto">
      <Card className="mb-4">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-blue-600" />
            Hybrid AI Government Assistant
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Smart routing between SQL queries and RAG retrieval for comprehensive government data analysis.
          </p>
        </CardHeader>
      </Card>

      <Card className="flex-1 flex flex-col">
        <div className="flex-1 p-4 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Bot className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">Welcome to GovHack Hybrid AI Assistant</h3>
              <p className="text-muted-foreground mb-4 max-w-md">
                I can help you explore Australian government data using intelligent routing between statistical analysis and document retrieval.
              </p>
              <div className="space-y-2 text-sm text-muted-foreground">
                <p>• "What is the education department budget for 2024?" (SQL)</p>
                <p>• "Find details about Supplier Company 1" (RAG)</p>
                <p>• "Show me budget summary and employee records" (Hybrid)</p>
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
            Press Enter to send • Powered by Hybrid AI System (SQL + RAG)
          </p>
        </div>
      </Card>
    </div>
  );
}