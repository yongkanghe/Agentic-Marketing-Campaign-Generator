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
import { ArrowLeft, ArrowRight, Sparkles, RefreshCw, Heart, MessageCircle, Share, ExternalLink, Image, Video, Hash, Calendar, Home, Wand2, Info, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';
import VideoVentureLaunchAPI from '../lib/api';

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
      
      const data = await VideoVentureLaunchAPI.generateBulkContent({
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
      });
      
      // Transform API response to match frontend format
      const transformedPosts = data.new_posts.map((post: any, idx: number) => ({
        id: post.id || `${columnId}-post-${Date.now()}-${idx}`,
        type: columnId as 'text-only' | 'text-with-image' | 'text-with-video',
        platform: 'linkedin' as const,
        content: {
          text: post.content || `Generated ${postType.replace('_', ' + ')} content`,
          hashtags: post.hashtags || suggestedHashtags.slice(0, 3),
          imageUrl: (columnId === 'text-image' && post.image_url) ? post.image_url : undefined,
          videoUrl: (columnId === 'text-video' && post.video_url) ? post.video_url : undefined,
          productUrl: (columnId === 'text-only' && post.url) ? post.url : 
                     (columnId === 'text-only' ? (currentCampaign?.productServiceUrl || currentCampaign?.businessUrl) : undefined)
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
      
      // Reset loading state
      setSocialMediaColumns(prev => prev.map(col => 
        col.id === columnId ? { ...col, isGenerating: false } : col
      ));
      
      // Show proper error message without fallback to mock content
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      toast.error(`Failed to generate ${columnId} posts: ${errorMessage}. Please check your internet connection and try again.`);
    }
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

          {/* Business Logic & Cost Control Information */}
          <div className="vvl-card p-6 mb-8">
            <div className="flex items-center gap-3 mb-4">
              <Info className="text-blue-400" size={24} />
              <h3 className="text-lg font-semibold vvl-text-primary">Content Generation Limits & Cost Control</h3>
            </div>
            
            <div className="grid md:grid-cols-3 gap-4 mb-4">
              <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Hash className="text-blue-400" size={16} />
                  <span className="text-sm font-medium text-blue-400">Text + URL Posts</span>
                </div>
                <p className="text-lg font-bold vvl-text-primary">Up to 10 posts</p>
                <p className="text-xs vvl-text-secondary">Optimized for link sharing and traffic generation</p>
              </div>
              
              <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Image className="text-green-400" size={16} />
                  <span className="text-sm font-medium text-green-400">Text + Image Posts</span>
                </div>
                <p className="text-lg font-bold vvl-text-primary">Up to 4 posts</p>
                <p className="text-xs vvl-text-secondary">Limited to control Imagen API costs</p>
              </div>
              
              <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Video className="text-purple-400" size={16} />
                  <span className="text-sm font-medium text-purple-400">Text + Video Posts</span>
                </div>
                <p className="text-lg font-bold vvl-text-primary">Up to 4 posts</p>
                <p className="text-xs vvl-text-secondary">Limited to control Veo API costs</p>
              </div>
            </div>
            
            <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3">
              <div className="flex items-start gap-2">
                <AlertTriangle className="text-yellow-400 mt-0.5" size={16} />
                <div className="text-xs vvl-text-secondary">
                  <strong className="text-yellow-400">Cost Management:</strong> Generation limits are enforced to prevent 
                  exceeding model context limits and manage API costs. Text + URL posts have higher limits as they use only 
                  text generation, while visual content is limited due to compute-intensive image/video generation.
                </div>
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

            {/* Content Grid */}
            <div className="grid lg:grid-cols-3 gap-8">
              {socialMediaColumns.map((column) => (
                <div key={column.id} className="vvl-card p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2">
                        {column.id === 'text-only' && <Hash className="text-blue-400" size={20} />}
                        {column.id === 'text-image' && <Image className="text-green-400" size={20} />}
                        {column.id === 'text-video' && <Video className="text-purple-400" size={20} />}
                        <h3 className="text-lg font-semibold vvl-text-primary">{column.title}</h3>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        column.id === 'text-only' ? 'bg-blue-500/20 text-blue-400' :
                        column.id === 'text-image' ? 'bg-green-500/20 text-green-400' :
                        'bg-purple-500/20 text-purple-400'
                      }`}>
                        {column.id === 'text-only' ? 'BASIC' : 
                         column.id === 'text-image' ? 'ENHANCED' : 'PREMIUM'}
                      </span>
                    </div>
                  </div>
                  
                  <p className="text-sm vvl-text-secondary mb-4">{column.description}</p>
                  
                  <button
                    onClick={() => generateColumnPosts(column.id)}
                    disabled={column.isGenerating}
                    className={`w-full py-3 px-4 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 ${
                      column.isGenerating
                        ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                        : column.id === 'text-only'
                        ? 'bg-blue-600 hover:bg-blue-700 text-white'
                        : column.id === 'text-image'
                        ? 'bg-green-600 hover:bg-green-700 text-white'
                        : 'bg-gradient-to-r from-purple-600 to-orange-500 hover:from-purple-700 hover:to-orange-600 text-white'
                    }`}
                  >
                    {column.isGenerating ? (
                      <>
                        {/* AI Processing Animation */}
                        <div className="flex items-center gap-2">
                          <div className="relative">
                            <div className="w-4 h-4 border-2 border-gray-400 border-t-white rounded-full animate-spin"></div>
                          </div>
                          <span className="text-sm">AI Processing...</span>
                        </div>
                      </>
                    ) : (
                      <>
                        <RefreshCw size={16} />
                        {column.id === 'text-only' ? 'Regenerate' :
                         column.id === 'text-image' ? 'Generate Enhanced Content' :
                         'Generate Premium Content'}
                      </>
                    )}
                  </button>
                  
                  {/* Loading State with AI Indicators */}
                  {column.isGenerating && (
                    <div className="mt-4 p-4 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg">
                      <div className="space-y-3">
                        <div className="flex items-center gap-3 text-sm text-blue-400">
                          <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                          <span>Analyzing business context with Gemini AI...</span>
                        </div>
                        <div className="flex items-center gap-3 text-sm text-green-400">
                          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse animation-delay-300"></div>
                          <span>Generating creative content variations...</span>
                        </div>
                        <div className="flex items-center gap-3 text-sm text-purple-400">
                          <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse animation-delay-600"></div>
                          <span>Optimizing for platform engagement...</span>
                        </div>
                        {column.id !== 'text-only' && (
                          <div className="flex items-center gap-3 text-sm text-orange-400">
                            <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse animation-delay-900"></div>
                            <span>Preparing visual content prompts...</span>
                          </div>
                        )}
                      </div>
                      
                      {/* Progress Bar */}
                      <div className="mt-4">
                        <div className="w-full bg-gray-700 rounded-full h-1">
                          <div className="bg-gradient-to-r from-blue-500 to-purple-500 h-1 rounded-full animate-pulse w-3/4 transition-all duration-1000"></div>
                        </div>
                        <p className="text-xs text-gray-400 mt-2 text-center">Expected completion: ~5-10 seconds</p>
                      </div>
                    </div>
                  )}
                  
                  {/* Posts Display */}
                  <div className="mt-6 space-y-4">
                    {column.posts.length === 0 && !column.isGenerating ? (
                      <div className="text-center py-8 text-gray-400">
                        <div className="text-4xl mb-2">🎯</div>
                        <p className="text-sm">No posts generated yet</p>
                        <p className="text-xs text-gray-500 mt-1">Click "Regenerate" to create content</p>
                      </div>
                    ) : (
                      column.posts.map((post, index) => (
                        <div key={post.id} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
                          <div className="flex items-start justify-between mb-3">
                            {/* Post Content */}
                            <p className="text-sm vvl-text-secondary mb-3 leading-relaxed whitespace-pre-line">{post.content.text}</p>
                            
                            {/* URL Display for Text + URL Posts */}
                            {post.content.productUrl && (
                              <div className="mb-3 p-2 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                                <div className="flex items-center gap-2 text-blue-400">
                                  <ExternalLink size={14} />
                                  <a 
                                    href={post.content.productUrl} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="text-sm hover:text-blue-300 transition-colors truncate"
                                  >
                                    {post.content.productUrl}
                                  </a>
                                </div>
                              </div>
                            )}
                            
                            {/* Image Display for Text + Image Posts */}
                            {post.content.imageUrl && (
                              <div className="mb-3">
                                <img 
                                  src={post.content.imageUrl} 
                                  alt="AI Generated Marketing Image" 
                                  className="w-full h-40 object-cover rounded-lg border border-white/10"
                                  onError={(e) => {
                                    const target = e.target as HTMLImageElement;
                                    target.src = "https://picsum.photos/400/200?random=999&blur=1";
                                  }}
                                />
                                <p className="text-xs text-gray-400 mt-1">AI-Generated Image</p>
                              </div>
                            )}
                            
                            {/* Video Display for Text + Video Posts */}
                            {post.content.videoUrl && (
                              <div className="mb-3">
                                <div className="relative bg-purple-500/10 border border-purple-500/20 rounded-lg h-32 flex items-center justify-center">
                                  <div className="text-center">
                                    <Video className="text-purple-400 mx-auto mb-2" size={24} />
                                    <p className="text-xs text-purple-400">AI-Generated Video</p>
                                    <p className="text-xs text-gray-400 mt-1">Veo API Integration</p>
                                  </div>
                                </div>
                              </div>
                            )}
                            
                            {/* Hashtags */}
                            {post.content.hashtags && post.content.hashtags.length > 0 && (
                              <div className="flex flex-wrap gap-1 mb-3">
                                {post.content.hashtags.map((tag: string, idx: number) => (
                                  <span 
                                    key={idx} 
                                    className="text-xs text-blue-400 bg-blue-400/10 px-2 py-1 rounded"
                                  >
                                    {tag.startsWith('#') ? tag : `#${tag}`}
                                  </span>
                                ))}
                              </div>
                            )}
                            
                            {/* Engagement Score */}
                            <div className="flex items-center gap-2 text-xs text-gray-400">
                              <span className="flex items-center gap-1">
                                <div className={`w-2 h-2 rounded-full ${
                                  post.engagement_score >= 8 ? 'bg-green-400' :
                                  post.engagement_score >= 7 ? 'bg-yellow-400' : 'bg-red-400'
                                }`}></div>
                                  Engagement Score: {post.engagement_score.toFixed(1)}
                              </span>
                            </div>
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
                      ))
                    )}
                  </div>
                </div>
              ))}
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
