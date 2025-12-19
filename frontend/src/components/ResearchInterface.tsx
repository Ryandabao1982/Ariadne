import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/api';

interface ResearchResult {
  query: string;
  user_id?: string;
  start_time: string;
  results: Array<{
    tool: string;
    data: any;
    success: boolean;
    metadata: any;
  }>;
  errors: string[];
  tools_used: string[];
  status: string;
  execution_time_seconds: number;
}

export const ResearchInterface: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<ResearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [tools, setTools] = useState<any[]>([]);

  useEffect(() => {
    loadAvailableTools();
  }, []);

  const loadAvailableTools = async () => {
    try {
      const response = await apiClient.request<{ tools: any[] }>('/api/v1/research/tools');
      setTools(response.tools);
    } catch (error) {
      console.error('Failed to load tools:', error);
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const response = await apiClient.searchResearch({ query });
      setResults(response as ResearchResult);
    } catch (error) {
      console.error('Research failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const response = await apiClient.analyzeContent({ content: query });
      console.log('Analysis result:', response);
      alert('Analysis completed! Check console for details.');
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-deep-space border border-cosmic-white/20 rounded-lg p-6">
      <h3 className="text-xl font-bold text-cosmic-white mb-4">
        🔬 Research Interface
      </h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-cosmic-white mb-2">Research Query:</label>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your research question..."
            className="w-full p-3 bg-cosmic-white/10 border border-cosmic-white/20 rounded text-cosmic-white placeholder-cosmic-white/50"
            rows={3}
          />
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={handleSearch}
            disabled={loading || !query.trim()}
            className="px-4 py-2 bg-cosmic-white text-deep-space rounded hover:bg-cosmic-white/90 disabled:opacity-50"
          >
            {loading ? 'Searching...' : '🔍 Search'}
          </button>
          
          <button
            onClick={handleAnalyze}
            disabled={loading || !query.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Analyzing...' : '📊 Analyze'}
          </button>
        </div>
        
        {tools.length > 0 && (
          <div className="bg-cosmic-white/10 rounded p-4">
            <h4 className="text-cosmic-white font-semibold mb-2">Available Tools:</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {tools.map((tool, index) => (
                <div key={index} className="text-sm">
                  <span className="text-green-400">✓</span> {tool.name}
                  <span className="text-cosmic-white/60 ml-2">({tool.version})</span>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {results && (
          <div className="bg-cosmic-white/10 rounded p-4">
            <h4 className="text-cosmic-white font-semibold mb-2">Research Results:</h4>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-cosmic-white">Query:</span> {results.query}
              </div>
              <div>
                <span className="text-cosmic-white">Status:</span> 
                <span className={`ml-2 ${results.status === 'completed' ? 'text-green-400' : 'text-yellow-400'}`}>
                  {results.status}
                </span>
              </div>
              <div>
                <span className="text-cosmic-white">Execution Time:</span> {results.execution_time_seconds.toFixed(2)}s
              </div>
              <div>
                <span className="text-cosmic-white">Tools Used:</span> {results.tools_used.join(', ') || 'None'}
              </div>
              {results.errors.length > 0 && (
                <div>
                  <span className="text-red-400">Errors:</span>
                  <ul className="list-disc list-inside ml-4 text-red-300">
                    {results.errors.map((error, index) => (
                      <li key={index}>{error}</li>
                    ))}
                  </ul>
                </div>
              )}
              <div>
                <span className="text-cosmic-white">Results Count:</span> {results.results.length}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
