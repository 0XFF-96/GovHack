import React from 'react';
import { Card, Tag, Space, Typography, Button, Tooltip } from 'antd';
import { 
  DatabaseOutlined, 
  CalendarOutlined, 
  FileTextOutlined, 
  EyeOutlined,
  BarChartOutlined 
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import type { Dataset } from '../../types/api';

const { Title, Text, Paragraph } = Typography;

interface DatasetCardProps {
  dataset: Dataset;
  onView?: (dataset: Dataset) => void;
  onAnalyze?: (dataset: Dataset) => void;
}

export const DatasetCard: React.FC<DatasetCardProps> = ({ 
  dataset, 
  onView, 
  onAnalyze 
}) => {
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <motion.div
      whileHover={{ y: -4, boxShadow: '0 8px 25px rgba(0,0,0,0.12)' }}
      transition={{ duration: 0.2 }}
    >
      <Card
        className="h-full shadow-sm border-gray-200 hover:border-blue-300 transition-colors"
        bodyStyle={{ height: '100%' }}
      >
        <div className="h-full flex flex-col">
          {/* Header */}
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <DatabaseOutlined className="text-blue-600 text-lg" />
              </div>
              <div>
                <Title level={5} className="!mb-1 !text-gray-900">
                  {dataset.name}
                </Title>
                <Text className="text-xs text-gray-500">ID: {dataset.id}</Text>
              </div>
            </div>
          </div>

          {/* Description */}
          <div className="flex-1 mb-4">
            <Paragraph 
              className="text-gray-700 text-sm !mb-2"
              ellipsis={{ rows: 2, tooltip: dataset.description }}
            >
              {dataset.description}
            </Paragraph>
          </div>

          {/* Statistics */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="text-center p-2 bg-gray-50 rounded-lg">
              <div className="text-lg font-semibold text-blue-600">
                {formatNumber(dataset.record_count)}
              </div>
              <div className="text-xs text-gray-600">Records</div>
            </div>
            
            {dataset.portfolios && (
              <div className="text-center p-2 bg-gray-50 rounded-lg">
                <div className="text-lg font-semibold text-green-600">
                  {dataset.portfolios}
                </div>
                <div className="text-xs text-gray-600">Portfolios</div>
              </div>
            )}
            
            {dataset.departments && (
              <div className="text-center p-2 bg-gray-50 rounded-lg">
                <div className="text-lg font-semibold text-orange-600">
                  {dataset.departments}
                </div>
                <div className="text-xs text-gray-600">Departments</div>
              </div>
            )}
            
            <div className="text-center p-2 bg-gray-50 rounded-lg">
              <div className="text-lg font-semibold text-purple-600">
                {(dataset.size / 1000).toFixed(1)}K
              </div>
              <div className="text-xs text-gray-600">Data Size</div>
            </div>
          </div>

          {/* Metadata */}
          <div className="mb-4">
            <Space direction="vertical" size={4} className="w-full">
              <div className="flex items-center text-xs text-gray-600">
                <CalendarOutlined className="mr-2" />
                Last Updated: {formatDate(dataset.last_updated)}
              </div>
            </Space>
          </div>

          {/* Tags */}
          <div className="mb-4">
            <Space wrap>
              <Tag color="blue" icon={<FileTextOutlined />}>
                Budget Data
              </Tag>
              <Tag color="green">
                Public Data
              </Tag>
              {dataset.record_count > 1000 && (
                <Tag color="orange">
                  Large Dataset
                </Tag>
              )}
            </Space>
          </div>

          {/* Actions */}
          <div className="flex space-x-2 mt-auto">
            <Tooltip title="View Details">
              <Button
                type="default"
                icon={<EyeOutlined />}
                onClick={() => onView?.(dataset)}
                className="flex-1"
              >
                View Details
              </Button>
            </Tooltip>
            
            <Tooltip title="Data Analysis">
              <Button
                type="primary"
                icon={<BarChartOutlined />}
                onClick={() => onAnalyze?.(dataset)}
                className="flex-1 bg-blue-600 hover:bg-blue-700 border-blue-600"
              >
                Data Analysis
              </Button>
            </Tooltip>
          </div>
        </div>
      </Card>
    </motion.div>
  );
};