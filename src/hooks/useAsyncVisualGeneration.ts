/**
 * FILENAME: useAsyncVisualGeneration.ts
 * DESCRIPTION/PURPOSE: React hook for async visual content generation with progressive loading
 * Author: JP + 2025-06-28
 * 
 * Features:
 * - Background visual generation with immediate response
 * - Real-time progress tracking via polling
 * - Progressive UI updates as content becomes available
 * - Loading states and error handling
 * - Automatic cleanup and cancellation
 */

import { useState, useEffect, useCallback, useRef } from 'react';

// Types for async visual generation
interface VisualJob {
  job_id: string;
  campaign_id: string;
  post_id: string;
  content_type: 'image' | 'video';
  prompt: string;
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number; // 0.0 to 1.0
  estimated_completion_seconds?: number;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  result_url?: string;
  file_size_bytes?: number;
  metadata: Record<string, any>;
}

interface AsyncVisualResponse {
  success: boolean;
  jobs: VisualJob[];
  total_jobs: number;
  estimated_total_time_seconds: number;
  polling_endpoint: string;
  websocket_endpoint?: string;
  message: string;
}

interface BatchVisualStatus {
  campaign_id: string;
  total_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  overall_progress: number; // 0.0 to 1.0
  jobs: VisualJob[];
  posts_with_visuals: Array<{
    id: string;
    image_url?: string;
    video_url?: string;
  }>;
  is_complete: boolean;
  estimated_completion_seconds?: number;
}

interface UseAsyncVisualGenerationState {
  // Status
  isGenerating: boolean;
  isPolling: boolean;
  hasStarted: boolean;
  isComplete: boolean;
  
  // Progress
  overallProgress: number;
  completedJobs: number;
  totalJobs: number;
  failedJobs: number;
  estimatedTimeRemaining?: number;
  
  // Results
  jobs: VisualJob[];
  postsWithVisuals: Array<{
    id: string;
    image_url?: string;
    video_url?: string;
  }>;
  
  // Error handling
  error?: string;
  
  // Actions
  startGeneration: (posts: any[], businessContext: any, campaignId: string, campaignObjective?: string) => Promise<void>;
  cancelGeneration: () => Promise<void>;
  resetState: () => void;
}

