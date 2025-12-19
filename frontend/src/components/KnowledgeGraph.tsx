import React, { useState, useEffect } from 'react';

interface Concept {
  id: string;
  name: string;
  frequency: number;
  contexts: Array<{
    query: string;
    timestamp: string;
  }>;
}

interface KnowledgeGraphData {
  concepts: Concept[];
  connections: any[];
  stats: {
    total_contexts: number;
    total_concepts: number;
    total_edges: number;
    most_common_concepts: Array<[string, number]>;
    recent_contexts: any[];
  };
}

export const KnowledgeGraph: React.FC = () => {
  const [graphData, setGraphData] = useState<KnowledgeGraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedConcept, setSelectedConcept] = useState<Concept | null>(null);
  const [viewMode, setViewMode] = useState<'overview' | 'detailed'>('overview');

  useEffect(() => {
    loadKnowledgeGraph();
  }, []);

  const loadKnowledgeGraph = async () => {
    setLoading(true);
    try {
      // In a real implementation, this would call the API
      // For now, simulate knowledge graph data
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockData: KnowledgeGraphData = {
        concepts: [
          {
            id: 'concept_artificial_intelligence',
            name: 'artificial intelligence',
            frequency: 12,
            contexts: [
              { query: 'What is machine learning?', timestamp: '2025-12-19T09:00:00Z' },
              { query: 'How do neural networks work?', timestamp: '2025-12-19T08:30:00Z' },
              { query: 'AI applications in healthcare', timestamp: '2025-12-19T07:15:00Z' }
            ]
          },
          {
            id: 'concept_machine_learning',
            name: 'machine learning',
            frequency: 8,
            contexts: [
              { query: 'What is machine learning?', timestamp: '2025-12-19T09:00:00Z' },
              { query: 'Supervised vs unsupervised learning', timestamp: '2025-12-19T06:45:00Z' },
              { query: 'Deep learning algorithms', timestamp: '2025-12-19T05:20:00Z' }
            ]
          },
          {
            id: 'concept_neural_networks',
            name: 'neural networks',
            frequency: 6,
            contexts: [
              { query: 'How do neural networks work?', timestamp: '2025-12-19T08:30:00Z' },
              { query: 'Deep learning algorithms', timestamp: '2025-12-19T05:20:00Z' },
              { query: 'CNN architecture explained', timestamp: '2025-12-19T04:10:00Z' }
            ]
          },
          {
            id: 'concept_natural_language_processing',
            name: 'natural language processing',
            frequency: 4,
            contexts: [
              { query: 'NLP techniques for text analysis', timestamp: '2025-12-19T03:30:00Z' },
              { query: 'Language models and transformers', timestamp: '2025-12-19T02:15:00Z' }
            ]
          }
        ],
        connections: [
          { source: 'concept_artificial_intelligence', target: 'concept_machine_learning', strength: 0.8 },
          { source: 'concept_machine_learning', target: 'concept_neural_networks', strength: 0.9 },
          { source: 'concept_artificial_intelligence', target: 'concept_neural_networks', strength: 0.7 },
          { source: 'concept_natural_language_processing', target: 'concept_neural_networks', strength: 0.6 }
        ],
        stats: {
          total_contexts: 15,
          total_concepts: 4,
          total_edges: 4,
          most_common_concepts: [
            ['artificial intelligence', 12],
            ['machine learning', 8],
            ['neural networks', 6],
            ['natural language processing', 4],
            ['deep learning', 3]
          ],
          recent_contexts: [
            { query: 'What is machine learning?', timestamp: '2025-12-19T09:00:00Z' },
            { query: 'How do neural networks work?', timestamp: '2025-12-19T08:30:00Z' },
            { query: 'AI applications in healthcare', timestamp: '2025-12-19T07:15:00Z' }
          ]
        }
      };
      
      setGraphData(mockData);
    } catch (error) {
      console.error('Failed to load knowledge graph:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderGraphVisualization = () => {
    if (!graphData) return null;

    const { concepts, connections } = graphData;
    const width = 800;
    const height = 500;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 3;

    // Calculate positions for concepts (circular layout)
    const conceptPositions = concepts.map((concept, index) => {
      const angle = (index / concepts.length) * 2 * Math.PI;
      return {
        ...concept,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      };
    });

    return (
      <div className="relative bg-deep-space border border-cosmic-white/20 rounded-lg p-6">
        <svg width={width} height={height} className="w-full h-auto">
          {/* Render connections */}
          {connections.map((connection, index) => {
            const source = conceptPositions.find(c => c.id === connection.source);
            const target = conceptPositions.find(c => c.id === connection.target);
            
            if (!source || !target) return null;
            
            return (
              <line
                key={index}
                x1={source.x}
                y1={source.y}
                x2={target.x}
                y2={target.y}
                stroke="rgba(255, 255, 255, 0.3)"
                strokeWidth={connection.strength * 3}
                className="transition-all duration-300"
              />
            );
          })}
          
          {/* Render concept nodes */}
          {conceptPositions.map((concept) => {
            const size = Math.max(20, concept.frequency * 3);
            const isSelected = selectedConcept?.id === concept.id;
            
            return (
              <g key={concept.id}>
                <circle
                  cx={concept.x}
                  cy={concept.y}
                  r={size}
                  fill={isSelected ? "#60A5FA" : "rgba(147, 197, 253, 0.7)"}
                  stroke="rgba(255, 255, 255, 0.5)"
                  strokeWidth={isSelected ? 3 : 1}
                  className="cursor-pointer transition-all duration-300 hover:fill-blue-400"
                  onClick={() => setSelectedConcept(concept)}
                />
                <text
                  x={concept.x}
                  y={concept.y + size + 15}
                  textAnchor="middle"
                  className="fill-cosmic-white text-sm font-medium pointer-events-none"
                >
                  {concept.name}
                </text>
                <text
                  x={concept.x}
                  y={concept.y + size + 28}
                  textAnchor="middle"
                  className="fill-cosmic-white/60 text-xs pointer-events-none"
                >
                  {concept.frequency} mentions
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    );
  };

  const renderConceptDetails = () => {
    if (!selectedConcept) return null;

    return (
      <div className="bg-cosmic-white/10 rounded-lg p-4">
        <h4 className="text-lg font-semibold text-cosmic-white mb-3">
          📚 {selectedConcept.name}
        </h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-cosmic-white/80">Frequency:</span>
            <span className="text-green-400">{selectedConcept.frequency} mentions</span>
          </div>
          <div className="text-cosmic-white/80">
            Recent contexts:
          </div>
          <div className="space-y-2">
            {selectedConcept.contexts.slice(0, 3).map((context, index) => (
              <div key={index} className="bg-deep-space/50 rounded p-2">
                <div className="text-cosmic-white">{context.query}</div>
                <div className="text-cosmic-white/60 text-xs">
                  {new Date(context.timestamp).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="bg-deep-space border border-cosmic-white/20 rounded-lg p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cosmic-white mx-auto mb-4"></div>
        <p className="text-cosmic-white">Loading knowledge graph...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-deep-space border border-cosmic-white/20 rounded-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-2xl font-bold text-cosmic-white">
            🕸️ The Loom - Knowledge Graph
          </h3>
          <div className="flex gap-3">
            <button
              onClick={() => setViewMode(viewMode === 'overview' ? 'detailed' : 'overview')}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              {viewMode === 'overview' ? '📊 Detailed View' : '🕸️ Graph View'}
            </button>
            <button
              onClick={loadKnowledgeGraph}
              className="px-4 py-2 bg-cosmic-white text-deep-space rounded hover:bg-cosmic-white/90"
            >
              🔄 Refresh
            </button>
          </div>
        </div>

        {graphData && (
          <>
            {/* Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-cosmic-white/10 rounded p-4 text-center">
                <div className="text-2xl font-bold text-green-400">
                  {graphData.stats.total_concepts}
                </div>
                <div className="text-cosmic-white/80 text-sm">Concepts</div>
              </div>
              <div className="bg-cosmic-white/10 rounded p-4 text-center">
                <div className="text-2xl font-bold text-blue-400">
                  {graphData.stats.total_contexts}
                </div>
                <div className="text-cosmic-white/80 text-sm">Research Sessions</div>
              </div>
              <div className="bg-cosmic-white/10 rounded p-4 text-center">
                <div className="text-2xl font-bold text-purple-400">
                  {graphData.stats.total_edges}
                </div>
                <div className="text-cosmic-white/80 text-sm">Connections</div>
              </div>
              <div className="bg-cosmic-white/10 rounded p-4 text-center">
                <div className="text-2xl font-bold text-yellow-400">
                  {graphData.stats.most_common_concepts.length}
                </div>
                <div className="text-cosmic-white/80 text-sm">Top Concepts</div>
              </div>
            </div>

            {/* Main visualization or detailed view */}
            {viewMode === 'overview' ? (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                  {renderGraphVisualization()}
                </div>
                <div className="space-y-4">
                  {renderConceptDetails()}
                  
                  {/* Most common concepts */}
                  <div className="bg-cosmic-white/10 rounded-lg p-4">
                    <h4 className="text-lg font-semibold text-cosmic-white mb-3">
                      🔥 Most Common Concepts
                    </h4>
                    <div className="space-y-2">
                      {graphData.stats.most_common_concepts.slice(0, 5).map(([concept, freq], index) => (
                        <div key={index} className="flex justify-between items-center">
                          <span className="text-cosmic-white text-sm">{concept}</span>
                          <span className="text-green-400 text-sm font-medium">{freq}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Detailed concept list */}
                <div className="bg-cosmic-white/10 rounded-lg p-4">
                  <h4 className="text-lg font-semibold text-cosmic-white mb-4">
                    📚 All Concepts
                  </h4>
                  <div className="space-y-3">
                    {graphData.concepts.map((concept) => (
                      <div
                        key={concept.id}
                        className={`p-3 rounded cursor-pointer transition-all ${
                          selectedConcept?.id === concept.id
                            ? 'bg-blue-600/20 border border-blue-400'
                            : 'bg-deep-space/50 hover:bg-deep-space/70'
                        }`}
                        onClick={() => setSelectedConcept(concept)}
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="text-cosmic-white font-medium">{concept.name}</div>
                            <div className="text-cosmic-white/60 text-sm">
                              {concept.contexts.length} contexts
                            </div>
                          </div>
                          <div className="text-green-400 font-bold">
                            {concept.frequency}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Selected concept details */}
                <div>
                  {renderConceptDetails() || (
                    <div className="bg-cosmic-white/10 rounded-lg p-8 text-center">
                      <div className="text-cosmic-white/60">
                        Select a concept to view details
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};
