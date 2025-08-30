import React from 'react';
import { Card, Row, Col, Statistic, Typography } from 'antd';
import {
  DashboardOutlined,
  DatabaseOutlined,
  MessageOutlined,
  TrophyOutlined,
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import { BudgetChart } from '../components/charts/BudgetChart';

const { Title, Text } = Typography;

export const DashboardPage: React.FC = () => {
  const stats = [
    {
      title: 'Total Datasets',
      value: 2,
      icon: <DatabaseOutlined className="text-blue-500" />,
      suffix: '',
    },
    {
      title: 'Budget Records',
      value: 1874,
      icon: <TrophyOutlined className="text-green-500" />,
      suffix: '',
    },
    {
      title: 'Chat Sessions',
      value: 0,
      icon: <MessageOutlined className="text-orange-500" />,
      suffix: '',
    },
    {
      title: 'Average Trust Score',
      value: 85,
      icon: <TrophyOutlined className="text-purple-500" />,
      suffix: '%',
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Page Header */}
      <div className="mb-6">
        <Title level={2} className="!mb-2 flex items-center">
          <DashboardOutlined className="mr-3 text-blue-600" />
          Data Dashboard
        </Title>
        <Text className="text-gray-600">
          Real-time system monitoring and data statistics overview
        </Text>
      </div>

      {/* Statistics Cards */}
      <Row gutter={[16, 16]} className="mb-6">
        {stats.map((stat, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card className="shadow-sm border-gray-200 hover:shadow-md transition-shadow">
                <Statistic
                  title={stat.title}
                  value={stat.value}
                  suffix={stat.suffix}
                  prefix={stat.icon}
                  valueStyle={{ color: '#1f2937' }}
                />
              </Card>
            </motion.div>
          </Col>
        ))}
      </Row>

      {/* Charts Section */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card 
            title="Department Budget Comparison" 
            className="shadow-sm border-gray-200"
            extra={<Text className="text-gray-500">2023 vs 2024 Financial Year</Text>}
          >
            <BudgetChart type="bar" height={300} />
          </Card>
        </Col>
        
        <Col xs={24} lg={12}>
          <Card 
            title="Budget Distribution" 
            className="shadow-sm border-gray-200"
            extra={<Text className="text-gray-500">2024 Financial Year</Text>}
          >
            <BudgetChart type="pie" height={300} />
          </Card>
        </Col>
        
        <Col xs={24}>
          <Card 
            title="Budget Trend Analysis" 
            className="shadow-sm border-gray-200"
            extra={<Text className="text-gray-500">2020-2024 Financial Years</Text>}
          >
            <BudgetChart type="line" height={250} />
          </Card>
        </Col>
      </Row>
    </motion.div>
  );
};