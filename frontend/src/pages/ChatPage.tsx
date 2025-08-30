import React from 'react';
import { Typography } from 'antd';
import { MessageOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';
import { ChatInterface } from '../components/chat/ChatInterface';

const { Title, Text } = Typography;

export const ChatPage: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="h-full flex flex-col"
    >
      {/* Page Header */}
      <div className="mb-6">
        <Title level={2} className="!mb-2 flex items-center">
          <MessageOutlined className="mr-3 text-blue-600" />
          Smart Chat Query
        </Title>
        <Text className="text-gray-600">
          Query Australian government budget data using natural language and get accurate, reliable answers
        </Text>
      </div>

      {/* Chat Interface */}
      <div className="flex-1 bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <ChatInterface />
      </div>
    </motion.div>
  );
};