import React, { useState, useEffect, useRef } from 'react';
import { message as antdMessage } from 'antd';
import { AnimatePresence, motion } from 'framer-motion';

// Components
import { MessageBubble } from './MessageBubble';
import { MessageInput } from './MessageInput';
import { TypingIndicator } from './TypingIndicator';

// API and Types
import { chatApi } from '../../services/api';
import type { ChatMessage, ChatQueryResponse } from '../../types/api';

interface ChatInterfaceProps {
  className?: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ className = '' }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom when new messages are added
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Handle sending a new message
  const handleSendMessage = async (messageText: string) => {
    if (!messageText.trim() || isLoading) return;

    try {
      setIsLoading(true);
      setError(null);

      // Prepare the API request
      const queryRequest = {
        query: messageText,
        session_id: currentSessionId || undefined,
      };

      // Call the chat API
      const response: ChatQueryResponse = await chatApi.sendQuery(queryRequest);

      // Update session ID if this is the first message
      if (!currentSessionId) {
        setCurrentSessionId(response.session_id);
      }

      // Add both user and assistant messages to the state
      setMessages(prev => [
        ...prev,
        response.user_message,
        response.assistant_message,
      ]);

    } catch (error: any) {
      console.error('Error sending message:', error);
      setError('Failed to send message, please try again later');
      antdMessage.error('Failed to send message, please try again later');
    } finally {
      setIsLoading(false);
    }
  };

  // Welcome message
  const welcomeMessage = {
    id: 0,
    message_type: 'assistant' as const,
    content: 'Hello! I am the GovHack AI assistant, and I can help you query Australian government budget data.\n\nYou can ask me about:\n• Budget situation of specific departments\n• Expenditure comparisons across different years\n• Funding allocation for specific projects\n• Budget trend analysis\n\nFeel free to ask me anything!',
    timestamp: new Date().toISOString(),
    trust_score: null,
    metadata: {},
    context: null,
  };

  const hasMessages = messages.length > 0;
  const displayMessages = hasMessages ? messages : [welcomeMessage];

  return (
    <div className={`h-full flex flex-col bg-gray-50 ${className}`}>
      {/* Messages Area */}
      <div 
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-4"
        style={{ maxHeight: 'calc(100vh - 300px)' }}
      >
        <AnimatePresence>
          {displayMessages.map((message, index) => (
            <MessageBubble
              key={`${message.id}-${index}`}
              message={message}
              isLatest={index === displayMessages.length - 1}
            />
          ))}
          
          {/* Typing Indicator */}
          {isLoading && <TypingIndicator />}
        </AnimatePresence>
        
        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Error Message */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mx-4 mb-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm"
        >
          {error}
        </motion.div>
      )}

      {/* Input Area */}
      <MessageInput
        onSendMessage={handleSendMessage}
        loading={isLoading}
        placeholder="Please enter your question about government budget..."
      />

      {/* Session Info */}
      {currentSessionId && (
        <div className="px-4 py-2 bg-gray-100 border-t border-gray-200">
          <div className="text-xs text-gray-600">
            Session ID: {currentSessionId.slice(0, 8)}... | Messages: {messages.length}
          </div>
        </div>
      )}
    </div>
  );
};