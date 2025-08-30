import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Result, Button } from 'antd';
import { ReloadOutlined, HomeOutlined } from '@ant-design/icons';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error Boundary caught an error:', error, errorInfo);
    
    // In production, you might want to log this to an error reporting service
    if (process.env.NODE_ENV === 'production') {
      // Example: Sentry.captureException(error, { contexts: { errorInfo } });
    }
    
    this.setState({
      error,
      errorInfo,
    });
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-lg w-full mx-4">
            <Result
              status="error"
              title="页面出现错误"
              subTitle="抱歉，页面遇到了一些问题。请尝试刷新页面或返回首页。"
              extra={[
                <Button 
                  type="primary" 
                  icon={<ReloadOutlined />} 
                  onClick={this.handleReload}
                  key="reload"
                >
                  刷新页面
                </Button>,
                <Button 
                  icon={<HomeOutlined />} 
                  onClick={this.handleGoHome}
                  key="home"
                >
                  返回首页
                </Button>,
              ]}
            />
            
            {/* Error details (only in development) */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-6 p-4 bg-gray-100 rounded-lg text-sm">
                <summary className="cursor-pointer font-medium text-gray-700 mb-2">
                  错误详情 (开发模式)
                </summary>
                <div className="space-y-2">
                  <div>
                    <strong>错误信息:</strong>
                    <pre className="mt-1 text-red-600 whitespace-pre-wrap">
                      {this.state.error.message}
                    </pre>
                  </div>
                  <div>
                    <strong>错误堆栈:</strong>
                    <pre className="mt-1 text-gray-600 text-xs whitespace-pre-wrap">
                      {this.state.error.stack}
                    </pre>
                  </div>
                  {this.state.errorInfo && (
                    <div>
                      <strong>组件堆栈:</strong>
                      <pre className="mt-1 text-gray-600 text-xs whitespace-pre-wrap">
                        {this.state.errorInfo.componentStack}
                      </pre>
                    </div>
                  )}
                </div>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}