import React, { useState } from 'react';
import { Search, Sparkles, Target, Clock, Users } from 'lucide-react';

interface LandingPageProps {
  onQuery: (query: string) => void;
  isLoading?: boolean;
}

const LandingPage: React.FC<LandingPageProps> = ({ onQuery, isLoading = false }) => {
  const [query, setQuery] = useState('');

  const exampleQueries = [
    "What are the ethical implications of AI in healthcare?",
    "Latest developments in quantum computing",
    "How does the human microbiome affect mental health?"
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onQuery(query.trim());
    }
  };

  const handleExampleClick = (exampleQuery: string) => {
    setQuery(exampleQuery);
    onQuery(exampleQuery);
  };

  return (
    <div className="min-h-screen bg-deep-space text-cosmic-white">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-deep-space via-charcoal to-deep-space" />
        <div className="relative max-w-7xl mx-auto px-4 py-24 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-cosmic-white to-ariadne-glow bg-clip-text text-transparent">
              Your AI Research Partner
            </h1>
            <p className="text-xl md:text-2xl text-nebula-grey mb-12 max-w-3xl mx-auto">
              Ask any question. Get synthesized, cited reports in minutes. No login required.
            </p>

            {/* Search Box */}
            <form onSubmit={handleSubmit} className="max-w-2xl mx-auto mb-8">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-stardust w-6 h-6" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask me anything. No login required."
                  className="w-full pl-12 pr-4 py-4 bg-charcoal border border-graphite rounded-2xl text-cosmic-white placeholder-stardust focus:outline-none focus:ring-2 focus:ring-ariadne-glow focus:border-transparent text-lg"
                  disabled={isLoading}
                />
                {isLoading && (
                  <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                    <Sparkles className="w-6 h-6 text-ariadne-glow animate-spin" />
                  </div>
                )}
              </div>
            </form>

            {/* Example Queries */}
            <div className="space-y-2">
              <p className="text-stardust mb-4">Try these examples:</p>
              <div className="flex flex-wrap justify-center gap-3">
                {exampleQueries.map((example, index) => (
                  <button
                    key={index}
                    onClick={() => handleExampleClick(example)}
                    className="px-4 py-2 bg-charcoal border border-graphite rounded-lg text-cosmic-white hover:border-ariadne-glow hover:text-ariadne-glow transition-colors text-sm"
                    disabled={isLoading}
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="py-24 bg-charcoal">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-16">Why Choose Ariadne?</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-ariadne-glow rounded-full flex items-center justify-center mx-auto mb-6">
                <Target className="w-8 h-8 text-cosmic-white" />
              </div>
              <h3 className="text-xl font-semibold mb-4">Personal Knowledge Graph</h3>
              <p className="text-nebula-grey">
                Every query builds your personal library of knowledge, creating connections between topics you explore.
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-verified-green rounded-full flex items-center justify-center mx-auto mb-6">
                <Sparkles className="w-8 h-8 text-cosmic-white" />
              </div>
              <h3 className="text-xl font-semibold mb-4">AI-Powered Synthesis</h3>
              <p className="text-nebula-grey">
                Get comprehensive reports with proper citations, not just a list of search results.
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-attention-amber rounded-full flex items-center justify-center mx-auto mb-6">
                <Users className="w-8 h-8 text-cosmic-white" />
              </div>
              <h3 className="text-xl font-semibold mb-4">Collaborative Research</h3>
              <p className="text-nebula-grey">
                Share your findings with colleagues and build upon each other's research in real-time.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Social Proof Section */}
      <div className="py-16 bg-deep-space">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-stardust mb-8">Trusted by researchers at leading institutions</p>
          <div className="flex justify-center items-center space-x-8 opacity-60">
            {/* Placeholder for institution logos */}
            <div className="text-2xl font-bold text-stardust">MIT</div>
            <div className="text-2xl font-bold text-stardust">Stanford</div>
            <div className="text-2xl font-bold text-stardust">Oxford</div>
            <div className="text-2xl font-bold text-stardust">Harvard</div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="py-8 bg-charcoal border-t border-graphite">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-stardust">
          <p>&copy; 2025 Ariadne. Research with AI. Share with the world.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
