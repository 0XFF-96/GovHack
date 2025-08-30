'use client';

import { useEffect, useState } from 'react';
import { api } from '../../lib/api';

export default function TestPage() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const testAPI = async () => {
      try {
        console.log('Testing API calls...');
        console.log('API object:', api);
        
        // Test budget summary
        const summary = await api.budget.getSummary('2024-25');
        console.log('Budget summary:', summary);
        
        setData({ summary });
        setError(null);
      } catch (err) {
        console.error('API Error:', err);
        setError(err.message || 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    testAPI();
  }, []);

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }
  
  if (error) {
    return <div className="p-8 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">API Test Results</h1>
      <pre className="bg-gray-100 p-4 rounded overflow-auto">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}