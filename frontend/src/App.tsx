import React from 'react';
import { BackendTest } from './components/BackendTest';
import './index.css';

function App() {
  return (
    <div className="min-h-screen bg-deep-space text-cosmic-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8">
          🚀 Ariadne - The AI Research Navigator
        </h1>
        <p className="text-center text-cosmic-white/80 mb-12">
          Testing frontend-backend communication...
        </p>
        
        <BackendTest />
        
        <div className="mt-12 text-center">
          <h2 className="text-2xl font-bold mb-4">Development Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-cosmic-white/10 rounded-lg p-4">
              <h3 className="font-semibold text-green-400">✅ Backend</h3>
              <p className="text-sm text-cosmic-white/80">FastAPI server with all endpoints</p>
            </div>
            <div className="bg-cosmic-white/10 rounded-lg p-4">
              <h3 className="font-semibold text-yellow-400">🔄 Frontend</h3>
              <p className="text-sm text-cosmic-white/80">React app testing connection</p>
            </div>
            <div className="bg-cosmic-white/10 rounded-lg p-4">
              <h3 className="font-semibold text-blue-400">🔗 Communication</h3>
              <p className="text-sm text-cosmic-white/80">API client setup complete</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
