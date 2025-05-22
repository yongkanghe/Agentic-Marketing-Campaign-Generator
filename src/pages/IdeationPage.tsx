
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMarketingContext } from '@/contexts/MarketingContext';
import { MaterialCard } from '@/components/MaterialCard';
import { MaterialButton } from '@/components/MaterialButton';
import { MaterialTag } from '@/components/MaterialTag';
import { MaterialAppBar } from '@/components/MaterialAppBar';
import { Textarea } from '@/components/ui/textarea';
import { ArrowLeft, ArrowRight, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

const IdeationPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    currentCampaign,
    aiSummary,
    suggestedThemes,
    suggestedTags,
    selectedThemes,
    selectedTags,
    selectTheme,
    unselectTheme,
    selectTag,
    unselectTag,
    updateCurrentCampaign,
    generateIdeas
  } = useMarketingContext();
  
  const [preferredDesign, setPreferredDesign] = useState(currentCampaign?.preferredDesign || '');
  const [isLoading, setIsLoading] = useState(false);
  
  useEffect(() => {
    if (!currentCampaign) {
      navigate('/');
      return;
    }
    
    if (currentCampaign.preferredDesign) {
      setPreferredDesign(currentCampaign.preferredDesign);
    }
  }, [currentCampaign, navigate]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (selectedThemes.length === 0 || selectedTags.length === 0) {
      toast.error('Please select at least one theme and one tag');
      return;
    }
    
    setIsLoading(true);
    
    // Update the campaign with preferred design
    if (preferredDesign !== currentCampaign?.preferredDesign) {
      updateCurrentCampaign({ preferredDesign });
    }
    
    try {
      // Generate ideas based on selected themes and tags
      await generateIdeas();
      navigate('/proposals');
    } catch (error) {
      toast.error('Failed to generate ideas. Please try again.');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };
  
  if (!currentCampaign) return null;
  
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <MaterialAppBar title="Campaign Ideation">
        <MaterialButton 
          variant="text" 
          className="mr-2 flex items-center gap-1"
          onClick={() => navigate('/')}
        >
          <ArrowLeft size={16} />
          <span>Back</span>
        </MaterialButton>
      </MaterialAppBar>
      
      <div className="container py-8">
        <div className="max-w-4xl mx-auto">
          <MaterialCard className="mb-6 p-6">
            <div className="flex items-center gap-2 text-material-primary mb-4">
              <Sparkles size={20} />
              <h2 className="text-lg font-medium">AI Summary</h2>
            </div>
            <div className="bg-material-primary/5 p-4 rounded-md">
              <p className="text-sm">{aiSummary || "AI will generate a summary based on your business description and objective."}</p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-6 mt-6">
              <div>
                <h3 className="font-medium mb-3">Campaign Name</h3>
                <p className="text-sm bg-muted p-2 rounded">{currentCampaign.name}</p>
              </div>
              <div>
                <h3 className="font-medium mb-3">Campaign Objective</h3>
                <p className="text-sm bg-muted p-2 rounded">{currentCampaign.objective}</p>
              </div>
            </div>
          </MaterialCard>
          
          <form onSubmit={handleSubmit}>
            <MaterialCard className="mb-6 p-6">
              <h2 className="text-lg font-medium mb-4">Suggested Themes</h2>
              <p className="text-sm text-muted-foreground mb-4">
                Select themes that match the look and feel you want for your marketing content.
              </p>
              
              <div className="flex flex-wrap gap-2 mb-6">
                {suggestedThemes.map(theme => (
                  <MaterialTag
                    key={theme}
                    label={theme}
                    selected={selectedThemes.includes(theme)}
                    onClick={() => 
                      selectedThemes.includes(theme)
                        ? unselectTheme(theme)
                        : selectTheme(theme)
                    }
                  />
                ))}
              </div>
              
              <h2 className="text-lg font-medium mb-4">Suggested Tags</h2>
              <p className="text-sm text-muted-foreground mb-4">
                Select tags that represent the key topics and keywords for your campaign.
              </p>
              
              <div className="flex flex-wrap gap-2">
                {suggestedTags.map(tag => (
                  <MaterialTag
                    key={tag}
                    label={tag}
                    selected={selectedTags.includes(tag)}
                    onClick={() => 
                      selectedTags.includes(tag)
                        ? unselectTag(tag)
                        : selectTag(tag)
                    }
                  />
                ))}
              </div>
            </MaterialCard>
            
            <MaterialCard className="mb-6 p-6">
              <h2 className="text-lg font-medium mb-4">Preferred Design Language (Optional)</h2>
              <p className="text-sm text-muted-foreground mb-4">
                Describe any specific design preferences, visual styles, or brand guidelines you'd like the AI to follow.
              </p>
              
              <Textarea
                value={preferredDesign}
                onChange={(e) => setPreferredDesign(e.target.value)}
                placeholder="E.g., Minimalist design, bright colors, product-focused, etc."
                className="min-h-[100px]"
              />
            </MaterialCard>
            
            <div className="flex justify-between mt-8">
              <MaterialButton
                type="button"
                variant="outline"
                onClick={() => navigate('/')}
                className="flex items-center gap-2"
              >
                <ArrowLeft size={16} />
                <span>Back</span>
              </MaterialButton>
              
              <MaterialButton 
                type="submit"
                disabled={isLoading}
                className="flex items-center gap-2"
              >
                <span>{isLoading ? 'Generating...' : 'Generate Ideas'}</span>
                <ArrowRight size={16} />
              </MaterialButton>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default IdeationPage;
