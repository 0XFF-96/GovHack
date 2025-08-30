import React from 'react';
import { Card, Typography, Empty } from 'antd';
import { SettingOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';

const { Title, Text } = Typography;

export const SettingsPage: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Page Header */}
      <div className="mb-6">
        <Title level={2} className="!mb-2 flex items-center">
          <SettingOutlined className="mr-3 text-blue-600" />
          System Settings
        </Title>
        <Text className="text-gray-600">
          Configure system parameters and user preferences
        </Text>
      </div>

      {/* Settings Content */}
      <Card className="shadow-sm border-gray-200">
        <div className="h-96 flex items-center justify-center">
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={
              <span className="text-gray-500">
                System settings interface under development...
                <br />
                Personalized configuration features coming soon
              </span>
            }
          />
        </div>
      </Card>
    </motion.div>
  );
};