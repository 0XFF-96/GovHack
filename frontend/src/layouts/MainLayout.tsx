import React from 'react';
import { Layout, Menu, Button, Dropdown, Avatar, Space, Badge } from 'antd';
import {
  MessageOutlined,
  DashboardOutlined,
  DatabaseOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  WifiOutlined,
  DisconnectOutlined,
} from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useNetworkStatus } from '../hooks/useNetworkStatus';

const { Header, Sider, Content } = Layout;

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = React.useState(false);
  const location = useLocation();
  const { isOnline, isSlowConnection } = useNetworkStatus();

  const menuItems = [
    {
      key: '/',
      icon: <MessageOutlined />,
      label: <Link to="/">Smart Chat</Link>,
    },
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: <Link to="/dashboard">Data Dashboard</Link>,
    },
    {
      key: '/datasets',
      icon: <DatabaseOutlined />,
      label: <Link to="/datasets">Dataset Management</Link>,
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: <Link to="/settings">System Settings</Link>,
    },
  ];

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      danger: true,
    },
  ];

  const handleUserMenuClick = (key: string) => {
    if (key === 'logout') {
      // Handle logout logic
      localStorage.removeItem('auth_token');
      // Could redirect to login page
    }
  };

  return (
    <Layout className="min-h-screen">
      {/* Sidebar */}
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        width={280}
        className="bg-white shadow-lg border-r border-gray-200"
        style={{
          position: 'fixed',
          height: '100vh',
          left: 0,
          top: 0,
          bottom: 0,
          zIndex: 100,
        }}
      >
        {/* Logo and Brand */}
        <motion.div
          className="flex items-center justify-center h-16 border-b border-gray-200"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          {!collapsed ? (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <MessageOutlined className="text-white text-lg" />
              </div>
              <span className="text-lg font-semibold text-gray-800">
                GovHack AI
              </span>
            </div>
          ) : (
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <MessageOutlined className="text-white text-lg" />
            </div>
          )}
        </motion.div>

        {/* Navigation Menu */}
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          className="border-0 bg-transparent"
          items={menuItems}
          style={{
            height: 'calc(100vh - 64px)',
            borderRight: 0,
          }}
        />
      </Sider>

      {/* Main Content Area */}
      <Layout style={{ marginLeft: collapsed ? 80 : 280, transition: 'all 0.3s' }}>
        {/* Top Header */}
        <Header className="bg-white shadow-sm border-b border-gray-200 px-6 flex justify-between items-center">
          {/* Collapse Toggle */}
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            className="hover:bg-gray-100 transition-colors"
          />

          {/* Header Right Section */}
          <Space>
            {/* Network Status Indicator */}
            <Badge 
              status={isOnline ? (isSlowConnection ? 'warning' : 'success') : 'error'}
              text={
                <span className="text-xs text-gray-600">
                  {isOnline ? (isSlowConnection ? 'Slow Network' : 'Online') : 'Offline'}
                </span>
              }
            />
            
            <div className="text-gray-300">|</div>
            
            {/* User Profile Dropdown */}
            <Dropdown
              menu={{
                items: userMenuItems,
                onClick: ({ key }) => handleUserMenuClick(key),
              }}
              placement="bottomRight"
              arrow
            >
              <div className="flex items-center space-x-2 cursor-pointer hover:bg-gray-50 px-3 py-2 rounded-lg transition-colors">
                <Avatar size="small" icon={<UserOutlined />} />
                <span className="text-sm font-medium">Administrator</span>
              </div>
            </Dropdown>
          </Space>
        </Header>

        {/* Page Content */}
        <Content className="p-6 bg-gray-50 min-h-screen">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="h-full"
          >
            {children}
          </motion.div>
        </Content>
      </Layout>
    </Layout>
  );
};