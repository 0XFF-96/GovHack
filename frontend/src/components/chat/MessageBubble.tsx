import React from 'react';
import { Avatar, Typography, Space } from 'antd';
import { UserOutlined, RobotOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';
import { TrustScoreBadge } from './TrustScoreBadge';
import type { ChatMessage } from '../../types/api';

const { Text, Paragraph } = Typography;

interface MessageBubbleProps {
  message: ChatMessage;
  isLatest?: boolean;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isLatest = false }) => {
  const isUser = message.message_type === 'user';
  const hasGoodTrustScore = message.trust_score && message.trust_score >= 0.7;

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`flex w-full mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <Avatar
          size={40}
          className={`flex-shrink-0 ${isUser ? 'ml-3' : 'mr-3'}`}
          style={{
            backgroundColor: isUser ? '#0066CC' : '#52c41a',
          }}
          icon={isUser ? <UserOutlined /> : <RobotOutlined />}
        />

        {/* Message Content */}
        <div
          className={`
            relative p-4 rounded-2xl shadow-sm
            ${isUser 
              ? 'bg-blue-600 text-white' 
              : 'bg-white border border-gray-200'
            }
          `}
        >
          {/* Message Text */}
          <div className={`${isUser ? 'text-white' : 'text-gray-900'}`}>
            {message.content.split('\n').map((line, index) => (
              <Paragraph
                key={index}
                className={`!mb-2 last:!mb-0 ${isUser ? '!text-white' : '!text-gray-900'}`}
                style={{ color: isUser ? '#ffffff' : '#1f2937' }}
              >
                {line}
              </Paragraph>
            ))}
          </div>

          {/* Message Footer */}
          <div className={`flex items-center justify-between mt-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
            {/* Timestamp */}
            <Space className={`text-xs ${isUser ? 'text-blue-100' : 'text-gray-500'}`}>
              <ClockCircleOutlined />
              <span>{formatTimestamp(message.timestamp)}</span>
            </Space>

            {/* Trust Score (only for assistant messages) */}
            {!isUser && message.trust_score && (
              <TrustScoreBadge score={message.trust_score} size="small" />
            )}
          </div>

          {/* Processing Info (only for assistant messages) */}
          {!isUser && message.context && (
            <div className="mt-3 p-2 bg-gray-50 rounded-lg">
              <div className="flex flex-wrap gap-2 text-xs text-gray-600">
                <span>处理时间: {message.context.processing_time}s</span>
                <span>•</span>
                <span>意图: {message.context.intent}</span>
                {message.context.data_sources.length > 0 && (
                  <>
                    <span>•</span>
                    <span>数据源: {message.context.data_sources.join(', ')}</span>
                  </>
                )}
              </div>
            </div>
          )}

          {/* Message Tail */}
          <div
            className={`
              absolute top-4 w-3 h-3 transform rotate-45
              ${isUser 
                ? 'bg-blue-600 -right-1.5' 
                : 'bg-white border-l border-t border-gray-200 -left-1.5'
              }
            `}
          />
        </div>
      </div>
    </motion.div>
  );
};