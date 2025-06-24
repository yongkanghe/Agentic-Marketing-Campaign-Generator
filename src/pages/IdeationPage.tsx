/**
 * FILENAME: IdeationPage.tsx
 * DESCRIPTION/PURPOSE: Simplified marketing post generation page
 * Author: JP + 2025-06-25
 * 
 * ADR COMPLIANCE:
 * - ADR-018: camelCase API calls only
 * - ADR-016: Per-post error handling
 * - Functional over complex styling
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMarketingContext } from '@/contexts/MarketingContext';
import { ArrowLeft, RefreshCw, Sparkles, AlertTriangle, Image, Video, Hash } from 'lucide-react';
import { toast } from 'sonner';
import VideoVentureLaunchAPI, { SocialMediaPost } from '../lib/api';
import { useAbortableApi } from '@/hooks/useAbortableApi';

interface PostColumn {
  id: string;
  title: string;
  type: 'text_url' | 'text_image' | 'text_video';
  posts: SocialMediaPost[];
  isGenerating: boolean;
  error: string | null;
}

const IdeationPage: React.FC = () => {
  const navigate = useNavigate();
  const { currentCampaign, aiSummary } = useMarketingContext();
  const { executeAbortableCall, hasActiveRequest } = useAbortableApi();
  
  const [mediaPrefs, setMediaPrefs] = useState('');
  const [selectedPosts, setSelectedPosts] = useState<string[]>([]);
  const [columns, setColumns] = useState<PostColumn[]>([
    { id: 'url', title: 'Text + URL', type: 'text_url', posts: [], isGenerating: false, error: null },
    { id: 'image', title: 'Text + Image', type: 'text_image', posts: [], isGenerating: false, error: null },
    { id: 'video', title: 'Text + Video', type: 'text_video', posts: [], isGenerating: false, error: null }
  ]);

  const generatePosts = useCallback(async (columnId: string) => {
    if (!currentCampaign) return;
    
    const column = columns.find(c => c.id === columnId);
    if (!column) return;

    // Set generating state
    setColumns(prev => prev.map(col => 
      col.id === columnId ? { ...col, isGenerating: true, posts: [], error: null } : col
    ));

    try {
      console.log(`🚀 Generating ${column.type} posts...`);
      
      // STEP 1: Generate text content (ADR-018: camelCase)
      const textResponse = await executeAbortableCall(async () => {
        return VideoVentureLaunchAPI.generateBulkContent({
          postType: column.type,
          regenerateCount: 3,
          businessContext: {
            companyName: currentCampaign.name,
            objective: currentCampaign.objective,
            campaignType: currentCampaign.campaignType,
            targetAudience: (aiSummary as any)?.businessAnalysis?.targetAudience || 'professionals',
            businessDescription: currentCampaign.businessDescription,
            businessWebsite: currentCampaign.businessUrl,
            productServiceUrl: currentCampaign.productServiceUrl,
            campaignMediaTuning: mediaPrefs
          },
          creativityLevel: currentCampaign.creativityLevel || 7
        });
      });

      if (!textResponse?.newPosts?.length) {
        throw new Error('No posts generated');
      }

      let posts = textResponse.newPosts.map((post: any) => ({
        ...post,
        id: post.id || `${columnId}-${Date.now()}`,
        type: column.type,
        selected: false,
        error: post.error || null // ADR-016: per-post errors
      }));

      // STEP 2: Generate visuals if needed (ADR-018: camelCase)
      if ((column.type === 'text_image' || column.type === 'text_video') && posts.length > 0) {
        console.log(`🎨 Generating visuals for ${column.type}...`);
        
        const visualResponse = await executeAbortableCall(async () => {
          return VideoVentureLaunchAPI.generateVisualContent({
            socialPosts: posts.map(post => ({
              id: post.id,
              content: post.content,
              type: column.type,
              platform: 'linkedin',
              hashtags: post.hashtags || []
            })),
            businessContext: {
              businessName: currentCampaign.name,
              industry: (aiSummary as any)?.businessAnalysis?.industry || 'business',
              objective: currentCampaign.objective,
              targetAudience: (aiSummary as any)?.businessAnalysis?.targetAudience || 'professionals'
            },
            campaignObjective: currentCampaign.objective,
            campaignId: currentCampaign.id
          });
        });

        // Map visual content with error handling (ADR-016)
        if (visualResponse?.postsWithVisuals) {
          posts = posts.map(post => {
            const visualPost = visualResponse.postsWithVisuals.find((vp: any) => vp.id === post.id);
            if (visualPost) {
              if ((visualPost as any).error) {
                return { ...post, error: (visualPost as any).error };
              }
              return {
                ...post,
                imageUrl: (visualPost as any).imageUrl,
                videoUrl: (visualPost as any).videoUrl
              };
            }
            return post;
          });
        }
      }

      // Update final state
      setColumns(prev => prev.map(col => 
        col.id === columnId ? { ...col, posts, isGenerating: false, error: null } : col
      ));

      const successCount = posts.filter(p => !p.error).length;
      toast.success(`Generated ${successCount} ${column.title} posts!`);

    } catch (error: any) {
      console.error(`❌ Generation failed for ${columnId}:`, error);
      const errorMsg = error.response?.data?.detail || error.message || 'Generation failed';
      
      setColumns(prev => prev.map(col =>
        col.id === columnId ? { ...col, isGenerating: false, error: errorMsg } : col
      ));
      
      toast.error(`Failed to generate ${column.title}: ${errorMsg}`);
    }
  }, [currentCampaign, aiSummary, mediaPrefs, executeAbortableCall, columns]);

  // Navigation guard
  useEffect(() => {
    if (!currentCampaign) {
      navigate('/dashboard');
    }
  }, [currentCampaign, navigate]);

  if (!currentCampaign) {
    return <div className="p-8 text-white">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* Header */}
      <div className="mb-8">
        <button 
          onClick={() => navigate('/dashboard')} 
          className="flex items-center text-blue-400 hover:text-blue-300 mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </button>
        <h1 className="text-3xl font-bold">Marketing Post Generation</h1>
        <p className="text-gray-400 mt-2">Campaign: {currentCampaign.name}</p>
      </div>

      {/* Media Preferences */}
      <div className="mb-8 bg-gray-800 p-4 rounded-lg">
        <label className="block text-sm font-medium mb-2">
          Visual Style Preferences (Optional)
        </label>
        <textarea
          value={mediaPrefs}
          onChange={(e) => setMediaPrefs(e.target.value)}
          placeholder="e.g., bright colors, modern design, outdoor setting..."
          className="w-full p-3 bg-gray-700 border border-gray-600 rounded text-white resize-none"
          rows={2}
        />
      </div>

      {/* Generation Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {columns.map((column) => (
          <div key={column.id} className="bg-gray-800 rounded-lg p-6">
            {/* Column Header */}
            <div className="flex items-center mb-4">
              {column.type === 'text_url' && <Hash className="w-6 h-6 text-blue-400 mr-3" />}
              {column.type === 'text_image' && <Image className="w-6 h-6 text-green-400 mr-3" />}
              {column.type === 'text_video' && <Video className="w-6 h-6 text-purple-400 mr-3" />}
              <h3 className="text-xl font-bold">{column.title}</h3>
            </div>

            {/* Generate Button */}
            <button 
              onClick={() => generatePosts(column.id)}
              disabled={column.isGenerating || hasActiveRequest}
              className={`w-full py-3 px-4 rounded-lg font-medium mb-4 transition-colors ${
                column.isGenerating || hasActiveRequest
                  ? 'bg-gray-600 cursor-not-allowed'
                  : column.type === 'text_image'
                  ? 'bg-green-600 hover:bg-green-700'
                  : column.type === 'text_video'
                  ? 'bg-purple-600 hover:bg-purple-700'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {column.isGenerating ? (
                <>
                  <RefreshCw className="animate-spin w-4 h-4 inline mr-2" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 inline mr-2" />
                  Generate Posts
                </>
              )}
            </button>

            {/* Column Error (ADR-016) */}
            {column.error && (
              <div className="mb-4 p-3 bg-red-900 border border-red-700 rounded-lg">
                <div className="flex items-start">
                  <AlertTriangle className="h-4 w-4 mr-2 text-red-400 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-red-200">{column.error}</span>
                </div>
              </div>
            )}

            {/* Posts Display */}
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {column.posts.length === 0 && !column.isGenerating ? (
                <div className="text-center py-8 text-gray-500">
                  <div className="text-3xl mb-2">📝</div>
                  <p className="text-sm">No posts generated yet</p>
                </div>
              ) : (
                column.posts.map((post) => (
                  <div key={post.id} className="border border-gray-700 rounded-lg p-4 bg-gray-750">
                    {/* Per-Post Error (ADR-016) */}
                    {post.error ? (
                      <div className="p-3 bg-red-900 border border-red-700 rounded-lg">
                        <div className="flex items-start">
                          <AlertTriangle className="h-4 w-4 mr-2 text-red-400 mt-0.5" />
                          <span className="text-sm text-red-200">
                            Generation failed: {post.error}
                          </span>
                        </div>
                      </div>
                    ) : (
                      <>
                        {/* Visual Content */}
                        {post.imageUrl && (
                          <img 
                            src={post.imageUrl} 
                            alt="Generated" 
                            className="w-full h-32 object-cover rounded mb-3"
                            onError={(e) => e.currentTarget.style.display = 'none'}
                          />
                        )}
                        
                        {post.videoUrl && (
                          <video 
                            src={post.videoUrl}
                            className="w-full h-32 object-cover rounded mb-3"
                            controls
                            muted
                            onError={(e) => e.currentTarget.style.display = 'none'}
                          />
                        )}

                        {/* Text Content */}
                        <p className="text-gray-300 text-sm mb-3 leading-relaxed">
                          {post.content}
                        </p>
                        
                        {/* Hashtags */}
                        {post.hashtags && post.hashtags.length > 0 && (
                          <div className="flex flex-wrap gap-1 mb-3">
                            {post.hashtags.slice(0, 3).map((tag, idx) => (
                              <span key={idx} className="text-xs bg-gray-700 px-2 py-1 rounded">
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}

                        {/* Select Button */}
                        <button
                          onClick={() => {
                            setSelectedPosts(prev => 
                              prev.includes(post.id) 
                                ? prev.filter(id => id !== post.id)
                                : [...prev, post.id]
                            );
                          }}
                          className={`w-full py-2 px-3 rounded text-sm font-medium transition-colors ${
                            selectedPosts.includes(post.id)
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                          }`}
                        >
                          {selectedPosts.includes(post.id) ? '✓ Selected' : 'Select for Campaign'}
                        </button>
                      </>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Selected Posts Summary */}
      {selectedPosts.length > 0 && (
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-lg font-bold mb-2">{selectedPosts.length} Posts Selected</h3>
          <button
            onClick={() => {
              toast.success(`${selectedPosts.length} posts ready for scheduling!`);
              navigate('/scheduling');
            }}
            className="bg-green-600 hover:bg-green-700 px-6 py-3 rounded-lg font-medium"
          >
            Proceed to Scheduling →
          </button>
        </div>
      )}
    </div>
  );
};

export default IdeationPage; 