import React, { useState } from 'react';
import { Row, Col, Typography, Spin, Alert, Button, Input, Space, Modal, Descriptions } from 'antd';
import { DatabaseOutlined, SearchOutlined, ReloadOutlined, EyeOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';

// Components and Hooks
import { DatasetCard } from '../components/datasets/DatasetCard';
import { DataAnalysisModal } from '../components/datasets/DataAnalysisModal';
import { useDatasets } from '../hooks/useDatasets';
import type { Dataset } from '../types/api';

const { Title, Text } = Typography;
const { Search } = Input;

export const DatasetsPage: React.FC = () => {
  const { datasets, loading, error, refetch } = useDatasets();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [analysisModalVisible, setAnalysisModalVisible] = useState(false);
  const [analysisDataset, setAnalysisDataset] = useState<Dataset | null>(null);

  // Filter datasets based on search term
  const filteredDatasets = datasets.filter(dataset =>
    dataset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    dataset.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    dataset.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleViewDataset = (dataset: Dataset) => {
    setSelectedDataset(dataset);
    setDetailModalVisible(true);
  };

  const handleAnalyzeDataset = (dataset: Dataset) => {
    setAnalysisDataset(dataset);
    setAnalysisModalVisible(true);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Page Header */}
      <div className="mb-6">
        <Title level={2} className="!mb-2 flex items-center">
          <DatabaseOutlined className="mr-3 text-blue-600" />
          Dataset Management
        </Title>
        <Text className="text-gray-600">
          Browse and manage government budget datasets, view detailed statistics
        </Text>
      </div>

      {/* Search and Actions Bar */}
      <div className="mb-6 bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <Space className="w-full justify-between">
          <Search
            placeholder="Search dataset name, description or ID..."
            prefix={<SearchOutlined />}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-80"
            allowClear
          />
          
          <Button
            icon={<ReloadOutlined />}
            onClick={refetch}
            loading={loading}
            className="flex items-center"
          >
            Refresh
          </Button>
        </Space>
        
        {/* Summary */}
        <div className="mt-3 text-sm text-gray-600">
          Found {filteredDatasets.length} datasets
          {searchTerm && ` (Search: "${searchTerm}")`}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <Alert
          message="Loading Failed"
          description={error}
          type="error"
          showIcon
          className="mb-6"
          action={
            <Button size="small" onClick={refetch}>
              Retry
            </Button>
          }
        />
      )}

      {/* Datasets Grid */}
      <Spin spinning={loading}>
        <Row gutter={[16, 16]}>
          {filteredDatasets.map((dataset, index) => (
            <Col xs={24} md={12} xl={8} key={dataset.id}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <DatasetCard
                  dataset={dataset}
                  onView={handleViewDataset}
                  onAnalyze={handleAnalyzeDataset}
                />
              </motion.div>
            </Col>
          ))}
        </Row>
        
        {/* Empty State */}
        {!loading && filteredDatasets.length === 0 && (
          <div className="text-center py-12">
            <DatabaseOutlined className="text-6xl text-gray-300 mb-4" />
            <Title level={4} className="text-gray-500">
              {searchTerm ? 'No matching datasets found' : 'No datasets available'}
            </Title>
            <Text className="text-gray-400">
              {searchTerm ? 'Please try other search keywords' : 'No datasets available in the system'}
            </Text>
          </div>
        )}
      </Spin>

      {/* Dataset Detail Modal */}
      <Modal
        title={
          <div className="flex items-center">
            <DatabaseOutlined className="mr-2 text-blue-600" />
            Dataset Details
          </div>
        }
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            Close
          </Button>,
          <Button 
            key="analyze" 
            type="primary" 
            icon={<EyeOutlined />}
            onClick={() => selectedDataset && handleAnalyzeDataset(selectedDataset)}
          >
            Data Analysis
          </Button>,
        ]}
        width={800}
      >
        {selectedDataset && (
          <Descriptions column={2} bordered>
            <Descriptions.Item label="Dataset ID">
              {selectedDataset.id}
            </Descriptions.Item>
            <Descriptions.Item label="Dataset Name">
              {selectedDataset.name}
            </Descriptions.Item>
            <Descriptions.Item label="Description" span={2}>
              {selectedDataset.description}
            </Descriptions.Item>
            <Descriptions.Item label="Record Count">
              {formatNumber(selectedDataset.record_count)}
            </Descriptions.Item>
            <Descriptions.Item label="Data Size">
              {formatNumber(selectedDataset.size)} records
            </Descriptions.Item>
            {selectedDataset.portfolios && (
              <Descriptions.Item label="Portfolios">
                {selectedDataset.portfolios}
              </Descriptions.Item>
            )}
            {selectedDataset.departments && (
              <Descriptions.Item label="Departments">
                {selectedDataset.departments}
              </Descriptions.Item>
            )}
            <Descriptions.Item label="Last Updated" span={2}>
              {formatDate(selectedDataset.last_updated)}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>

      {/* Data Analysis Modal */}
      <DataAnalysisModal
        dataset={analysisDataset}
        open={analysisModalVisible}
        onClose={() => setAnalysisModalVisible(false)}
      />
    </motion.div>
  );
};