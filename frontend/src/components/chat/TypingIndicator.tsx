import React from 'react';
import { Avatar } from 'antd';
import { RobotOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';

export const TypingIndicator: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="flex w-full mb-4 justify-start"
    >
      <div className="flex max-w-[80%]">
        {/* Avatar */}
        <Avatar
          size={40}
          className="flex-shrink-0 mr-3"
          style={{ backgroundColor: '#52c41a' }}
          icon={<RobotOutlined />}
        />

        {/* Typing Animation */}
        <div className="relative p-4 bg-white border border-gray-200 rounded-2xl shadow-sm">
          <div className="typing-indicator">
            <motion.span
              animate={{ scale: [1, 1.2, 1] }}
              transition={{
                duration: 0.6,
                repeat: Infinity,
                delay: 0,
              }}
              className="w-2 h-2 bg-gray-400 rounded-full inline-block"
            />
            <motion.span
              animate={{ scale: [1, 1.2, 1] }}
              transition={{
                duration: 0.6,
                repeat: Infinity,
                delay: 0.2,
              }}
              className="w-2 h-2 bg-gray-400 rounded-full inline-block mx-1"
            />
            <motion.span
              animate={{ scale: [1, 1.2, 1] }}
              transition={{
                duration: 0.6,
                repeat: Infinity,
                delay: 0.4,
              }}
              className="w-2 h-2 bg-gray-400 rounded-full inline-block"
            />
          </div>
          
          {/* Message Tail */}
          <div className="absolute top-4 w-3 h-3 transform rotate-45 bg-white border-l border-t border-gray-200 -left-1.5" />
        </div>
      </div>
    </motion.div>
  );
};