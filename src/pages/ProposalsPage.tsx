
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMarketingContext } from '@/contexts/MarketingContext';
import { MaterialCard } from '@/components/MaterialCard';
import { MaterialButton } from '@/components/MaterialButton';
import { MaterialAppBar } from '@/components/MaterialAppBar';
import { MaterialVideoCard } from '@/components/MaterialVideoCard';
import { ArrowLeft, FileText, Video, Download } from 'lucide-react';
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
    <div className="min-h-screen bg-background flex flex-col">
      <MaterialAppBar title="Marketing Proposals">
        <MaterialButton 
          variant="text" 
          className="mr-2 flex items-center gap-1"
          onClick={() => navigate('/')}
        >
          <ArrowLeft size={16} />
          <span>Dashboard</span>
        </MaterialButton>
        
        <MaterialButton 
          variant="text" 
          className="mr-2 flex items-center gap-1"
          onClick={() => navigate('/ideation')}
        >
          <ArrowLeft size={16} />
          <span>Back to Ideation</span>
        </MaterialButton>
      </MaterialAppBar>
      
      <div className="container py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-medium">{currentCampaign.name} - Proposals</h1>
          <div className="flex gap-2">
            <MaterialButton
              variant="outline"
              className="flex items-center gap-2"
              onClick={exportToText}
            >
              <FileText size={18} />
              <span>Export to Text</span>
            </MaterialButton>
            
            {!videosGenerated && (
              <MaterialButton
                variant="primary"
                className="flex items-center gap-2"
                onClick={handleGenerateVideos}
                disabled={isLoading}
              >
                <Video size={18} />
                <span>{isLoading ? 'Generating...' : 'Generate Videos'}</span>
              </MaterialButton>
            )}
            
            {videosGenerated && (
              <MaterialButton
                variant="primary"
                className="flex items-center gap-2"
                onClick={() => toast.success('Videos downloaded successfully!')}
              >
                <Download size={18} />
                <span>Download All Videos</span>
              </MaterialButton>
            )}
          </div>
        </div>
        
        {!videosGenerated ? (
          <>
            <p className="text-muted-foreground mb-6">
              Select marketing ideas that you'd like to generate videos for. You can select multiple ideas.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {generatedIdeas.map(idea => (
                <MaterialVideoCard 
                  key={idea.id}
                  idea={idea}
                  onSelect={handleSelectIdea}
                />
              ))}
            </div>
            
            <div className="mt-8 flex justify-center">
              <MaterialButton
                variant="primary"
                size="lg"
                className="flex items-center gap-2"
                onClick={handleGenerateVideos}
                disabled={isLoading || selectedIdeas.length === 0}
              >
                <Video size={18} />
                <span>
                  {isLoading 
                    ? 'Generating...' 
                    : `Generate ${selectedIdeas.length || 'All'} Videos`}
                </span>
              </MaterialButton>
            </div>
          </>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-8">
              <h2 className="text-xl font-medium mb-4">Generated Videos</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
              <MaterialCard className="sticky top-4">
                <div className="p-4 border-b">
                  <h3 className="font-medium">Social Media Preview</h3>
                </div>
                <div className="p-4">
                  <h4 className="text-sm font-medium mb-2">LinkedIn Post</h4>
                  <p className="text-sm text-muted-foreground bg-muted p-3 rounded mb-4">
                    {selectedIdeas[0]?.platforms?.linkedin || generatedIdeas[0]?.platforms?.linkedin || "LinkedIn post content would appear here."}
                  </p>
                  
                  <h4 className="text-sm font-medium mb-2">Twitter Post</h4>
                  <p className="text-sm text-muted-foreground bg-muted p-3 rounded mb-4">
                    {selectedIdeas[0]?.platforms?.twitter || generatedIdeas[0]?.platforms?.twitter || "Twitter post content would appear here."}
                  </p>
                  
                  <h4 className="text-sm font-medium mb-2">Instagram Caption</h4>
                  <p className="text-sm text-muted-foreground bg-muted p-3 rounded mb-4">
                    {selectedIdeas[0]?.platforms?.instagram || generatedIdeas[0]?.platforms?.instagram || "Instagram caption would appear here."}
                  </p>
                </div>
              </MaterialCard>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProposalsPage;
