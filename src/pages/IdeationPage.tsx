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
  const [isRegeneratingAnalysis, setIsRegeneratingAnalysis] = useState(false);
  
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
    
    // Only auto-generate Text+URL posts on page load (basic tier)
    // Enhanced and Premium content requires user action
    await generateColumnPosts('text-only');
  };

  const generateColumnPosts = async (columnId: string) => {
    setSocialMediaColumns(prev => prev.map(col => 
      col.id === columnId ? { ...col, isGenerating: true } : col
    ));
    
    try {
      // Real API call to backend for content generation
      const postType = columnId === 'text-only' ? 'text_url' : 
                      columnId === 'text-image' ? 'text_image' : 'text_video';
      
      const response = await fetch('/api/v1/content/regenerate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          post_type: postType,
          regenerate_count: 5,
          business_context: {
            company_name: currentCampaign?.name || 'Your Company',
            objective: currentCampaign?.objective || 'increase sales',
            campaign_type: currentCampaign?.campaignType || 'service',
            target_audience: 'business professionals', // TODO: Add target_audience to Campaign interface
            business_description: currentCampaign?.businessDescription || '',
            business_website: currentCampaign?.businessUrl || '',
            product_service_url: currentCampaign?.productServiceUrl || ''
          },
          creativity_level: currentCampaign?.creativityLevel || 7
        })
      });

      if (!response.ok) {
        throw new Error(`API call failed: ${response.status}`);
      }

      const data = await response.json();
      
      // Transform API response to match frontend format
      const transformedPosts = data.new_posts.map((post: any, idx: number) => ({
        id: post.id || `${columnId}-post-${Date.now()}-${idx}`,
        type: columnId as 'text-only' | 'text-with-image' | 'text-with-video',
        platform: 'linkedin' as const,
        content: {
          text: post.content || `Generated ${postType.replace('_', ' + ')} content for ${currentCampaign?.objective}`,
          hashtags: post.hashtags || suggestedHashtags.slice(0, 3),
          imageUrl: columnId === 'text-image' ? post.image_url || `https://via.placeholder.com/400x300/4F46E5/FFFFFF?text=AI+Generated+${idx + 1}` : undefined,
          videoUrl: columnId === 'text-video' ? post.video_url || `https://placeholder-videos.s3.amazonaws.com/sample${idx + 1}.mp4` : undefined,
          productUrl: columnId === 'text-only' ? currentCampaign?.productServiceUrl || currentCampaign?.businessUrl || 'https://example.com/product' : undefined
        },
        generationPrompt: `Generate ${columnId} post for ${currentCampaign?.campaignType} campaign about ${currentCampaign?.objective}`,
        selected: false,
        engagement_score: post.engagement_score || (7.0 + idx * 0.1),
        platform_optimized: post.platform_optimized || {}
      }));
      
      setSocialMediaColumns(prev => prev.map(col => 
        col.id === columnId ? { ...col, posts: transformedPosts, isGenerating: false } : col
      ));

      toast.success(`Generated ${transformedPosts.length} ${postType.replace('_', ' + ')} posts successfully!`);
      
    } catch (error) {
      console.error(`Failed to generate ${columnId} posts:`, error);
      
      // Fallback to enhanced mock data on API failure
      const fallbackPosts = Array(5).fill(null).map((_, idx) => ({
        id: `${columnId}-post-${Date.now()}-${idx}`,
        type: columnId as 'text-only' | 'text-with-image' | 'text-with-video',
        platform: 'linkedin' as const,
        content: {
          text: generateMockPostText(columnId, idx),
          hashtags: suggestedHashtags.slice(0, 3),
          imageUrl: columnId === 'text-image' ? `https://via.placeholder.com/400x300/4F46E5/FFFFFF?text=AI+Generated+${idx + 1}` : undefined,
          videoUrl: columnId === 'text-video' ? `https://placeholder-videos.s3.amazonaws.com/sample${idx + 1}.mp4` : undefined,
          productUrl: columnId === 'text-only' ? currentCampaign?.productServiceUrl || currentCampaign?.businessUrl || 'https://example.com/product' : undefined
        },
        generationPrompt: `Generate ${columnId} post for ${currentCampaign?.campaignType} campaign about ${currentCampaign?.objective}`,
        selected: false
      }));
      
      setSocialMediaColumns(prev => prev.map(col => 
        col.id === columnId ? { ...col, posts: fallbackPosts, isGenerating: false } : col
      ));
      
      toast.error(`API unavailable - using enhanced mock content for ${columnId} posts`);
    }
  };

  const generateMockPostText = (type: string, index: number) => {
    const objective = currentCampaign?.objective || 'increase sales';
    const campaignType = currentCampaign?.campaignType || 'service';
    const businessName = currentCampaign?.name || 'Your Business';
    
    const baseTexts = {
      'text-only': [
        `🚀 Exciting news! We're launching something amazing that will transform how you ${objective}. Our innovative ${campaignType} solution has been designed with your success in mind. After months of development and testing, we're ready to share the results with you. Check out the details below and let us know what you think! This could be the game-changer your business has been waiting for.`,
        `💡 Innovation meets excellence in our latest ${campaignType} offering. Designed specifically for businesses looking to ${objective}, this solution addresses the core challenges we've identified in the market. What's your biggest challenge in this area? We'd love to hear from you and show how our approach can make a real difference in your business outcomes.`,
        `🎯 Ready to take your business to the next level? Our new ${campaignType} solution addresses exactly what you need to ${objective}. We've worked with companies just like yours to understand the pain points and create something truly valuable. The early results have been incredible, and we're excited to share this opportunity with you. Link in comments!`,
        `✨ Behind the scenes: Here's how we're helping companies like ${businessName} ${objective}. The results speak for themselves - our clients are seeing measurable improvements in their business metrics. This isn't just another ${campaignType}; it's a comprehensive approach that delivers real value. Want to learn more about how this could work for your business?`,
        `🔥 Game-changer alert! This is what happens when innovation meets real business needs. Perfect for anyone looking to ${objective}, our ${campaignType} solution has been tested and proven in real-world scenarios. The feedback from our beta users has been overwhelmingly positive, and we're confident this can help transform your business too.`
      ],
      'text-image': [
        `🎨 Visual storytelling at its finest! See how we're revolutionizing ${campaignType} marketing with this powerful image that captures the essence of what it means to ${objective}. Every element in this visual has been carefully crafted to communicate our value proposition and connect with businesses like yours. This isn't just a pretty picture - it's a strategic communication tool designed to inspire action.`,
        `📸 A picture is worth a thousand words. Here's our approach to helping businesses ${objective} through innovative ${campaignType} solutions. This image represents months of research, development, and real-world testing. We believe that visual communication is key to understanding complex business solutions, and this image tells the story of transformation and success.`,
        `🌟 Sneak peek at what's coming! This is how we're changing the game for businesses looking to ${objective}. The visual you see here represents our commitment to excellence and innovation in the ${campaignType} space. We're not just talking about change - we're showing you what it looks like when businesses embrace new possibilities.`,
        `💫 Design meets functionality. Check out this amazing visual representation of how our ${campaignType} solution helps businesses ${objective}. Every color, shape, and element has been chosen to communicate our core message: that success is achievable when you have the right tools and approach. This image is just the beginning of what we can accomplish together.`,
        `🎭 Creative meets strategic. This image tells our whole story about helping businesses ${objective} through innovative ${campaignType} solutions. We believe that great design isn't just about aesthetics - it's about communication, connection, and creating meaningful experiences that drive real business results.`
      ],
      'text-video': [
        `🎬 Watch this! 60 seconds that will change how you think about ${objective}. This video showcases our ${campaignType} solution in action, demonstrating real results from real businesses. We've packed this short video with insights, examples, and proof points that show exactly how our approach can transform your business. Don't just take our word for it - see the results for yourself.`,
        `📹 Video speaks louder than words. See our ${campaignType} solution in action and discover how we're helping businesses ${objective} with measurable results. This isn't just a promotional video - it's a demonstration of real value, real solutions, and real outcomes. Watch how other businesses have transformed their operations and achieved their goals.`,
        `🎥 Behind the scenes: The making of something extraordinary. This video takes you inside our process of developing ${campaignType} solutions that help businesses ${objective}. From concept to implementation, you'll see the dedication, innovation, and expertise that goes into every solution we create. This is what happens when passion meets purpose.`,
        `🎪 Lights, camera, action! Here's our story in motion - how we're revolutionizing the way businesses approach ${objective} through innovative ${campaignType} solutions. This video captures the energy, excitement, and results that come from working with a team that truly understands your challenges and has the expertise to solve them.`,
        `🎨 Motion graphics meet real results. Watch the magic happen as we demonstrate how our ${campaignType} solution transforms the way businesses ${objective}. This video combines stunning visuals with compelling data to show you exactly what's possible when you choose the right partner for your business transformation journey.`
      ]
    };
    
    return baseTexts[type as keyof typeof baseTexts][index] || `Comprehensive ${type.replace('-', ' + ')} content for ${businessName} focusing on ${objective} through innovative ${campaignType} solutions. This post demonstrates our commitment to delivering real value and measurable results for businesses like yours.`;
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

  const regenerateAIAnalysis = async () => {
    setIsRegeneratingAnalysis(true);
    try {
      // TODO: Replace with real API call to backend
      // const response = await fetch(`/api/v1/campaigns/${currentCampaign.id}/regenerate-analysis`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' }
      // });
      // const data = await response.json();
      
      // Mock regeneration for now
      await new Promise(resolve => setTimeout(resolve, 2000));
      toast.success('AI analysis regenerated successfully!');
      
      // In real implementation, this would update the aiSummary in context
      // updateAISummary(data.analysis);
      
    } catch (error) {
      toast.error('Failed to regenerate AI analysis');
    } finally {
      setIsRegeneratingAnalysis(false);
    }
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
            <div className="flex items-center gap-3 vvl-text-primary mb-6">
              <Sparkles size={24} className="text-blue-400" />
              <h2 className="text-2xl font-bold">AI Campaign Summary</h2>
            </div>
            
            {/* Campaign Overview */}
            <div className="grid lg:grid-cols-3 gap-6 mb-6">
              <div className="lg:col-span-2">
                <h3 className="text-lg font-semibold vvl-text-primary mb-3">{currentCampaign.name}</h3>
                <p className="vvl-text-secondary mb-4 text-sm leading-relaxed">{currentCampaign.objective}</p>
                
                {/* Campaign Configuration */}
                <div className="grid md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <h4 className="text-sm font-semibold vvl-text-primary mb-2">Campaign Type</h4>
                    <span className="text-xs bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full">
                      {currentCampaign.campaignType || 'General'}
                    </span>
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold vvl-text-primary mb-2">AI Creativity Level</h4>
                    <span className="text-xs bg-purple-500/20 text-purple-400 px-3 py-1 rounded-full">
                      Level {currentCampaign.creativityLevel || 7}/10
                    </span>
                  </div>
                </div>

                {/* Business Information */}
                {currentCampaign.businessDescription && (
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold vvl-text-primary mb-2">Business Context</h4>
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-3">
                      <p className="text-sm vvl-text-secondary leading-relaxed">
                        {currentCampaign.businessDescription}
                      </p>
                    </div>
                  </div>
                )}

                {/* URLs Analyzed */}
                {(currentCampaign.businessUrl || currentCampaign.aboutPageUrl || currentCampaign.productServiceUrl) && (
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold vvl-text-primary mb-2">URLs Analyzed</h4>
                    <div className="space-y-2">
                      {currentCampaign.businessUrl && (
                        <div className="flex items-center gap-2 text-xs">
                          <ExternalLink size={12} className="text-blue-400" />
                          <span className="vvl-text-secondary">Business:</span>
                          <a href={currentCampaign.businessUrl} target="_blank" rel="noopener noreferrer" 
                             className="text-blue-400 hover:text-blue-300 truncate max-w-xs">
                            {currentCampaign.businessUrl}
                          </a>
                        </div>
                      )}
                      {currentCampaign.aboutPageUrl && (
                        <div className="flex items-center gap-2 text-xs">
                          <ExternalLink size={12} className="text-green-400" />
                          <span className="vvl-text-secondary">About:</span>
                          <a href={currentCampaign.aboutPageUrl} target="_blank" rel="noopener noreferrer" 
                             className="text-green-400 hover:text-green-300 truncate max-w-xs">
                            {currentCampaign.aboutPageUrl}
                          </a>
                        </div>
                      )}
                      {currentCampaign.productServiceUrl && (
                        <div className="flex items-center gap-2 text-xs">
                          <ExternalLink size={12} className="text-purple-400" />
                          <span className="vvl-text-secondary">Product/Service:</span>
                          <a href={currentCampaign.productServiceUrl} target="_blank" rel="noopener noreferrer" 
                             className="text-purple-400 hover:text-purple-300 truncate max-w-xs">
                            {currentCampaign.productServiceUrl}
                          </a>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Uploaded Assets */}
                {(currentCampaign.uploadedImages?.length || currentCampaign.uploadedDocuments?.length || currentCampaign.campaignAssets?.length) && (
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold vvl-text-primary mb-2">Uploaded Assets</h4>
                    <div className="grid grid-cols-3 gap-4">
                      {currentCampaign.uploadedImages?.length > 0 && (
                        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-3 text-center">
                          <Image size={16} className="text-green-400 mx-auto mb-1" />
                          <p className="text-xs vvl-text-secondary">Product/Brand Images</p>
                          <p className="text-xs text-green-400 font-medium">{currentCampaign.uploadedImages.length} files</p>
                        </div>
                      )}
                      {currentCampaign.uploadedDocuments?.length > 0 && (
                        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-3 text-center">
                          <Hash size={16} className="text-blue-400 mx-auto mb-1" />
                          <p className="text-xs vvl-text-secondary">Documents & Specs</p>
                          <p className="text-xs text-blue-400 font-medium">{currentCampaign.uploadedDocuments.length} files</p>
                        </div>
                      )}
                      {currentCampaign.campaignAssets?.length > 0 && (
                        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-3 text-center">
                          <Video size={16} className="text-purple-400 mx-auto mb-1" />
                          <p className="text-xs vvl-text-secondary">Campaign Assets</p>
                          <p className="text-xs text-purple-400 font-medium">{currentCampaign.campaignAssets.length} files</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Example Content */}
                {currentCampaign.exampleContent && (
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold vvl-text-primary mb-2">Example Content Reference</h4>
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-3">
                      <p className="text-sm vvl-text-secondary leading-relaxed">
                        {currentCampaign.exampleContent}
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* AI Analysis Panel */}
              <div className="lg:col-span-1">
                <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 backdrop-blur-sm border border-blue-400/20 rounded-lg p-4">
                  <h4 className="text-sm font-semibold vvl-text-primary mb-3 flex items-center gap-2">
                    <Sparkles size={16} className="text-blue-400" />
                    AI Analysis
                  </h4>
                  <p className="text-sm vvl-text-secondary leading-relaxed mb-4">
                    {aiSummary || "AI-generated summary of campaign targeting get more sales based on the provided business description. This would be generated by Gemini in a real implementation."}
                  </p>
                  
                  {/* Analysis Metrics */}
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-xs vvl-text-secondary">Content Relevance</span>
                      <span className="text-xs text-green-400 font-medium">High</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs vvl-text-secondary">Brand Alignment</span>
                      <span className="text-xs text-blue-400 font-medium">Excellent</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs vvl-text-secondary">Target Audience Fit</span>
                      <span className="text-xs text-purple-400 font-medium">Strong</span>
                    </div>
                  </div>

                  {/* Quick Actions */}
                  <div className="mt-4 pt-3 border-t border-white/10">
                    <button 
                      onClick={regenerateAIAnalysis}
                      disabled={isRegeneratingAnalysis}
                      className="w-full text-xs bg-blue-500/20 text-blue-400 px-3 py-2 rounded-lg hover:bg-blue-500/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      <RefreshCw size={12} className={isRegeneratingAnalysis ? 'animate-spin' : ''} />
                      {isRegeneratingAnalysis ? 'Regenerating...' : 'Regenerate Analysis'}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Campaign Validation Status */}
            <div className="bg-green-500/10 border border-green-400/20 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-sm font-medium text-green-400">Campaign Ready for Content Generation</span>
              </div>
              <p className="text-xs vvl-text-secondary mt-1 ml-5">
                All required information has been provided. AI is ready to generate targeted social media content.
              </p>
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

          {/* Suggested Marketing Post Ideas - Main Section */}
          <div className="mb-12">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold vvl-text-primary mb-4 flex items-center justify-center gap-3">
                <Sparkles className="text-blue-400" size={32} />
                Suggested Marketing Post Ideas
              </h2>
              <p className="text-lg vvl-text-secondary">
                AI-generated social media content tailored to your campaign objectives
              </p>
            </div>

            <div className="grid lg:grid-cols-3 gap-8">
              {socialMediaColumns.map(column => {
                const isBasic = column.id === 'text-only';
                const isEnhanced = column.id === 'text-image';
                const isPremium = column.id === 'text-video';
                
                return (
                  <div 
                    key={column.id} 
                    className={`vvl-card relative overflow-hidden ${
                      isBasic ? 'ring-2 ring-blue-400/30 shadow-lg shadow-blue-400/20' :
                      isEnhanced ? 'ring-2 ring-green-400/30 shadow-lg shadow-green-400/20' :
                      'ring-2 ring-purple-400/30 shadow-lg shadow-purple-400/20'
                    }`}
                  >
                    {/* Glow Effect */}
                    <div className={`absolute inset-0 opacity-20 ${
                      isBasic ? 'bg-gradient-to-br from-blue-400/20 to-cyan-400/20' :
                      isEnhanced ? 'bg-gradient-to-br from-green-400/20 to-emerald-400/20' :
                      'bg-gradient-to-br from-purple-400/20 to-orange-400/20'
                    }`}></div>
                    
                    {/* Tier Badge */}
                    <div className={`absolute top-4 right-4 px-3 py-1 rounded-full text-xs font-bold ${
                      isBasic ? 'bg-blue-500/30 text-blue-300 border border-blue-400/50' :
                      isEnhanced ? 'bg-green-500/30 text-green-300 border border-green-400/50' :
                      'bg-gradient-to-r from-purple-500/30 to-orange-500/30 text-orange-300 border border-purple-400/50'
                    }`}>
                      {isBasic ? 'BASIC' : isEnhanced ? 'ENHANCED' : 'PREMIUM'}
                    </div>

                    <div className="relative z-10 p-6 border-b border-white/20">
                      <div className="flex items-center gap-3 mb-2">
                        {column.id === 'text-only' && <Hash className="text-blue-400" size={24} />}
                        {column.id === 'text-image' && <Image className="text-green-400" size={24} />}
                        {column.id === 'text-video' && <Video className="text-purple-400" size={24} />}
                        <h3 className="text-lg font-bold vvl-text-primary">{column.title}</h3>
                      </div>
                      <p className="text-sm vvl-text-secondary mb-4">{column.description}</p>
                      
                      {/* Generate Button */}
                      {isBasic ? (
                        <button
                          onClick={() => generateColumnPosts(column.id)}
                          disabled={column.isGenerating}
                          className="w-full vvl-button-secondary text-sm flex items-center gap-2 justify-center disabled:opacity-50"
                        >
                          <RefreshCw size={14} className={column.isGenerating ? 'animate-spin' : ''} />
                          {column.isGenerating ? 'Generating...' : 'Regenerate'}
                        </button>
                      ) : (
                        <button
                          onClick={() => generateColumnPosts(column.id)}
                          disabled={column.isGenerating}
                          className={`w-full text-sm flex items-center gap-2 justify-center disabled:opacity-50 transition-all duration-300 ${
                            column.posts.length === 0 && !column.isGenerating
                              ? `animate-pulse ${
                                  isEnhanced 
                                    ? 'bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-400 hover:to-emerald-400 text-white font-bold py-3 px-6 rounded-lg shadow-lg shadow-green-500/30' 
                                    : 'bg-gradient-to-r from-purple-500 to-orange-500 hover:from-purple-400 hover:to-orange-400 text-white font-bold py-3 px-6 rounded-lg shadow-lg shadow-purple-500/30'
                                }`
                              : 'vvl-button-secondary'
                          }`}
                        >
                          {column.isGenerating ? (
                            <>
                              <RefreshCw size={14} className="animate-spin" />
                              Generating...
                            </>
                          ) : column.posts.length === 0 ? (
                            <>
                              <Wand2 size={16} />
                              Generate {isEnhanced ? 'Enhanced' : 'Premium'} Content
                            </>
                          ) : (
                            <>
                              <RefreshCw size={14} />
                              Regenerate
                            </>
                          )}
                        </button>
                      )}
                    </div>
                    
                    <div className="relative z-10 p-4 space-y-4 min-h-[600px] overflow-y-auto">
                  {column.posts.map((post: any) => (
                    <div key={post.id} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-grow">
                          <p className="text-sm vvl-text-secondary mb-3 leading-relaxed">{post.content.text}</p>
                          
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
                );
              })}
            </div>
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
                  onClick={async () => {
                    setIsLoading(true);
                    try {
                      await Promise.all([
                        generateColumnPosts('text-only'),
                        generateColumnPosts('text-image'),
                        generateColumnPosts('text-video')
                      ]);
                      toast.success('All posts regenerated successfully!');
                    } catch (error) {
                      toast.error('Failed to regenerate posts');
                    } finally {
                      setIsLoading(false);
                    }
                  }}
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
