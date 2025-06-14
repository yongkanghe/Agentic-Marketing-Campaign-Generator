import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMarketingContext } from '@/contexts/MarketingContext';
import { MaterialCard } from '@/components/MaterialCard';
import { MaterialButton } from '@/components/MaterialButton';
import { MaterialAppBar } from '@/components/MaterialAppBar';
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
  ExternalLink
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
  
  const platforms = [
    { id: 'linkedin', name: 'LinkedIn', connected: true },
    { id: 'twitter', name: 'Twitter/X', connected: true },
    { id: 'instagram', name: 'Instagram', connected: false },
    { id: 'facebook', name: 'Facebook', connected: false },
    { id: 'tiktok', name: 'TikTok', connected: false }
  ];

  useEffect(() => {
    if (!currentCampaign) {
      navigate('/');
    }
  }, [currentCampaign, navigate]);

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

  const handleConnectPlatform = (platformId: string) => {
    toast.info(`Redirecting to ${platformId} authentication...`);
    // TODO: Implement OAuth flow for social media platforms
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
    <div className="min-h-screen bg-background flex flex-col">
      <MaterialAppBar title="Schedule & Publish">
        <MaterialButton 
          variant="outline" 
          className="mr-2 flex items-center gap-1"
          onClick={() => navigate('/ideation')}
        >
          <ArrowLeft size={16} />
          <span>Back to Posts</span>
        </MaterialButton>
        
        <MaterialButton
          variant="outline"
          onClick={() => setShowScheduledPanel(!showScheduledPanel)}
          className="flex items-center gap-1"
        >
          <Calendar size={16} />
          <span>Scheduled ({scheduledPosts.length})</span>
          {showScheduledPanel ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
        </MaterialButton>
      </MaterialAppBar>
      
      <div className="flex flex-1">
        {/* Main Content */}
        <div className={`flex-1 transition-all duration-300 ${showScheduledPanel ? 'mr-80' : ''}`}>
          <div className="container py-8">
            <div className="max-w-4xl mx-auto space-y-6">
              
              {/* Campaign Summary */}
              <MaterialCard className="p-6">
                <h2 className="text-xl font-medium mb-4">{currentCampaign.name} - Ready to Schedule</h2>
                <div className="grid md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Selected Posts:</span> {selectedPosts.length}
                  </div>
                  <div>
                    <span className="font-medium">Campaign Type:</span> {currentCampaign.campaignType}
                  </div>
                  <div>
                    <span className="font-medium">Objective:</span> {currentCampaign.objective}
                  </div>
                </div>
              </MaterialCard>

              {/* Social Media Platform Selection */}
              <MaterialCard className="p-6">
                <h3 className="text-lg font-medium mb-4">Select Social Media Platforms</h3>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {platforms.map(platform => (
                    <div
                      key={platform.id}
                      className={`p-4 border rounded-lg cursor-pointer transition-all ${
                        selectedPlatforms.includes(platform.id)
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      } ${!platform.connected ? 'opacity-50' : ''}`}
                      onClick={() => platform.connected && togglePlatform(platform.id)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <PlatformIcon platform={platform.id} />
                          <span className="font-medium">{platform.name}</span>
                        </div>
                        {platform.connected ? (
                          <CheckCircle size={16} className="text-green-600" />
                        ) : (
                          <AlertCircle size={16} className="text-orange-600" />
                        )}
                      </div>
                      
                      {!platform.connected ? (
                        <MaterialButton
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleConnectPlatform(platform.id);
                          }}
                          className="w-full"
                        >
                          Connect Account
                        </MaterialButton>
                      ) : (
                        <div className="text-xs text-muted-foreground">
                          {selectedPlatforms.includes(platform.id) ? 'Selected for posting' : 'Click to select'}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </MaterialCard>

              {/* Scheduling Configuration */}
              <MaterialCard className="p-6">
                <h3 className="text-lg font-medium mb-4">Scheduling Settings</h3>
                
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="start-time">Start Time</Label>
                      <Input
                        id="start-time"
                        type="time"
                        value={startTime}
                        onChange={(e) => setStartTime(e.target.value)}
                        className="mt-1"
                      />
                    </div>
                    
                    <div>
                      <Label>Posting Interval: {schedulingInterval[0]} hours</Label>
                      <div className="mt-2 px-2">
                        <Slider
                          value={schedulingInterval}
                          onValueChange={setSchedulingInterval}
                          max={24}
                          min={1}
                          step={1}
                          className="w-full"
                        />
                      </div>
                      <div className="flex justify-between text-xs text-muted-foreground mt-1">
                        <span>1 hour</span>
                        <span>24 hours</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <h4 className="font-medium text-blue-900 mb-2">Scheduling Preview</h4>
                      <div className="text-sm text-blue-700 space-y-1">
                        <p>📅 Start: Today at {startTime}</p>
                        <p>⏱️ Interval: Every {schedulingInterval[0]} hours</p>
                        <p>📱 Platforms: {selectedPlatforms.length} selected</p>
                        <p>📝 Posts: {selectedPosts.length} ready</p>
                      </div>
                    </div>
                    
                    <div className="text-xs text-muted-foreground">
                      ⚠️ Keep this page open to maintain active scheduling session
                    </div>
                  </div>
                </div>
              </MaterialCard>

              {/* Selected Posts Preview */}
              <MaterialCard className="p-6">
                <h3 className="text-lg font-medium mb-4">Posts Ready for Scheduling</h3>
                <div className="space-y-4">
                  {selectedPosts.map((post, index) => (
                    <div key={post.id} className="p-4 border rounded-lg">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">#{index + 1}</span>
                          <PlatformIcon platform={post.platform} />
                          <span className="text-sm text-muted-foreground">{post.type}</span>
                        </div>
                        <div className="text-xs text-muted-foreground">
                          Will post in {(index + 1) * schedulingInterval[0]} hours
                        </div>
                      </div>
                      
                      <p className="text-sm mb-2">{post.content.text}</p>
                      
                      {post.content.imageUrl && (
                        <img 
                          src={post.content.imageUrl} 
                          alt="Post preview" 
                          className="w-32 h-24 object-cover rounded mb-2"
                        />
                      )}
                      
                      {post.content.productUrl && (
                        <div className="text-xs text-blue-600 mb-2">
                          🔗 {post.content.productUrl}
                        </div>
                      )}
                      
                      <div className="flex gap-1">
                        {post.content.hashtags.map(tag => (
                          <span key={tag} className="text-xs text-blue-600">{tag}</span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </MaterialCard>

              {/* Action Buttons */}
              <div className="flex justify-between items-center">
                <div className="flex gap-4">
                  <MaterialButton
                    variant="outline"
                    onClick={exportCampaignTemplate}
                    className="flex items-center gap-2"
                  >
                    <Download size={16} />
                    <span>Export Template</span>
                  </MaterialButton>
                </div>
                
                <div className="flex gap-4">
                  {isSchedulingActive ? (
                    <MaterialButton
                      variant="outline"
                      onClick={handleStopScheduling}
                      className="flex items-center gap-2"
                    >
                      <Pause size={16} />
                      <span>Pause Scheduling</span>
                    </MaterialButton>
                  ) : (
                    <MaterialButton
                      onClick={handleStartScheduling}
                      disabled={selectedPlatforms.length === 0}
                      className="flex items-center gap-2"
                    >
                      <Play size={16} />
                      <span>Start Scheduling</span>
                    </MaterialButton>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Scheduled Posts Slide-out Panel */}
        {showScheduledPanel && (
          <div className="fixed right-0 top-0 h-full w-80 bg-white border-l shadow-lg z-50 overflow-y-auto">
            <div className="p-4 border-b">
              <div className="flex items-center justify-between">
                <h3 className="font-medium">Scheduled Posts</h3>
                <MaterialButton
                  variant="outline"
                  size="sm"
                  onClick={() => setShowScheduledPanel(false)}
                >
                  <ChevronRight size={16} />
                </MaterialButton>
              </div>
            </div>
            
            <div className="p-4 space-y-4">
              {scheduledPosts.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  <Calendar size={48} className="mx-auto mb-4 opacity-50" />
                  <p>No posts scheduled yet</p>
                </div>
              ) : (
                scheduledPosts.map(scheduled => (
                  <div key={scheduled.id} className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <PlatformIcon platform={scheduled.platform} />
                        <span className="text-sm font-medium">{scheduled.platform}</span>
                      </div>
                      <div className={`text-xs px-2 py-1 rounded ${
                        scheduled.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                        scheduled.status === 'posted' ? 'bg-green-100 text-green-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {scheduled.status}
                      </div>
                    </div>
                    
                    <p className="text-xs text-muted-foreground mb-2">
                      {new Date(scheduled.scheduledTime).toLocaleString()}
                    </p>
                    
                    <p className="text-sm">{scheduled.post.content.text.slice(0, 100)}...</p>
                    
                    {scheduled.status === 'posted' && (
                      <MaterialButton
                        variant="outline"
                        size="sm"
                        className="mt-2 w-full flex items-center gap-1"
                      >
                        <ExternalLink size={12} />
                        <span>View Post</span>
                      </MaterialButton>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SchedulingPage; 