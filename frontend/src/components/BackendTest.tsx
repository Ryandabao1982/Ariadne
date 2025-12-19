import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/api';

export const BackendTest: React.FC = () => {
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const [healthData, setHealthData] = useState<any>(null);

  const testBackendConnection = async () => {
    setStatus('loading');
    setMessage('Testing backend connection...');
    
    try {
      // Test health endpoint
      const health = await apiClient.healthCheck();
      setHealthData(health);
      setMessage('✅ Backend connection successful!');
      setStatus('success');
      
      // Test other endpoints
      try {
        const users = await apiClient.getUserProfile();
        console.log('Users endpoint:', users);
      } catch (error) {
        console.log('Users endpoint (expected in dev):', error);
      }
      
      try {
        const tapestries = await apiClient.listTapestries();
        console.log('Tapestries endpoint:', tapestries);
      } catch (error) {
        console.log('Tapestries endpoint (expected in dev):', error);
      }
      
    } catch (error) {
      setMessage('❌ Backend connection failed');
      setStatus('error');
      console.error('Backend test failed:', error);
    }
  };

  useEffect(() => {
    testBackendConnection();
  }, []);

  return (
    <div className="bg-deep-space border border-cosmic-white/20 rounded-lg p-6">
      <h3 className="text-xl font-bold text-cosmic-white mb-4">
        Backend Connection Test
      </h3>
      
      <div className="space-y-4">
        <div>
          <span className="text-cosmic-white">Status: </span>
          <span className={
            status === 'success' ? 'text-green-400' :
            status === 'error' ? 'text-red-400' :
            status === 'loading' ? 'text-yellow-400' :
            'text-gray-400'
          }>
            {status}
          </span>
        </div>
        
        <div className="text-cosmic-white">{message}</div>
        
        {healthData && (
          <div className="bg-cosmic-white/10 rounded p-4">
            <h4 className="text-cosmic-white font-semibold mb-2">Backend Info:</h4>
            <pre className="text-sm text-cosmic-white/80 overflow-auto">
              {JSON.stringify(healthData, null, 2)}
            </pre>
          </div>
        )}
        
        <button
          onClick={testBackendConnection}
          disabled={status === 'loading'}
          className="px-4 py-2 bg-cosmic-white text-deep-space rounded hover:bg-cosmic-white/90 disabled:opacity-50"
        >
          {status === 'loading' ? 'Testing...' : 'Retest Connection'}
        </button>
      </div>
    </div>
  );
};
