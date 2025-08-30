import React from 'react';
import { Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';

interface LoadingSpinnerProps {
  size?: 'small' | 'default' | 'large';
  tip?: string;
  className?: string;
  fullscreen?: boolean;
}

const customIcon = <LoadingOutlined style={{ fontSize: 24 }} spin />;

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'default',
  tip = '正在加载...',
  className = '',
  fullscreen = false,
}) => {
  const content = (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex flex-col items-center justify-center ${className}`}
    >
      <Spin
        indicator={customIcon}
        size={size}
        tip={tip}
        className="text-blue-600"
      />
      {tip && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className="mt-4 text-sm text-gray-600"
        >
          {tip}
        </motion.div>
      )}
    </motion.div>
  );

  if (fullscreen) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-white bg-opacity-80 z-50">
        {content}
      </div>
    );
  }

  return content;
};