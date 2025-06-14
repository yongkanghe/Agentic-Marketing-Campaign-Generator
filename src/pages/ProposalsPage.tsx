/**
 * FILENAME: ProposalsPage.tsx
 * DESCRIPTION/PURPOSE: Marketing proposals page with video generation capabilities using VVL design system
 * Author: JP + 2024-12-19
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMarketingContext } from '@/contexts/MarketingContext';
import { MaterialVideoCard } from '@/components/MaterialVideoCard';
import { ArrowLeft, FileText, Video, Download, Home, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

const ProposalsPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    currentCampaign,
    generatedIdeas,
    toggleIdeaSelection,
    generateVideos,
    exportToText
  } = useMarketingContext();
  
  const [isLoading, setIsLoading] = useState(false);
  const [videosGenerated, setVideosGenerated] = useState(false);
  
  useEffect(() => {
    if (!currentCampaign) {
      navigate('/');
    }
  }, [currentCampaign, navigate]);
  
  const handleGenerateVideos = async () => {
    setIsLoading(true);
    
    try {
      await generateVideos();
      setVideosGenerated(true);
      toast.success('Videos generated successfully!');
    } catch (error) {
      toast.error('Failed to generate videos. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleSelectIdea = (ideaId: string) => {
    toggleIdeaSelection(ideaId);
  };
  
  if (!currentCampaign || generatedIdeas.length === 0) return null;
  
  const selectedIdeas = generatedIdeas.filter(idea => idea.selected);
  
  return (
    <div className="min-h-screen vvl-gradient-bg flex flex-col">
      {/* Header */}
      <header className="vvl-header-blur">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button 
                onClick={() => navigate('/')}
                className="vvl-button-secondary text-sm flex items-center gap-2"
              >
                <Home size={16} />
                Dashboard
              </button>
              <button 
                onClick={() => navigate('/ideation')}
                className="vvl-button-secondary text-sm flex items-center gap-2"
              >
                <ArrowLeft size={16} />
                Back to Ideation
              </button>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={exportToText}
                className="vvl-button-secondary text-sm flex items-center gap-2"
              >
                <FileText size={16} />
                Export to Text
              </button>
              
              {!videosGenerated && (
                <button
                  onClick={handleGenerateVideos}
                  disabled={isLoading}
                  className="vvl-button-primary text-sm flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Video size={16} />
                  {isLoading ? 'Generating...' : 'Generate Videos'}
                </button>
              )}
              
              {videosGenerated && (
                <button
                  onClick={() => toast.success('Videos downloaded successfully!')}
                  className="vvl-button-primary text-sm flex items-center gap-2"
                >
                  <Download size={16} />
                  Download All Videos
                </button>
              )}
            </div>
          </div>
        </div>
      </header>
      
      <div className="container mx-auto px-6 py-12 flex-grow">
        <div className="max-w-7xl mx-auto">
          {/* Page Header */}
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-3 mb-4">
              <Sparkles className="text-blue-400" size={32} />
              <h1 className="text-3xl font-bold vvl-text-primary">{currentCampaign.name}</h1>
            </div>
            <h2 className="text-xl vvl-text-accent font-semibold mb-2">Marketing Proposals</h2>
            <p className="text-lg vvl-text-secondary">AI-generated marketing content and video proposals</p>
          </div>
        
          {!videosGenerated ? (
            <>
              <div className="vvl-card p-6 mb-8">
                <p className="vvl-text-secondary text-center">
                  Select marketing ideas that you'd like to generate videos for. You can select multiple ideas to create a comprehensive video campaign.
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
                {generatedIdeas.map(idea => (
                  <MaterialVideoCard 
                    key={idea.id}
                    idea={idea}
                    onSelect={handleSelectIdea}
                  />
                ))}
              </div>
              
              <div className="text-center">
                <div className="vvl-card p-8 inline-block">
                  <h3 className="text-lg font-semibold vvl-text-primary mb-4">
                    Ready to Generate Videos?
                  </h3>
                  <p className="vvl-text-secondary mb-6">
                    {selectedIdeas.length > 0 
                      ? `${selectedIdeas.length} ideas selected for video generation`
                      : 'Select ideas above or generate videos for all ideas'
                    }
                  </p>
                  <button
                    onClick={handleGenerateVideos}
                    disabled={isLoading}
                    className="vvl-button-primary text-lg px-8 py-4 flex items-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Video size={20} />
                    {isLoading 
                      ? 'Generating Videos...' 
                      : `Generate ${selectedIdeas.length || 'All'} Videos`}
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              <div className="lg:col-span-8">
                <div className="vvl-card p-6 mb-8">
                  <h2 className="text-2xl font-bold vvl-text-primary mb-2">Generated Videos</h2>
                  <p className="vvl-text-secondary">Your AI-generated marketing videos are ready for review and download</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  {(selectedIdeas.length > 0 ? selectedIdeas : generatedIdeas).map(idea => (
                    <MaterialVideoCard 
                      key={idea.id}
                      idea={idea}
                      showVideo={true}
                    />
                  ))}
                </div>
              </div>
              
              <div className="lg:col-span-4">
                <div className="vvl-card sticky top-4">
                  <div className="p-6 border-b border-white/20">
                    <h3 className="font-semibold vvl-text-primary">Social Media Preview</h3>
                    <p className="text-sm vvl-text-secondary mt-1">How your content will appear on different platforms</p>
                  </div>
                  <div className="p-6 space-y-6">
                    <div>
                      <h4 className="text-sm font-semibold vvl-text-primary mb-2 flex items-center gap-2">
                        💼 LinkedIn Post
                      </h4>
                      <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
                        <p className="text-sm vvl-text-secondary">
                          {selectedIdeas[0]?.platforms?.linkedin || generatedIdeas[0]?.platforms?.linkedin || "LinkedIn post content would appear here with professional tone and industry insights."}
                        </p>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-semibold vvl-text-primary mb-2 flex items-center gap-2">
                        🐦 Twitter Post
                      </h4>
                      <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
                        <p className="text-sm vvl-text-secondary">
                          {selectedIdeas[0]?.platforms?.twitter || generatedIdeas[0]?.platforms?.twitter || "Twitter post content would appear here with concise messaging and hashtags."}
                        </p>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-semibold vvl-text-primary mb-2 flex items-center gap-2">
                        📸 Instagram Caption
                      </h4>
                      <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
                        <p className="text-sm vvl-text-secondary">
                          {selectedIdeas[0]?.platforms?.instagram || generatedIdeas[0]?.platforms?.instagram || "Instagram caption would appear here with visual storytelling and engaging hashtags."}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProposalsPage;
