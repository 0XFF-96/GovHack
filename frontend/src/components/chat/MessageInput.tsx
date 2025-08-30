import React, { useState, useRef, useEffect } from 'react';
import { Input, Button, Space, Tooltip } from 'antd';
import { SendOutlined, LoadingOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';

const { TextArea } = Input;

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  loading?: boolean;
  placeholder?: string;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  disabled = false,
  loading = false,
  placeholder = 'Please enter your question...',
}) => {
  const [message, setMessage] = useState('');
  const [rows, setRows] = useState(1);
  const textAreaRef = useRef<any>(null);

  const handleSend = () => {
    const trimmedMessage = message.trim();
    if (trimmedMessage && !loading && !disabled) {
      onSendMessage(trimmedMessage);
      setMessage('');
      setRows(1);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setMessage(value);
    
    // Auto-resize logic
    const lines = value.split('\n');
    const newRows = Math.min(Math.max(lines.length, 1), 4);
    setRows(newRows);
  };

  // Focus on input when loading finishes
  useEffect(() => {
    if (!loading && textAreaRef.current) {
      textAreaRef.current.focus();
    }
  }, [loading]);

  const canSend = message.trim().length > 0 && !loading && !disabled;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="bg-white border-t border-gray-200 p-4"
    >
      {/* Quick Suggestions */}
      <div className="mb-3">
        <div className="flex flex-wrap gap-2">
          {[
            'Show Department of Education 2024 budget',
            'Compare departmental expenditures', 
            'Query healthcare-related expenditures'
          ].map((suggestion, index) => (
            <motion.button
              key={index}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => !loading && !disabled && setMessage(suggestion)}
              className={`
                px-3 py-1 text-xs rounded-full border transition-colors
                ${loading || disabled 
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed border-gray-200'
                  : 'bg-gray-50 text-gray-700 border-gray-300 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-700 cursor-pointer'
                }
              `}
              disabled={loading || disabled}
            >
              {suggestion}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Input Area */}
      <div className="flex items-end space-x-3">
        <div className="flex-1">
          <TextArea
            ref={textAreaRef}
            value={message}
            onChange={handleChange}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            autoSize={{ minRows: 1, maxRows: 4 }}
            disabled={disabled}
            className={`
              resize-none border-gray-300 rounded-lg
              ${disabled ? 'bg-gray-50' : 'bg-white'}
              focus:border-blue-600 focus:shadow-sm
            `}
            style={{ paddingRight: '12px' }}
          />
        </div>
        
        <Tooltip title={canSend ? 'Send message (Enter)' : 'Please enter message content'}>
          <Button
            type="primary"
            icon={loading ? <LoadingOutlined /> : <SendOutlined />}
            onClick={handleSend}
            disabled={!canSend}
            loading={loading}
            size="large"
            className={`
              flex items-center justify-center h-10 w-10
              ${canSend 
                ? 'bg-blue-600 hover:bg-blue-700 border-blue-600 hover:border-blue-700' 
                : ''
              }
            `}
          />
        </Tooltip>
      </div>

      {/* Input Help Text */}
      <div className="mt-2 text-xs text-gray-500">
        Press Enter to send, Shift + Enter for new line
      </div>
    </motion.div>
  );
};