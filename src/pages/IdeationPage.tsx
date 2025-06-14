import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMarketingContext } from '@/contexts/MarketingContext';
import { MaterialCard } from '@/components/MaterialCard';
import { MaterialButton } from '@/components/MaterialButton';
import { MaterialTag } from '@/components/MaterialTag';
import { MaterialAppBar } from '@/components/MaterialAppBar';
import { Textarea } from '@/components/ui/textarea';
import { ArrowLeft, ArrowRight, Sparkles, RefreshCw, Heart, MessageCircle, Share, ExternalLink, Image, Video, Hash, Calendar } from 'lucide-react';
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
    <div className="min-h-screen bg-background flex flex-col">
      <MaterialAppBar title="Social Media Post Generator">
        <MaterialButton 
          variant="outline" 
          className="mr-2 flex items-center gap-1"
          onClick={() => navigate('/')}
        >
          <ArrowLeft size={16} />
          <span>Back</span>
        </MaterialButton>
      </MaterialAppBar>
      
      <div className="container py-8">
        <div className="max-w-7xl mx-auto">
          {/* Campaign Summary */}
          <MaterialCard className="mb-6 p-6">
            <div className="flex items-center gap-2 text-material-primary mb-4">
              <Sparkles size={20} />
              <h2 className="text-lg font-medium">AI Campaign Summary</h2>
            </div>
            <div className="bg-material-primary/5 p-4 rounded-md mb-4">
              <p className="text-sm">{aiSummary || "AI will generate a summary based on your business description and objective."}</p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-4">
              <div>
                <h3 className="font-medium mb-2">Campaign: {currentCampaign.name}</h3>
                <p className="text-sm text-muted-foreground">{currentCampaign.objective}</p>
              </div>
              <div>
                <h3 className="font-medium mb-2">Selected Themes</h3>
                <div className="flex flex-wrap gap-1">
                  {selectedThemes.map(theme => (
                    <span key={theme} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      {theme}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="font-medium mb-2">Selected Tags</h3>
                <div className="flex flex-wrap gap-1">
                  {selectedTags.map(tag => (
                    <span key={tag} className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </MaterialCard>

          {/* Quick Hashtag Selection */}
          <MaterialCard className="mb-6 p-6">
            <div className="flex items-center gap-2 mb-4">
              <Hash size={20} />
              <h2 className="text-lg font-medium">Suggested Hashtags</h2>
            </div>
            <div className="flex flex-wrap gap-2">
              {suggestedHashtags.map(hashtag => (
                <MaterialTag
                  key={hashtag}
                  label={hashtag}
                  selected={true}
                  onClick={() => {}}
                />
              ))}
            </div>
          </MaterialCard>

          {/* Social Media Post Columns */}
          <div className="grid lg:grid-cols-3 gap-6 mb-8">
            {socialMediaColumns.map(column => (
              <div key={column.id} className="space-y-4">
                <MaterialCard className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium">{column.title}</h3>
                    <MaterialButton
                      variant="outline"
                      size="sm"
                      onClick={() => generateColumnPosts(column.id)}
                      disabled={column.isGenerating}
                      className="flex items-center gap-1"
                    >
                      <RefreshCw size={14} className={column.isGenerating ? 'animate-spin' : ''} />
                      <span>Regenerate</span>
                    </MaterialButton>
                  </div>
                  <p className="text-sm text-muted-foreground mb-4">{column.description}</p>
                  
                  {column.isGenerating ? (
                    <div className="space-y-3">
                      {Array(3).fill(null).map((_, idx) => (
                        <div key={idx} className="animate-pulse">
                          <div className="h-4 bg-gray-200 rounded mb-2"></div>
                          <div className="h-3 bg-gray-200 rounded w-3/4"></div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {column.posts.map(post => (
                        <div
                          key={post.id}
                          className={`p-3 border rounded-lg cursor-pointer transition-all ${
                            selectedPosts.includes(post.id)
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                          onClick={() => togglePostSelection(post.id)}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              {post.type === 'text-with-image' && <Image size={14} className="text-green-600" />}
                              {post.type === 'text-with-video' && <Video size={14} className="text-purple-600" />}
                              {post.type === 'text-only' && <ExternalLink size={14} className="text-blue-600" />}
                            </div>
                            <MaterialButton
                              variant="outline"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                regeneratePost(column.id, post.id);
                              }}
                              className="opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                              <RefreshCw size={12} />
                            </MaterialButton>
                          </div>
                          
                          <p className="text-sm mb-2">{post.content.text}</p>
                          
                          {post.content.imageUrl && (
                            <img 
                              src={post.content.imageUrl} 
                              alt="Post preview" 
                              className="w-full h-24 object-cover rounded mb-2"
                            />
                          )}
                          
                          {post.content.videoUrl && (
                            <div className="w-full h-24 bg-gray-100 rounded mb-2 flex items-center justify-center">
                              <Video size={24} className="text-gray-400" />
                            </div>
                          )}
                          
                          {post.content.productUrl && (
                            <div className="text-xs text-blue-600 mb-2">
                              🔗 {post.content.productUrl}
                            </div>
                          )}
                          
                          <div className="flex items-center justify-between text-xs text-muted-foreground">
                            <div className="flex gap-3">
                              <span className="flex items-center gap-1">
                                <Heart size={12} /> 24
                              </span>
                              <span className="flex items-center gap-1">
                                <MessageCircle size={12} /> 8
                              </span>
                              <span className="flex items-center gap-1">
                                <Share size={12} /> 3
                              </span>
                            </div>
                            <div className="flex gap-1">
                              {post.content.hashtags.map(tag => (
                                <span key={tag} className="text-blue-600">{tag}</span>
                              ))}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </MaterialCard>
              </div>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between items-center">
            <div className="text-sm text-muted-foreground">
              {selectedPosts.length} posts selected
            </div>
            
            <div className="flex gap-4">
              <MaterialButton
                variant="outline"
                onClick={() => navigate('/new')}
                className="flex items-center gap-2"
              >
                <ArrowLeft size={16} />
                <span>Back to Campaign</span>
              </MaterialButton>
              
              <MaterialButton
                onClick={handleProceedToScheduling}
                disabled={selectedPosts.length === 0}
                className="flex items-center gap-2"
              >
                <Calendar size={16} />
                <span>Schedule Selected Posts ({selectedPosts.length})</span>
                <ArrowRight size={16} />
              </MaterialButton>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IdeationPage;
