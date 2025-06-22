/**
 * FILENAME: SchedulingPage.tsx
 * DESCRIPTION/PURPOSE: Social media scheduling page with VVL design system styling
 * Author: JP + 2025-06-15
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMarketingContext } from '@/contexts/MarketingContext';
import { Slider } from '@/components/ui/slider';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  ArrowLeft, 
  Calendar, 
  Clock, 
  Send, 
  Download, 
  Settings, 
  ChevronRight,
  ChevronLeft,
  Play,
  Pause,
  RotateCcw,
  CheckCircle,
  AlertCircle,
  ExternalLink,
  Home,
  Sparkles
} from 'lucide-react';
import { toast } from 'sonner';

// Social media platform icons (simplified)
const PlatformIcon = ({ platform }: { platform: string }) => {
  const icons = {
    linkedin: '💼',
    twitter: '🐦', 
    instagram: '📸',
    facebook: '👥',
    tiktok: '🎵'
  };
  return <span className="text-lg">{icons[platform as keyof typeof icons] || '📱'}</span>;
};

const SchedulingPage: React.FC = () => {
  const navigate = useNavigate();
  const { currentCampaign } = useMarketingContext();
  
  // Scheduling state
  const [schedulingInterval, setSchedulingInterval] = useState([4]); // hours
  const [startTime, setStartTime] = useState('09:00');
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['linkedin', 'twitter']);
  const [isSchedulingActive, setIsSchedulingActive] = useState(false);
  const [showScheduledPanel, setShowScheduledPanel] = useState(false);
  
  // Mock selected posts (would come from context)
  const [selectedPosts] = useState([
    {
      id: 'post-1',
      type: 'text-only' as const,
      platform: 'linkedin' as const,
      content: {
        text: '🚀 Exciting news! We\'re launching something amazing that will transform how you achieve your business goals.',
        hashtags: ['#marketing', '#business', '#growth'],
        productUrl: 'https://example.com/product'
      },
      generationPrompt: 'Generate text-only post for product campaign',
      selected: true
    },
    {
      id: 'post-2', 
      type: 'text-with-image' as const,
      platform: 'instagram' as const,
      content: {
        text: '🎨 Visual storytelling at its finest! See how we\'re revolutionizing marketing.',
        hashtags: ['#design', '#innovation', '#visual'],
        imageUrl: 'https://via.placeholder.com/400x300?text=Image+1'
      },
      generationPrompt: 'Generate image post for brand campaign',
      selected: true
    }
  ]);
  
  // Mock scheduled posts
  const [scheduledPosts, setScheduledPosts] = useState([
    {
      id: 'scheduled-1',
      post: selectedPosts[0],
      scheduledTime: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), // 2 hours from now
      platform: 'linkedin',
      status: 'pending' as const,
      campaignId: currentCampaign?.id || ''
    },
    {
      id: 'scheduled-2',
      post: selectedPosts[0],
      scheduledTime: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(), // 1 hour ago
      platform: 'twitter',
      status: 'posted' as const,
      campaignId: currentCampaign?.id || ''
    }
  ]);
  
  // Platform connection state
  const [platforms, setPlatforms] = useState([
    { id: 'linkedin', name: 'LinkedIn', connected: false, username: null },
    { id: 'twitter', name: 'Twitter/X', connected: false, username: null },
    { id: 'instagram', name: 'Instagram', connected: false, username: null },
    { id: 'facebook', name: 'Facebook', connected: false, username: null },
    { id: 'tiktok', name: 'TikTok', connected: false, username: null }
  ]);

  useEffect(() => {
    if (!currentCampaign) {
      navigate('/');
    } else {
      // Load platform connection status
      loadPlatformStatus();
    }
  }, [currentCampaign, navigate]);

  const loadPlatformStatus = async () => {
    try {
      const response = await fetch('/api/v1/auth/social/status');
      if (response.ok) {
        const data = await response.json();
        
        // Update platform connection status
        setPlatforms(prevPlatforms => 
          prevPlatforms.map(platform => ({
            ...platform,
            connected: data.platforms[platform.id]?.connected || false,
            username: data.platforms[platform.id]?.username || null
          }))
        );
      }
    } catch (error) {
      console.error('Failed to load platform status:', error);
    }
  };

  const togglePlatform = (platformId: string) => {
    setSelectedPlatforms(prev => 
      prev.includes(platformId)
        ? prev.filter(id => id !== platformId)
        : [...prev, platformId]
    );
  };

  const handleStartScheduling = () => {
    if (selectedPlatforms.length === 0) {
      toast.error('Please select at least one social media platform');
      return;
    }
    
    setIsSchedulingActive(true);
    toast.success(`Scheduling started! Posts will be published every ${schedulingInterval[0]} hours starting at ${startTime}`);
    
    // Mock scheduling logic
    const newScheduledPosts = selectedPosts.map((post, index) => ({
      id: `scheduled-${Date.now()}-${index}`,
      post,
      scheduledTime: new Date(Date.now() + (index + 1) * schedulingInterval[0] * 60 * 60 * 1000).toISOString(),
      platform: selectedPlatforms[index % selectedPlatforms.length],
      status: 'pending' as const,
      campaignId: currentCampaign?.id || ''
    }));
    
    setScheduledPosts(prev => [...prev, ...newScheduledPosts]);
  };

  const handleStopScheduling = () => {
    setIsSchedulingActive(false);
    toast.info('Scheduling paused. You can resume anytime.');
  };

  const handleConnectPlatform = async (platformId: string) => {
    try {
      // Initiate OAuth flow
      const response = await fetch('/api/v1/auth/social/initiate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          platform: platformId,
          callback_url: `${window.location.origin}/api/v1/auth/social/callback/${platformId}`
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Open OAuth popup
        const popup = window.open(
          data.oauth_url,
          'social_auth',
          'width=600,height=600,scrollbars=yes,resizable=yes'
        );

        // Listen for successful authentication
        const checkClosed = setInterval(() => {
          if (popup?.closed) {
            clearInterval(checkClosed);
            // Reload platform status after authentication
            setTimeout(() => {
              loadPlatformStatus();
              toast.success(`Successfully connected to ${platformId}!`);
            }, 1000);
          }
        }, 1000);

      } else {
        const errorData = await response.json();
        toast.error(`Failed to connect to ${platformId}: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('OAuth initiation error:', error);
      toast.error(`Failed to connect to ${platformId}. Please try again.`);
    }
  };

  const handleDisconnectPlatform = async (platformId: string) => {
    try {
      const response = await fetch(`/api/v1/auth/social/disconnect/${platformId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        loadPlatformStatus();
        toast.success(`Disconnected from ${platformId}`);
      } else {
        toast.error(`Failed to disconnect from ${platformId}`);
      }
    } catch (error) {
      console.error('Disconnect error:', error);
      toast.error(`Failed to disconnect from ${platformId}`);
    }
  };

  const exportCampaignTemplate = () => {
    const template = {
      name: currentCampaign?.name,
      objective: currentCampaign?.objective,
      businessDescription: currentCampaign?.businessDescription,
      campaignType: currentCampaign?.campaignType,
      creativityLevel: currentCampaign?.creativityLevel,
      selectedPosts: selectedPosts,
      prompts: selectedPosts.map(post => post.generationPrompt),
      createdAt: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(template, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentCampaign?.name || 'campaign'}-template.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast.success('Campaign template exported! You can upload this in future campaigns.');
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
                <Sparkles className="text-blue-400" size={24} />
                <h1 className="text-xl font-bold vvl-text-primary">Schedule & Publish</h1>
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
                onClick={() => navigate('/ideation')}
                className="vvl-button-secondary text-sm flex items-center gap-2"
              >
                <ArrowLeft size={16} />
                Back to Posts
              </button>
              
              <button
                onClick={() => setShowScheduledPanel(!showScheduledPanel)}
                className="vvl-button-secondary text-sm flex items-center gap-2"
              >
                <Calendar size={16} />
                Scheduled ({scheduledPosts.length})
                {showScheduledPanel ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
              </button>
            </div>
          </div>
        </div>
      </header>
      
      <div className="container mx-auto px-6 py-12 flex-grow">
        <div className="max-w-7xl mx-auto">
          {/* Page Header */}
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold vvl-text-primary mb-4">{currentCampaign.name}</h2>
            <p className="text-lg vvl-text-secondary">Schedule your AI-generated content across social media platforms</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Main Scheduling Panel */}
            <div className="lg:col-span-8">
              {/* Scheduling Controls */}
              <div className="vvl-card p-6 mb-8">
                <h3 className="text-xl font-semibold vvl-text-primary mb-6">Scheduling Settings</h3>
                
                {/* Platform Selection */}
                <div className="mb-6">
                  <Label className="text-sm font-medium vvl-text-primary mb-3 block">Select Platforms</Label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {platforms.map(platform => (
                      <div key={platform.id} className="relative">
                        <button
                          onClick={() => platform.connected ? togglePlatform(platform.id) : handleConnectPlatform(platform.id)}
                          disabled={!platform.connected && selectedPlatforms.includes(platform.id)}
                          className={`w-full p-3 rounded-lg border transition-all duration-200 flex items-center gap-3 ${
                            selectedPlatforms.includes(platform.id) && platform.connected
                              ? 'bg-blue-500/20 border-blue-400 text-blue-400'
                              : platform.connected
                              ? 'bg-white/5 border-white/20 vvl-text-secondary hover:bg-white/10'
                              : 'bg-white/5 border-white/10 vvl-text-secondary opacity-50 hover:opacity-75'
                          }`}
                        >
                          <PlatformIcon platform={platform.id} />
                          <div className="flex flex-col items-start flex-grow">
                            <span className="text-sm font-medium">{platform.name}</span>
                            {platform.connected && platform.username && (
                              <span className="text-xs vvl-text-secondary">@{platform.username}</span>
                            )}
                          </div>
                          {platform.connected ? (
                            <div className="flex items-center gap-2">
                              <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">
                                Connected
                              </span>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDisconnectPlatform(platform.id);
                                }}
                                className="text-xs bg-red-500/20 text-red-400 px-2 py-1 rounded hover:bg-red-500/30"
                              >
                                Disconnect
                              </button>
                            </div>
                          ) : (
                            <span className="text-xs bg-orange-500/20 text-orange-400 px-2 py-1 rounded">
                              Connect
                            </span>
                          )}
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Timing Controls */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div>
                    <Label className="text-sm font-medium vvl-text-primary mb-2 block">Posting Interval (hours)</Label>
                    <div className="space-y-2">
                      <Slider
                        value={schedulingInterval}
                        onValueChange={setSchedulingInterval}
                        max={24}
                        min={1}
                        step={1}
                        className="w-full"
                      />
                      <div className="text-sm vvl-text-secondary">
                        Post every {schedulingInterval[0]} hour{schedulingInterval[0] !== 1 ? 's' : ''}
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <Label className="text-sm font-medium vvl-text-primary mb-2 block">Start Time</Label>
                    <Input
                      type="time"
                      value={startTime}
                      onChange={(e) => setStartTime(e.target.value)}
                      className="vvl-input"
                    />
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-wrap gap-3">
                  {!isSchedulingActive ? (
                    <button
                      onClick={handleStartScheduling}
                      className="vvl-button-primary flex items-center gap-2"
                    >
                      <Play size={16} />
                      Start Scheduling
                    </button>
                  ) : (
                    <button
                      onClick={handleStopScheduling}
                      className="bg-orange-500 hover:bg-orange-600 text-white font-medium px-6 py-3 rounded-lg transition-all duration-200 flex items-center gap-2"
                    >
                      <Pause size={16} />
                      Pause Scheduling
                    </button>
                  )}
                  
                  <button
                    onClick={exportCampaignTemplate}
                    className="vvl-button-secondary flex items-center gap-2"
                  >
                    <Download size={16} />
                    Export Template
                  </button>
                </div>
              </div>

              {/* Selected Posts Preview */}
              <div className="vvl-card p-6">
                <h3 className="text-xl font-semibold vvl-text-primary mb-6">Posts to Schedule ({selectedPosts.length})</h3>
                <div className="space-y-4">
                  {selectedPosts.map((post, index) => (
                    <div key={post.id} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-4">
                      <div className="flex items-start gap-4">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold text-sm">
                          {index + 1}
                        </div>
                        <div className="flex-grow">
                          <div className="flex items-center gap-2 mb-2">
                            <PlatformIcon platform={post.platform} />
                            <span className="text-sm font-medium vvl-text-primary capitalize">{post.platform}</span>
                            <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">{post.type}</span>
                          </div>
                          <p className="vvl-text-secondary text-sm mb-2">{post.content.text}</p>
                          {post.content.hashtags && (
                            <div className="flex flex-wrap gap-1">
                              {post.content.hashtags.map((tag, idx) => (
                                <span key={idx} className="text-xs text-blue-400">#{tag.replace('#', '')}</span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Scheduled Posts Panel */}
            <div className={`lg:col-span-4 transition-all duration-300 ${showScheduledPanel ? 'block' : 'hidden lg:block'}`}>
              <div className="vvl-card sticky top-4">
                <div className="p-6 border-b border-white/20">
                  <h3 className="font-semibold vvl-text-primary flex items-center gap-2">
                    <Calendar size={20} />
                    Scheduled Posts
                  </h3>
                  <p className="text-sm vvl-text-secondary mt-1">{scheduledPosts.length} posts in queue</p>
                </div>
                <div className="p-6 max-h-96 overflow-y-auto">
                  <div className="space-y-4">
                    {scheduledPosts.map((scheduledPost) => (
                      <div key={scheduledPost.id} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-2">
                          <PlatformIcon platform={scheduledPost.platform} />
                          <span className="text-sm font-medium vvl-text-primary capitalize">{scheduledPost.platform}</span>
                          {scheduledPost.status === 'posted' ? (
                            <CheckCircle size={14} className="text-green-400" />
                          ) : (
                            <Clock size={14} className="text-orange-400" />
                          )}
                        </div>
                        <p className="text-xs vvl-text-secondary mb-2 line-clamp-2">
                          {scheduledPost.post.content.text}
                        </p>
                        <div className="text-xs vvl-text-secondary">
                          {scheduledPost.status === 'posted' ? 'Posted' : 'Scheduled for'}: {' '}
                          {new Date(scheduledPost.scheduledTime).toLocaleString()}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SchedulingPage; 