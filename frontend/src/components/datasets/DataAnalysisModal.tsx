import React, { useState, useEffect } from 'react';
import {
  Modal,
  Tabs,
  Card,
  Statistic,
  Row,
  Col,
  Spin,
  Alert,
  Progress,
  Typography,
  Divider,
  Tag,
} from 'antd';
import {
  DatabaseOutlined,
  BarChartOutlined,
  PieChartOutlined,
  BarChartOutlined as TrendingUpOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import { BudgetChart } from '../charts/BudgetChart';
import { EnhancedBudgetComparison } from '../charts/EnhancedBudgetComparison';
import { customAxiosInstance } from '../../services/axiosConfig';
import type { Dataset } from '../../types/api';

const { Title, Text } = Typography;

interface DataAnalysisModalProps {
  dataset: Dataset | null;
  open: boolean;
  onClose: () => void;
}

interface DataAnalysis {
  data_counts: {
    portfolios: number;
    departments: number;
    programs: number;
    budget_expenses: number;
  };
  last_import: {
    id: string;
    batch_id: string;
    source_file: string;
    status: string;
    total_rows: number;
    processed_rows: number;
    success_rows: number;
    error_rows: number;
    success_rate: number;
    start_time: string;
    end_time: string;
    duration_seconds: number;
    import_summary: {
      success_rate: number;
      total_processed: number;
      outcomes_created: number;
      programs_created: number;
      portfolios_created: number;
      departments_created: number;
    };
  };
  data_quality: {
    completeness_rate: number;
    total_budget_2024_25: number;
    data_freshness: string;
  };
}

export const DataAnalysisModal: React.FC<DataAnalysisModalProps> = ({
  dataset,
  open,
  onClose,
}) => {
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<DataAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalysis = async () => {
    if (!dataset) return;

    try {
      setLoading(true);
      setError(null);

      const response = await customAxiosInstance.get('/v1/datasets/stats/overview/');
      setAnalysis(response.data);
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to fetch data analysis';
      setError(errorMessage);
      console.error('Error fetching analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open && dataset) {
      fetchAnalysis();
    }
  }, [open, dataset]);

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'AUD',
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(amount * 1000); // Convert from thousands to actual amount
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

  const getQualityColor = (rate: number) => {
    if (rate >= 99) return 'success';
    if (rate >= 95) return 'warning';
    return 'exception';
  };

  const getQualityStatus = (rate: number) => {
    if (rate >= 99) return { color: '#52c41a', text: 'Excellent' };
    if (rate >= 95) return { color: '#faad14', text: 'Good' };
    return { color: '#ff4d4f', text: 'Need Improvement' };
  };

  const tabItems = [
    {
      key: 'overview',
      label: 'Data Overview',
      icon: <DatabaseOutlined />,
      children: (
        <div className="space-y-6">
          {/* 核心指标 */}
          <Row gutter={[16, 16]}>
            <Col xs={24} sm={12} lg={6}>
              <Card size="small">
                <Statistic
                  title="Portfolios"
                  value={analysis?.data_counts.portfolios}
                  prefix={<DatabaseOutlined className="text-blue-600" />}
                  suffix=""
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card size="small">
                <Statistic
                  title="Departments"
                  value={analysis?.data_counts.departments}
                  prefix={<DatabaseOutlined className="text-green-600" />}
                  suffix=""
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card size="small">
                <Statistic
                  title="Budget Programs"
                  value={analysis?.data_counts.programs}
                  prefix={<BarChartOutlined className="text-orange-600" />}
                  suffix=""
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card size="small">
                <Statistic
                  title="Budget Records"
                  value={analysis?.data_counts.budget_expenses}
                  prefix={<PieChartOutlined className="text-purple-600" />}
                  suffix=""
                />
              </Card>
            </Col>
          </Row>

          {/* 预算总额 */}
          <Card>
            <Title level={4}>2024-25 Budget Total</Title>
            <div className="text-center py-6">
              <div className="text-5xl font-bold text-blue-600 mb-2">
                {analysis && formatCurrency(analysis.data_quality.total_budget_2024_25)}
              </div>
              <Text className="text-lg text-gray-600">Australian Dollars</Text>
            </div>
          </Card>
        </div>
      ),
    },
    {
      key: 'quality',
      label: 'Data Quality',
      icon: <CheckCircleOutlined />,
      children: (
        <div className="space-y-6">
          {/* 数据完整性 */}
          <Card>
            <Title level={4}>数据完整性分析</Title>
            <Row gutter={[16, 16]} className="mt-4">
              <Col xs={24} lg={12}>
                <div className="text-center">
                  <Progress
                    type="circle"
                    percent={Math.round(analysis?.data_quality.completeness_rate || 0)}
                    status={getQualityColor(analysis?.data_quality.completeness_rate || 0) as any}
                    size={120}
                    strokeWidth={8}
                  />
                  <div className="mt-4">
                    <Text strong>Data Completeness Rate</Text>
                    <div className="mt-1">
                      <Tag color={getQualityStatus(analysis?.data_quality.completeness_rate || 0).color}>
                        {getQualityStatus(analysis?.data_quality.completeness_rate || 0).text}
                      </Tag>
                    </div>
                  </div>
                </div>
              </Col>
              <Col xs={24} lg={12}>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span>数据记录总数</span>
                    <span className="font-semibold">{formatNumber(analysis?.last_import.total_rows || 0)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>成功处理记录</span>
                    <span className="font-semibold text-green-600">
                      {formatNumber(analysis?.last_import.success_rows || 0)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>错误记录</span>
                    <span className="font-semibold text-red-600">
                      {formatNumber(analysis?.last_import.error_rows || 0)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>处理成功率</span>
                    <span className="font-semibold text-blue-600">
                      {(analysis?.last_import.success_rate || 0).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </Col>
            </Row>
          </Card>

          {/* Data Freshness */}
          <Card>
            <Title level={4}>Data Freshness</Title>
            <div className="flex items-center space-x-3">
              <ClockCircleOutlined className="text-blue-600 text-lg" />
              <div>
                <Text strong>最后更新时间: </Text>
                <Text>{analysis && formatDate(analysis.data_quality.data_freshness)}</Text>
              </div>
            </div>
          </Card>
        </div>
      ),
    },
    {
      key: 'import',
      label: 'Import History',
      icon: <TrendingUpOutlined />,
      children: (
        <div className="space-y-6">
          <Card>
            <Title level={4}>Recent Import Record</Title>
            {analysis?.last_import && (
              <div className="space-y-4">
                <Row gutter={[16, 16]}>
                  <Col xs={24} md={12}>
                    <div className="space-y-2">
                      <div><Text strong>Batch ID:</Text> {analysis.last_import.batch_id}</div>
                      <div><Text strong>Source File:</Text> {analysis.last_import.source_file.split('/').pop()}</div>
                      <div><Text strong>Status:</Text> 
                        <Tag color="success" className="ml-2">
                          <CheckCircleOutlined className="mr-1" />
                          {analysis.last_import.status === 'completed' ? 'Completed' : analysis.last_import.status}
                        </Tag>
                      </div>
                    </div>
                  </Col>
                  <Col xs={24} md={12}>
                    <div className="space-y-2">
                      <div><Text strong>Start Time:</Text> {formatDate(analysis.last_import.start_time)}</div>
                      <div><Text strong>End Time:</Text> {formatDate(analysis.last_import.end_time)}</div>
                      <div><Text strong>Processing Duration:</Text> {analysis.last_import.duration_seconds.toFixed(2)} seconds</div>
                    </div>
                  </Col>
                </Row>

                <Divider />

                <Title level={5}>Import Statistics</Title>
                <Row gutter={[16, 16]}>
                  <Col xs={24} sm={12} lg={6}>
                    <Statistic
                      title="Portfolios Created"
                      value={analysis.last_import.import_summary.portfolios_created}
                      prefix={<DatabaseOutlined />}
                    />
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <Statistic
                      title="Departments Created"
                      value={analysis.last_import.import_summary.departments_created}
                      prefix={<DatabaseOutlined />}
                    />
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <Statistic
                      title="Programs Created"
                      value={analysis.last_import.import_summary.programs_created}
                      prefix={<BarChartOutlined />}
                    />
                  </Col>
                  <Col xs={24} sm={12} lg={6}>
                    <Statistic
                      title="Outcomes Created"
                      value={analysis.last_import.import_summary.outcomes_created}
                      prefix={<PieChartOutlined />}
                    />
                  </Col>
                </Row>
              </div>
            )}
          </Card>
        </div>
      ),
    },
    {
      key: 'charts',
      label: 'Data Visualization',
      icon: <BarChartOutlined />,
      children: (
        <div className="space-y-6">
          {/* Enhanced Budget Comparison with full width */}
          <div className="mb-6">
            <EnhancedBudgetComparison />
          </div>
          
          <Row gutter={[16, 16]}>
            <Col xs={24} lg={12}>
              <Card title="Department Budget Distribution" size="small">
                <div className="h-72">
                  <BudgetChart type="pie" height={280} />
                </div>
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title="Budget Trend Analysis">
                <div className="h-72">
                  <BudgetChart type="line" height={280} />
                </div>
              </Card>
            </Col>
          </Row>
        </div>
      ),
    },
  ];

  return (
    <Modal
      title={
        <div className="flex items-center">
          <BarChartOutlined className="mr-2 text-blue-600" />
          Data Analysis - {dataset?.name}
        </div>
      }
      open={open}
      onCancel={onClose}
      width={1000}
      footer={null}
      destroyOnClose
    >
      <Spin spinning={loading}>
        {error ? (
          <Alert
            message="Loading Failed"
            description={error}
            type="error"
            showIcon
            className="mb-4"
          />
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Tabs
              defaultActiveKey="overview"
              items={tabItems}
              className="mt-4"
            />
          </motion.div>
        )}
      </Spin>
    </Modal>
  );
};