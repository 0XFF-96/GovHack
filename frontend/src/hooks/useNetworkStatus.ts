import { useState, useEffect } from 'react';
import { message } from 'antd';

interface NetworkStatus {
  isOnline: boolean;
  isSlowConnection: boolean;
  effectiveType?: string;
}

export const useNetworkStatus = (): NetworkStatus => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isSlowConnection, setIsSlowConnection] = useState(false);
  const [effectiveType, setEffectiveType] = useState<string | undefined>();

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      message.success('网络连接已恢复', 2);
    };

    const handleOffline = () => {
      setIsOnline(false);
      message.warning('网络连接已断开', 3);
    };

    const updateConnectionInfo = () => {
      // Check if the connection API is available
      if ('connection' in navigator || 'mozConnection' in navigator || 'webkitConnection' in navigator) {
        const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection;
        
        if (connection) {
          setEffectiveType(connection.effectiveType);
          
          // Consider 2G or slower as slow connection
          const slowTypes = ['slow-2g', '2g'];
          setIsSlowConnection(slowTypes.includes(connection.effectiveType));
          
          if (slowTypes.includes(connection.effectiveType)) {
            message.warning('检测到网络较慢，部分功能可能受影响', 3);
          }
        }
      }
    };

    // Add event listeners
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Listen for connection changes
    if ('connection' in navigator) {
      (navigator as any).connection?.addEventListener('change', updateConnectionInfo);
    }

    // Initial check
    updateConnectionInfo();

    // Cleanup
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      
      if ('connection' in navigator) {
        (navigator as any).connection?.removeEventListener('change', updateConnectionInfo);
      }
    };
  }, []);

  return {
    isOnline,
    isSlowConnection,
    effectiveType,
  };
};