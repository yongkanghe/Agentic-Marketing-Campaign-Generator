/**
 * FILENAME: IdeationPage.tsx
 * DESCRIPTION/PURPOSE: Social media post ideation and generation page with VVL design system styling
 * Author: JP + 2025-06-15
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMarketingContext } from '@/contexts/MarketingContext';
import { MaterialVideoCard } from '@/components/MaterialVideoCard';
import { Textarea } from '@/components/ui/textarea';
import { ArrowLeft, ArrowRight, Sparkles, RefreshCw, Heart, MessageCircle, Share, ExternalLink, Image, Video, Hash, Calendar, Home, Wand2 } from 'lucide-react';
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
  const [selectedPosts, setSelectedPosts] = useState<string[]>([]);
  const [suggestedHashtags, setSuggestedHashtags] = useState<string[]>([
    '#marketing', '#business', '#growth', '#innovation', '#success', '#entrepreneur'
  ]);
  
  // Mock social media columns data
  const [socialMediaColumns, setSocialMediaColumns] = useState([
    {
      id: 'text-only',
      title: 'Text + URL Posts',
      description: 'Marketing text with product URL for link unfurling',
      mediaType: 'text-only' as const,
      posts: [],
      isGenerating: false
    },
    {
      id: 'text-image',
      title: 'Text + Image Posts',
      description: 'Shortened text with AI-generated images',
      mediaType: 'text-with-image' as const,
      posts: [],
      isGenerating: false
    },
    {
      id: 'text-video',
      title: 'Text + Video Posts',
      description: 'Marketing text with AI-generated videos',
      mediaType: 'text-with-video' as const,
      posts: [],
      isGenerating: false
    }
  ]);
  
  useEffect(() => {
    if (!currentCampaign) {
      navigate('/');
      return;
    }
    
    if (currentCampaign.preferredDesign) {
      setPreferredDesign(currentCampaign.preferredDesign);
    }
    
    // Auto-generate initial posts when page loads
    generateAllPosts();
  }, [currentCampaign, navigate]);

  const generateAllPosts = async () => {
    if (selectedThemes.length === 0 || selectedTags.length === 0) {
      // Use default selections for quick start
      if (suggestedThemes.length > 0) selectTheme(suggestedThemes[0]);
      if (suggestedTags.length > 0) selectTag(suggestedTags[0]);
    }
    
    // Generate posts for all columns
    await Promise.all([
      generateColumnPosts('text-only'),
      generateColumnPosts('text-image'),
      generateColumnPosts('text-video')
    ]);
  };

  const generateColumnPosts = async (columnId: string) => {
    setSocialMediaColumns(prev => prev.map(col => 
      col.id === columnId ? { ...col, isGenerating: true } : col
    ));
    
    try {
      // Mock post generation - would be replaced with real API calls
      const mockPosts = Array(5).fill(null).map((_, idx) => ({
        id: `${columnId}-post-${Date.now()}-${idx}`,
        type: columnId as 'text-only' | 'text-with-image' | 'text-with-video',
        platform: 'linkedin' as const,
        content: {
          text: generateMockPostText(columnId, idx),
          hashtags: suggestedHashtags.slice(0, 3),
          imageUrl: columnId === 'text-image' ? `https://via.placeholder.com/400x300?text=Image+${idx + 1}` : undefined,
          videoUrl: columnId === 'text-video' ? `https://placeholder-videos.s3.amazonaws.com/sample${idx + 1}.mp4` : undefined,
          productUrl: columnId === 'text-only' ? currentCampaign?.productServiceUrl || 'https://example.com/product' : undefined
        },
        generationPrompt: `Generate ${columnId} post for ${currentCampaign?.campaignType} campaign about ${currentCampaign?.objective}`,
        selected: false
      }));
      
      setSocialMediaColumns(prev => prev.map(col => 
        col.id === columnId ? { ...col, posts: mockPosts, isGenerating: false } : col
      ));
      
    } catch (error) {
      toast.error(`Failed to generate ${columnId} posts`);
      setSocialMediaColumns(prev => prev.map(col => 
        col.id === columnId ? { ...col, isGenerating: false } : col
      ));
    }
  };

  const generateMockPostText = (type: string, index: number) => {
    const baseTexts = {
      'text-only': [
        `🚀 Exciting news! We're launching something amazing that will transform how you ${currentCampaign?.objective}. Check out the details below and let us know what you think!`,
        `💡 Innovation meets excellence in our latest offering. Designed specifically for businesses looking to ${currentCampaign?.objective}. What's your biggest challenge in this area?`,
        `🎯 Ready to take your business to the next level? Our new solution addresses exactly what you need to ${currentCampaign?.objective}. Link in comments!`,
        `✨ Behind the scenes: Here's how we're helping companies like yours ${currentCampaign?.objective}. The results speak for themselves.`,
        `🔥 Game-changer alert! This is what happens when innovation meets real business needs. Perfect for anyone looking to ${currentCampaign?.objective}.`
      ],
      'text-image': [
        `🎨 Visual storytelling at its finest! See how we're revolutionizing ${currentCampaign?.campaignType} marketing.`,
        `📸 A picture is worth a thousand words. Here's our approach to ${currentCampaign?.objective}.`,
        `🌟 Sneak peek at what's coming! This is how we're changing the game.`,
        `💫 Design meets functionality. Check out this amazing visual representation.`,
        `🎭 Creative meets strategic. This image tells our whole story.`
      ],
      'text-video': [
        `🎬 Watch this! 60 seconds that will change how you think about ${currentCampaign?.objective}.`,
        `📹 Video speaks louder than words. See our solution in action!`,
        `🎥 Behind the scenes: The making of something extraordinary.`,
        `🎪 Lights, camera, action! Here's our story in motion.`,
        `🎨 Motion graphics meet real results. Watch the magic happen.`
      ]
    };
    
    return baseTexts[type as keyof typeof baseTexts][index] || `Great content for ${type} post ${index + 1}`;
  };

  const togglePostSelection = (postId: string) => {
    setSelectedPosts(prev => 
      prev.includes(postId) 
        ? prev.filter(id => id !== postId)
        : [...prev, postId]
    );
  };

  const regeneratePost = async (columnId: string, postId: string) => {
    // Regenerate single post
    toast.success('Regenerating post...');
    // TODO: Implement single post regeneration
  };

  const handleProceedToScheduling = () => {
    if (selectedPosts.length === 0) {
      toast.error('Please select at least one post to proceed');
      return;
    }
    
    toast.success(`${selectedPosts.length} posts selected for scheduling!`);
    navigate('/scheduling');
  };
  
  if (!currentCampaign) return null;
  
  return (
    <div className="min-h-screen vvl-gradient-bg flex flex-col">
      {/* Header */}
      <header className="vvl-header-blur">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center gap-3">
                <Wand2 className="text-blue-400" size={24} />
                <h1 className="text-xl font-bold vvl-text-primary">Social Media Post Generator</h1>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button 
                onClick={() => navigate('/')}
                className="vvl-button-secondary text-sm flex items-center gap-2"
              >
                <Home size={16} />
                Dashboard
              </button>
              <button 
                onClick={() => navigate('/')}
                className="vvl-button-secondary text-sm flex items-center gap-2"
              >
                <ArrowLeft size={16} />
                Back
              </button>
            </div>
          </div>
        </div>
      </header>
      
      <div className="container mx-auto px-6 py-12 flex-grow">
        <div className="max-w-7xl mx-auto">
          {/* Campaign Summary */}
          <div className="vvl-card p-6 mb-8">
            <div className="flex items-center gap-3 vvl-text-primary mb-4">
              <Sparkles size={24} className="text-blue-400" />
              <h2 className="text-2xl font-bold">AI Campaign Summary</h2>
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold vvl-text-primary mb-2">{currentCampaign.name}</h3>
                <p className="vvl-text-secondary mb-4">{currentCampaign.objective}</p>
                <div className="flex flex-wrap gap-2">
                  <span className="text-xs bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full">
                    {currentCampaign.campaignType}
                  </span>
                  <span className="text-xs bg-purple-500/20 text-purple-400 px-3 py-1 rounded-full">
                    Creativity: {currentCampaign.creativityLevel}/10
                  </span>
                </div>
              </div>
              <div>
                <h4 className="text-sm font-semibold vvl-text-primary mb-2">AI Analysis</h4>
                <p className="text-sm vvl-text-secondary">
                  {aiSummary || "AI is analyzing your campaign requirements to generate targeted content that resonates with your audience and achieves your marketing objectives."}
                </p>
              </div>
            </div>
          </div>

          {/* Theme and Tag Selection */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <div className="vvl-card p-6">
              <h3 className="text-lg font-semibold vvl-text-primary mb-4">Suggested Themes</h3>
              <div className="flex flex-wrap gap-2">
                {suggestedThemes.map(theme => (
                  <button
                    key={theme}
                    onClick={() => selectedThemes.includes(theme) ? unselectTheme(theme) : selectTheme(theme)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      selectedThemes.includes(theme)
                        ? 'bg-blue-500/30 text-blue-400 border border-blue-400'
                        : 'bg-white/5 text-gray-300 border border-white/20 hover:bg-white/10'
                    }`}
                  >
                    {theme}
                  </button>
                ))}
              </div>
            </div>

            <div className="vvl-card p-6">
              <h3 className="text-lg font-semibold vvl-text-primary mb-4">Suggested Tags</h3>
              <div className="flex flex-wrap gap-2">
                {suggestedTags.map(tag => (
                  <button
                    key={tag}
                    onClick={() => selectedTags.includes(tag) ? unselectTag(tag) : selectTag(tag)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      selectedTags.includes(tag)
                        ? 'bg-purple-500/30 text-purple-400 border border-purple-400'
                        : 'bg-white/5 text-gray-300 border border-white/20 hover:bg-white/10'
                    }`}
                  >
                    #{tag}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Design Preferences */}
          <div className="vvl-card p-6 mb-8">
            <h3 className="text-lg font-semibold vvl-text-primary mb-4">Design Preferences (Optional)</h3>
            <Textarea
              placeholder="Describe your preferred visual style, colors, mood, or any specific design requirements..."
              value={preferredDesign}
              onChange={(e) => setPreferredDesign(e.target.value)}
              className="vvl-input min-h-[100px] resize-none"
            />
          </div>

          {/* Social Media Post Columns */}
          <div className="grid lg:grid-cols-3 gap-8 mb-8">
            {socialMediaColumns.map(column => (
              <div key={column.id} className="vvl-card">
                <div className="p-6 border-b border-white/20">
                  <div className="flex items-center gap-3 mb-2">
                    {column.id === 'text-only' && <Hash className="text-blue-400" size={20} />}
                    {column.id === 'text-image' && <Image className="text-green-400" size={20} />}
                    {column.id === 'text-video' && <Video className="text-purple-400" size={20} />}
                    <h3 className="font-semibold vvl-text-primary">{column.title}</h3>
                  </div>
                  <p className="text-sm vvl-text-secondary">{column.description}</p>
                  <button
                    onClick={() => generateColumnPosts(column.id)}
                    disabled={column.isGenerating}
                    className="mt-4 vvl-button-secondary text-sm flex items-center gap-2 w-full justify-center disabled:opacity-50"
                  >
                    <RefreshCw size={14} className={column.isGenerating ? 'animate-spin' : ''} />
                    {column.isGenerating ? 'Generating...' : 'Regenerate'}
                  </button>
                </div>
                
                <div className="p-4 space-y-4 max-h-96 overflow-y-auto">
                  {column.posts.map((post: any) => (
                    <div key={post.id} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-grow">
                          <p className="text-sm vvl-text-secondary mb-3 line-clamp-3">{post.content.text}</p>
                          
                          {post.content.imageUrl && (
                            <img 
                              src={post.content.imageUrl} 
                              alt="Generated content" 
                              className="w-full h-32 object-cover rounded mb-3"
                            />
                          )}
                          
                          {post.content.hashtags && (
                            <div className="flex flex-wrap gap-1 mb-3">
                              {post.content.hashtags.map((tag: string, idx: number) => (
                                <span key={idx} className="text-xs text-blue-400">#{tag.replace('#', '')}</span>
                              ))}
                            </div>
                          )}
                        </div>
                        
                        <button
                          onClick={() => togglePostSelection(post.id)}
                          className={`ml-3 p-2 rounded-lg transition-all duration-200 ${
                            selectedPosts.includes(post.id)
                              ? 'bg-blue-500/30 text-blue-400'
                              : 'bg-white/5 text-gray-400 hover:bg-white/10'
                          }`}
                        >
                          <Heart size={16} className={selectedPosts.includes(post.id) ? 'fill-current' : ''} />
                        </button>
                      </div>
                      
                      <div className="flex items-center justify-between text-xs vvl-text-secondary">
                        <div className="flex items-center gap-4">
                          <span className="flex items-center gap-1">
                            <Heart size={12} />
                            {Math.floor(Math.random() * 100) + 10}
                          </span>
                          <span className="flex items-center gap-1">
                            <MessageCircle size={12} />
                            {Math.floor(Math.random() * 20) + 2}
                          </span>
                          <span className="flex items-center gap-1">
                            <Share size={12} />
                            {Math.floor(Math.random() * 10) + 1}
                          </span>
                        </div>
                        <button
                          onClick={() => regeneratePost(column.id, post.id)}
                          className="text-blue-400 hover:text-blue-300 transition-colors"
                        >
                          <RefreshCw size={12} />
                        </button>
                      </div>
                    </div>
                  ))}
                  
                  {column.posts.length === 0 && !column.isGenerating && (
                    <div className="text-center py-8 vvl-text-secondary">
                      <p className="text-sm">No posts generated yet</p>
                      <p className="text-xs mt-1">Click "Regenerate" to create content</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Action Bar */}
          <div className="vvl-card p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="vvl-text-primary font-medium">
                  {selectedPosts.length} posts selected
                </span>
                {selectedPosts.length > 0 && (
                  <span className="text-sm vvl-text-secondary">
                    Ready for scheduling and publishing
                  </span>
                )}
              </div>
              
              <div className="flex items-center gap-3">
                <button
                  onClick={generateAllPosts}
                  disabled={isLoading}
                  className="vvl-button-secondary flex items-center gap-2"
                >
                  <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
                  {isLoading ? 'Generating...' : 'Regenerate All'}
                </button>
                
                <button
                  onClick={handleProceedToScheduling}
                  disabled={selectedPosts.length === 0}
                  className="vvl-button-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ArrowRight size={16} />
                  Proceed to Scheduling ({selectedPosts.length})
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IdeationPage;
