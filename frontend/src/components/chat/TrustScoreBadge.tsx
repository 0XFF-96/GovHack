import React from 'react';
import { Tag, Tooltip } from 'antd';
import { CheckCircleOutlined, ExclamationCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';

interface TrustScoreBadgeProps {
  score: number;
  size?: 'small' | 'default' | 'large';
  showIcon?: boolean;
}

export const TrustScoreBadge: React.FC<TrustScoreBadgeProps> = ({ 
  score, 
  size = 'default', 
  showIcon = true 
}) => {
  const percentage = Math.round(score * 100);
  
  const getTrustLevel = (score: number) => {
    if (score >= 0.9) return { level: 'high', color: '#28A745', text: '高可信度' };
    if (score >= 0.7) return { level: 'medium', color: '#FFC107', text: '中等可信度' };
    return { level: 'low', color: '#DC3545', text: '低可信度' };
  };

  const getIcon = (level: string) => {
    switch (level) {
      case 'high':
        return <CheckCircleOutlined />;
      case 'medium':
        return <ExclamationCircleOutlined />;
      case 'low':
        return <CloseCircleOutlined />;
      default:
        return null;
    }
  };

  const trustInfo = getTrustLevel(score);

  return (
    <Tooltip title={`${trustInfo.text}: ${percentage}%`}>
      <Tag
        color={trustInfo.color}
        icon={showIcon ? getIcon(trustInfo.level) : undefined}
        className={`
          inline-flex items-center font-medium
          ${size === 'small' ? 'text-xs' : size === 'large' ? 'text-base' : 'text-sm'}
        `}
      >
        {percentage}%
      </Tag>
    </Tooltip>
  );
};