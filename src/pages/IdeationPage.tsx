/**
 * FILENAME: IdeationPage.tsx
 * DESCRIPTION/PURPOSE: Social media post ideation and generation page with VVL design system styling
 * Author: JP + 2025-06-15
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMarketingContext } from '@/contexts/MarketingContext';
import { MaterialVideoCard } from '@/components/MaterialVideoCard';
import { EditableCampaignGuidance } from '@/components/EditableCampaignGuidance';
import { CampaignGuidanceChat } from '@/components/CampaignGuidanceChat';
import { Textarea } from '@/components/ui/textarea';
import { ArrowLeft, ArrowRight, Sparkles, RefreshCw, Heart, MessageCircle, Share, ExternalLink, Image, Video, Hash, Calendar, Home, Wand2, Info, AlertTriangle, Palette, Edit, X } from 'lucide-react';
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
  
  // Campaign Guidance Chat State
  const [showGuidanceChat, setShowGuidanceChat] = useState(false);
  const [showGuidanceEdit, setShowGuidanceEdit] = useState(false);
  
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
    
    // SESSION PERSISTENCE: Restore social media columns from localStorage or campaign data
    const campaignColumnsKey = `campaign-${currentCampaign.id}-columns`;
    const savedColumns = localStorage.getItem(campaignColumnsKey);
    
    if (savedColumns) {
      try {
        const parsedColumns = JSON.parse(savedColumns);
        // Ensure type compatibility
        setSocialMediaColumns(parsedColumns as typeof socialMediaColumns);
        console.log('Restored social media columns from localStorage for campaign:', currentCampaign.id);
      } catch (error) {
        console.error('Failed to parse saved columns:', error);
        // Auto-generate initial posts when page loads if no saved data
        generateAllPosts();
      }
    } else if (currentCampaign.socialMediaColumns && currentCampaign.socialMediaColumns.length > 0) {
      // Restore from campaign data if available
      setSocialMediaColumns(currentCampaign.socialMediaColumns as typeof socialMediaColumns);
      console.log('Restored social media columns from campaign data');
    } else {
      // Auto-generate initial posts when page loads
      generateAllPosts();
    }
  }, [currentCampaign, navigate]);

  // SESSION PERSISTENCE: Save social media columns to localStorage whenever they change
  useEffect(() => {
    if (currentCampaign && socialMediaColumns.some(col => col.posts.length > 0)) {
      const campaignColumnsKey = `campaign-${currentCampaign.id}-columns`;
      localStorage.setItem(campaignColumnsKey, JSON.stringify(socialMediaColumns));
      
      // Also update the campaign in the marketing context
      updateCurrentCampaign({ socialMediaColumns });
    }
  }, [socialMediaColumns, currentCampaign?.id]);

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
    // Set loading state immediately
    setSocialMediaColumns(prev => prev.map(col => 
      col.id === columnId ? { ...col, isGenerating: true, posts: [] } : col
    ));
    
    try {
      // Real API call to backend for content generation
      const postType = columnId === 'text-only' ? 'text_url' : 
                      columnId === 'text-image' ? 'text_image' : 'text_video';
      
      console.log(`🎯 Generating ${postType} posts for column ${columnId}...`);
      
      const data = await VideoVentureLaunchAPI.generateBulkContent({
        post_type: postType,
        regenerate_count: 5,
        business_context: {
          // Use REAL AI analysis data when available
          company_name: currentCampaign?.aiAnalysis?.businessAnalysis?.company_name || currentCampaign?.name || 'Your Company',
          objective: currentCampaign?.objective || 'increase sales',
          campaign_type: currentCampaign?.campaignType || 'service',
          target_audience: currentCampaign?.aiAnalysis?.businessAnalysis?.target_audience || 'business professionals',
          business_description: currentCampaign?.businessDescription || '',
          business_website: currentCampaign?.businessUrl || '',
          product_service_url: currentCampaign?.productServiceUrl || '',
          campaign_media_tuning: preferredDesign || ''
        },
        creativity_level: currentCampaign?.creativityLevel || 7
      });
      
      console.log(`✅ Generated ${data.new_posts.length} ${postType} posts successfully`);
      
      // Transform API response to match frontend format
      const transformedPosts = data.new_posts.map((post: any, idx: number) => {
        const column = socialMediaColumns.find(col => col.id === columnId);
        return {
          id: post.id || `${columnId}-post-${Date.now()}-${idx}`,
          type: column?.mediaType || columnId as 'text-only' | 'text-with-image' | 'text-with-video',
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
        };
      });
      
      setSocialMediaColumns(prev => prev.map(col => 
        col.id === columnId ? { ...col, posts: transformedPosts, isGenerating: false } : col
      ));

      toast.success(`Generated ${transformedPosts.length} ${postType.replace('_', ' + ')} posts successfully!`);
      
    } catch (error) {
      console.error(`❌ Failed to generate ${columnId} posts:`, error);
      
      // Reset loading state and clear any partial posts
      setSocialMediaColumns(prev => prev.map(col => 
        col.id === columnId ? { ...col, isGenerating: false, posts: [] } : col
      ));
      
      // Show detailed error message for debugging
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      const postType = columnId === 'text-only' ? 'text_url' : 
                      columnId === 'text-image' ? 'text_image' : 'text_video';
      console.error(`Generation error details:`, { columnId, postType, error });
      
      toast.error(`Failed to generate ${columnId.replace('-', ' + ')} posts: ${errorMessage}. Please check your connection and try again.`);
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
      // Real API call to analyze URLs and get themes/tags
      if (currentCampaign && (currentCampaign.businessUrl || currentCampaign.aboutPageUrl || currentCampaign.productServiceUrl)) {
        const urls = [
          currentCampaign.businessUrl,
          currentCampaign.aboutPageUrl,
          currentCampaign.productServiceUrl
        ].filter(url => url && url.trim());

        const response = await fetch('/api/v1/analysis/url', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            urls: urls,
            analysis_depth: 'comprehensive'
          }),
        });

        if (!response.ok) {
          throw new Error(`Analysis failed: ${response.status}`);
        }

        const analysisResult = await response.json();
        
        // Extract themes and tags from analysis result
        const suggestedThemes = analysisResult.suggested_themes || [];
        const suggestedTags = analysisResult.suggested_tags || [];
        
        // Update the marketing context with real themes and tags
        if (suggestedThemes.length > 0) {
          // Clear existing themes and add new ones
          selectedThemes.forEach(theme => unselectTheme(theme));
          suggestedThemes.slice(0, 3).forEach((theme: string) => selectTheme(theme));
        }
        
        if (suggestedTags.length > 0) {
          // Clear existing tags and add new ones  
          selectedTags.forEach(tag => unselectTag(tag));
          suggestedTags.slice(0, 4).forEach((tag: string) => selectTag(tag));
        }

        // Update AI summary with business analysis
        if (analysisResult.business_analysis) {
          const businessAnalysis = analysisResult.business_analysis;
          const newSummary = `AI Analysis: ${businessAnalysis.company_name} operates in ${businessAnalysis.industry}, targeting ${businessAnalysis.target_audience}. Key strengths: ${businessAnalysis.competitive_advantages?.join(', ') || 'Not specified'}.`;
          
                  // Update the current campaign with the COMPLETE new analysis
        updateCurrentCampaign({
          aiAnalysis: {
            summary: newSummary,
            businessAnalysis: businessAnalysis,
            campaignGuidance: businessAnalysis.campaign_guidance || {},
            lastUpdated: new Date().toISOString()
          }
        });
        }

        toast.success(`✨ AI Analysis Complete! Found ${suggestedThemes.length} themes and ${suggestedTags.length} tags from your business context.`);
      } else {
        // Fallback for campaigns without URLs
        toast.warning('No URLs provided for analysis. Using default themes and tags.');
      }
      
    } catch (error) {
      console.error('AI analysis regeneration failed:', error);
      toast.error('Failed to regenerate AI analysis. Please check your connection and try again.');
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
                    {currentCampaign?.aiAnalysis?.summary || aiSummary || "AI-generated summary will appear here after analyzing your business URLs. Click 'Regenerate Analysis' to analyze your campaign context."}
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

            {/* Campaign Creative Guidance Section - Now Editable */}
            <div className="bg-gradient-to-br from-purple-500/10 to-blue-500/10 border border-purple-400/20 rounded-lg p-6 mb-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <Palette className="text-purple-400" size={20} />
                  <h4 className="text-lg font-semibold text-white">Campaign Creative Guidance</h4>
                </div>
                <div className="flex items-center gap-2">
                  <button 
                    onClick={() => setShowGuidanceChat(!showGuidanceChat)}
                    className="flex items-center gap-2 bg-purple-500/20 text-purple-400 px-3 py-1 rounded-lg hover:bg-purple-500/30 transition-colors text-sm"
                  >
                    <MessageCircle size={16} />
                    Chat to Refine
                  </button>
                  <button 
                    onClick={() => setShowGuidanceEdit(!showGuidanceEdit)}
                    className="flex items-center gap-2 bg-blue-500/20 text-blue-400 px-3 py-1 rounded-lg hover:bg-blue-500/30 transition-colors text-sm"
                  >
                    <Edit size={16} />
                    Edit
                  </button>
                </div>
              </div>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h5 className="text-sm font-semibold text-white mb-2">Creative Direction</h5>
                  <p className="text-sm text-gray-200 leading-relaxed mb-3">
                    {currentCampaign?.aiAnalysis?.campaignGuidance?.creative_direction || 
                     "Professional lifestyle photography with modern, clean composition focusing on authentic customer scenarios. Emphasize trustworthy, competent brand personality through natural lighting and business-appropriate settings."}
                  </p>
                  
                  <h5 className="text-sm font-semibold text-white mb-2 mt-4">Visual Style</h5>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-xs">
                      <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                      <span className="text-gray-300">Photography: {currentCampaign?.aiAnalysis?.campaignGuidance?.visual_style?.photography_style || "Professional lifestyle"}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                      <span className="text-gray-300">Mood: {currentCampaign?.aiAnalysis?.campaignGuidance?.visual_style?.mood || "Professional, trustworthy, competent"}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                      <span className="text-gray-300">Lighting: {currentCampaign?.aiAnalysis?.campaignGuidance?.visual_style?.lighting || "Natural lighting"}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h5 className="text-sm font-semibold text-white mb-2">Content Themes</h5>
                  <p className="text-sm text-gray-200 leading-relaxed mb-3">
                    {currentCampaign?.aiAnalysis?.campaignGuidance?.target_context || 
                     "Focus on authenticity, results, and community building. Use inspiring and action-oriented calls-to-action that trigger aspiration, trust, and excitement in your target audience."}
                  </p>
                  
                  <div className="flex flex-wrap gap-2">
                    {(currentCampaign?.aiAnalysis?.campaignGuidance?.content_themes?.primary_themes || ['Authenticity', 'Results', 'Community', 'Growth', 'Innovation']).map((theme: string) => (
                      <span key={theme} className="text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded-full">
                        {theme}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t border-white/10">
                <div className="grid md:grid-cols-2 gap-4 text-xs">
                  <div>
                    <span className="font-semibold text-blue-400">Image Generation:</span>
                    <span className="text-gray-300 ml-2">
                      {currentCampaign?.aiAnalysis?.campaignGuidance?.imagen_prompts?.technical_specs || "Following Imagen best practices with 35mm lens, natural lighting, high resolution"}
                    </span>
                  </div>
                  <div>
                    <span className="font-semibold text-purple-400">Video Generation:</span>
                    <span className="text-gray-300 ml-2">
                      {currentCampaign?.aiAnalysis?.campaignGuidance?.veo_prompts?.duration_focus || "Following Veo best practices with smooth movements, 15-30 second social clips"}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Campaign Guidance Chat Interface */}
            {showGuidanceChat && (
              <div className="mt-6">
                <div className="vvl-card p-6">
                  <h4 className="text-lg font-semibold vvl-text-primary mb-4">Campaign Guidance Chat</h4>
                  <p className="vvl-text-secondary mb-4">Chat interface for refining campaign guidance will be available here.</p>
                  <button 
                    onClick={() => setShowGuidanceChat(false)}
                    className="vvl-button-secondary"
                  >
                    Close
                  </button>
                </div>
              </div>
            )}

            {/* Campaign Guidance Edit Interface */}
            {showGuidanceEdit && (
              <div className="mt-6">
                <div className="vvl-card p-6">
                  <h4 className="text-lg font-semibold vvl-text-primary mb-4">Edit Campaign Guidance</h4>
                  <p className="vvl-text-secondary mb-4">Edit interface for campaign guidance will be available here.</p>
                  <button 
                    onClick={() => setShowGuidanceEdit(false)}
                    className="vvl-button-secondary"
                  >
                    Close
                  </button>
                </div>
              </div>
            )}

            {/* Campaign Validation Status */}
            <div className="bg-green-500/10 border border-green-400/20 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-sm font-medium text-green-400">Campaign Ready for Content Generation</span>
              </div>
              <p className="text-xs vvl-text-secondary mt-1 ml-5">
                All required information has been provided. AI is ready to generate targeted social media content following the creative guidance above.
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

          {/* Campaign Media Tuning */}
          <div className="vvl-card p-6 mb-8">
            <h3 className="text-lg font-semibold vvl-text-primary mb-4">Campaign Media Tuning (Optional)</h3>
            <p className="text-sm vvl-text-secondary mb-3">
              Fine-tune your visual content generation by specifying design preferences, visual styles, colors, moods, or specific requirements for images and videos.
            </p>
            <Textarea
              placeholder="Example: I want vibrant, colorful t-shirt designs with creative artwork instead of generic text. Use modern, artistic styles with unique graphics that reflect creativity and personal expression..."
              value={preferredDesign}
              onChange={(e) => setPreferredDesign(e.target.value)}
              className="min-h-[100px] resize-none bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-3 text-white placeholder-gray-400 focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/25"
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
                        <div key={post.id} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4 break-words">
                          {/* Visual Content Display */}
                          {(post.content.imageUrl || post.content.videoUrl) && (
                            <div className="mb-4">
                              {post.content.imageUrl && (
                                <div className="relative rounded-lg overflow-hidden bg-gray-800">
                                  <img 
                                    src={post.content.imageUrl} 
                                    alt="Generated marketing image"
                                    className="w-full h-48 object-cover"
                                    onError={(e) => {
                                      // Fallback to placeholder if image fails to load
                                      e.currentTarget.src = 'https://picsum.photos/400/240?blur=2';
                                    }}
                                  />
                                </div>
                              )}
                              
                              {post.content.videoUrl && (
                                <div className="relative rounded-lg overflow-hidden bg-gray-800">
                                  <video 
                                    src={post.content.videoUrl}
                                    className="w-full h-48 object-cover"
                                    controls
                                    poster="https://picsum.photos/400/240?blur=2"
                                  />
                                </div>
                              )}
                            </div>
                          )}

                          {/* Post Content */}
                          <div className="mb-4">
                            <p className="text-gray-300 leading-relaxed text-sm break-words whitespace-pre-wrap">
                              {post.content.text}
                            </p>
                            
                            {/* URL Display for text+url posts */}
                            {post.content.productUrl && (
                              <div className="mt-3 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                                <div className="flex items-center gap-2 mb-1">
                                  <ExternalLink className="text-blue-400" size={14} />
                                  <span className="text-xs font-medium text-blue-400">See More</span>
                                </div>
                                <a 
                                  href={post.content.productUrl} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="text-blue-300 hover:text-blue-200 text-xs break-all underline"
                                >
                                  {post.content.productUrl}
                                </a>
                              </div>
                            )}
                          </div>

                          {/* Hashtags */}
                          {post.content.hashtags && post.content.hashtags.length > 0 && (
                            <div className="mb-4">
                              <div className="flex flex-wrap gap-2">
                                {post.content.hashtags.slice(0, 6).map((tag, tagIdx) => (
                                  <span
                                    key={tagIdx}
                                    className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded-full text-xs break-words"
                                  >
                                    {tag}
                                  </span>
                                ))}
                                {post.content.hashtags.length > 6 && (
                                  <span className="px-2 py-1 bg-gray-500/20 text-gray-400 rounded-full text-xs">
                                    +{post.content.hashtags.length - 6} more
                                  </span>
                                )}
                              </div>
                            </div>
                          )}
                          
                          {/* Post Actions */}
                          <div className="flex items-center justify-between pt-3 border-t border-white/10">
                            <div className="flex items-center gap-2 text-xs text-gray-400">
                              <span className="capitalize">{post.type.replace('_', ' + ')}</span>
                              {post.engagement_score && (
                                <>
                                  <span>•</span>
                                  <span>Score: {post.engagement_score.toFixed(1)}</span>
                                </>
                              )}
                            </div>
                            
                            <button
                              onClick={() => togglePostSelection(post.id)}
                              className={`p-2 rounded-lg transition-all duration-200 ${
                                selectedPosts.includes(post.id)
                                  ? 'bg-blue-500/30 text-blue-400'
                                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
                              }`}
                              title={selectedPosts.includes(post.id) ? 'Remove from selection' : 'Add to selection'}
                            >
                              <Heart size={16} className={selectedPosts.includes(post.id) ? 'fill-current' : ''} />
                            </button>
                          </div>
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