export function useAsyncVisualGeneration(): UseAsyncVisualGenerationState {
  // State management
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPolling, setIsPolling] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  
  const [overallProgress, setOverallProgress] = useState(0);
  const [completedJobs, setCompletedJobs] = useState(0);
  const [totalJobs, setTotalJobs] = useState(0);
  const [failedJobs, setFailedJobs] = useState(0);
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState<number>();
  
  const [jobs, setJobs] = useState<VisualJob[]>([]);
  const [postsWithVisuals, setPostsWithVisuals] = useState<Array<{
    id: string;
    image_url?: string;
    video_url?: string;
  }>>([]);
  
  const [error, setError] = useState<string>();
  
  // Refs for cleanup and polling control
  const pollingIntervalRef = useRef<NodeJS.Timeout>();
  const currentCampaignIdRef = useRef<string>();
  const isActiveRef = useRef(true);
  
  // Cleanup on unmount
  useEffect(() => {
    isActiveRef.current = true;
    return () => {
      isActiveRef.current = false;
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);
  
  // Start async visual generation
  const startGeneration = useCallback(async (
    posts: any[],
    businessContext: any,
    campaignId: string,
    campaignObjective: string = 'increase engagement'
  ) => {
    try {
      console.log('🚀 Starting async visual generation for', posts.length, 'posts');
      
      setIsGenerating(true);
      setHasStarted(true);
      setError(undefined);
      setIsComplete(false);
      currentCampaignIdRef.current = campaignId;
      
      // Start async generation (returns immediately)
      const response = await fetch('/api/v1/content/generate-visuals-async', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          social_posts: posts,
          business_context: businessContext,
          campaign_objective: campaignObjective,
          campaign_id: campaignId
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to start visual generation: ${response.statusText}`);
      }
      
      const data: AsyncVisualResponse = await response.json();
      
      console.log('✅ Visual generation started:', data);
      
      // Update state with initial job info
      setJobs(data.jobs);
      setTotalJobs(data.total_jobs);
      setOverallProgress(0);
      setCompletedJobs(0);
      setFailedJobs(0);
      setEstimatedTimeRemaining(data.estimated_total_time_seconds);
      
      // Start polling for updates
      startPolling(campaignId);
      
    } catch (err) {
      console.error('❌ Failed to start visual generation:', err);
      setError(err instanceof Error ? err.message : 'Failed to start visual generation');
      setIsGenerating(false);
    }
  }, []);
  
  // Start polling for status updates
  const startPolling = useCallback((campaignId: string) => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }
    
    setIsPolling(true);
    
    const pollStatus = async () => {
      try {
        if (!isActiveRef.current || currentCampaignIdRef.current !== campaignId) {
          return;
        }
        
        const response = await fetch(`/api/v1/content/visual-status/${campaignId}`);
        
        if (!response.ok) {
          throw new Error(`Failed to get status: ${response.statusText}`);
        }
        
        const status: BatchVisualStatus = await response.json();
        
        console.log('📊 Visual generation status:', {
          progress: `${status.completed_jobs}/${status.total_jobs}`,
          overallProgress: `${(status.overall_progress * 100).toFixed(0)}%`,
          isComplete: status.is_complete
        });
        
        // Update state with latest status
        setJobs(status.jobs);
        setOverallProgress(status.overall_progress);
        setCompletedJobs(status.completed_jobs);
        setFailedJobs(status.failed_jobs);
        setPostsWithVisuals(status.posts_with_visuals);
        setEstimatedTimeRemaining(status.estimated_completion_seconds);
        
        // Check if generation is complete
        if (status.is_complete) {
          console.log('✅ Visual generation complete!');
          setIsComplete(true);
          setIsGenerating(false);
          setIsPolling(false);
          
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = undefined;
          }
        }
        
      } catch (err) {
        console.error('❌ Polling error:', err);
        // Don't set error for single polling failures, just log them
        // The polling will continue trying
      }
    };
    
    // Initial poll
    pollStatus();
    
    // Set up interval polling (every 3 seconds)
    pollingIntervalRef.current = setInterval(pollStatus, 3000);
    
  }, []);
  
  // Cancel visual generation
  const cancelGeneration = useCallback(async () => {
    try {
      if (!currentCampaignIdRef.current) return;
      
      console.log('🛑 Cancelling visual generation');
      
      // Stop polling
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = undefined;
      }
      
      // Call cancel API
      const response = await fetch(`/api/v1/content/cancel-visual-jobs/${currentCampaignIdRef.current}`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error(`Failed to cancel: ${response.statusText}`);
      }
      
      // Reset state
      setIsGenerating(false);
      setIsPolling(false);
      setIsComplete(false);
      
      console.log('✅ Visual generation cancelled');
      
    } catch (err) {
      console.error('❌ Failed to cancel generation:', err);
      setError(err instanceof Error ? err.message : 'Failed to cancel generation');
    }
  }, []);
  
  // Reset state
  const resetState = useCallback(() => {
    console.log('🔄 Resetting visual generation state');
    
    // Stop polling
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = undefined;
    }
    
    // Reset all state
    setIsGenerating(false);
    setIsPolling(false);
    setHasStarted(false);
    setIsComplete(false);
    setOverallProgress(0);
    setCompletedJobs(0);
    setTotalJobs(0);
    setFailedJobs(0);
    setEstimatedTimeRemaining(undefined);
    setJobs([]);
    setPostsWithVisuals([]);
    setError(undefined);
    currentCampaignIdRef.current = undefined;
  }, []);
  
  return {
    // Status
    isGenerating,
    isPolling,
    hasStarted,
    isComplete,
    
    // Progress
    overallProgress,
    completedJobs,
    totalJobs,
    failedJobs,
    estimatedTimeRemaining,
    
    // Results
    jobs,
    postsWithVisuals,
    
    // Error handling
    error,
    
    // Actions
    startGeneration,
    cancelGeneration,
    resetState
  };
} 