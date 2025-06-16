/**
 * API Client Configuration
 * 
 * Author: JP + 2025-06-15
 * 
 * Centralized API client for AI Marketing Campaign Post Generator frontend-backend communication.
 * Handles HTTP requests, error handling, and response formatting.
 */

import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// API Configuration - Environment-based URL resolution
const getApiBaseUrl = (): string => {
  // Production/Cloud deployment - use environment variable
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // Development environment - detect backend location
  const isDevelopment = import.meta.env.DEV;
  const currentHost = window.location.hostname;
  
  if (isDevelopment) {
    // Local development
    if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
      return 'http://localhost:8000';
    }
    // Network development (e.g., testing on mobile devices)
    return `http://${currentHost}:8000`;
  }
  
  // Production fallback - same origin API
  return '/api';
};

const API_BASE_URL = getApiBaseUrl();

// Log configuration for debugging (dev only)
if (import.meta.env.DEV) {
  console.log(`🔗 API Base URL: ${API_BASE_URL}`);
  console.log(`🌍 Environment: ${import.meta.env.MODE}`);
}

// Create axios instance with default configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 45000, // 45 seconds timeout for AI operations (Gemini batch generation can take 20-30s)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens (future use)
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token when available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    // Handle common error scenarios
    if (error.response?.status === 401) {
      // Unauthorized - clear auth and redirect to login (future)
      localStorage.removeItem('auth_token');
    } else if (error.response?.status === 429) {
      // Rate limited
      console.warn('API rate limit exceeded');
    } else if (error.code === 'ECONNABORTED') {
      // Timeout
      console.error('API request timeout');
    }
    
    return Promise.reject(error);
  }
);

// Type definitions for API responses
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface Campaign {
  id: string;
  name: string;
  objective: string;
  business_description: string;
  example_content?: string;
  business_url?: string;
  about_page_url?: string;
  product_service_url?: string;
  campaign_type: 'product' | 'service' | 'brand' | 'event';
  creativity_level: number;
  created_at: string;
  updated_at: string;
  status: 'draft' | 'analyzing' | 'ready' | 'published';
}

export interface CreateCampaignRequest {
  name: string;
  objective: string;
  businessDescription: string;
  exampleContent?: string;
  businessUrl?: string;
  aboutPageUrl?: string;
  productServiceUrl?: string;
  campaignType: 'product' | 'service' | 'brand' | 'event';
  creativityLevel: number;
  uploadedImages?: File[];
  uploadedDocuments?: File[];
  campaignAssets?: File[];
}

export interface ContentGenerationRequest {
  campaign_id: string;
  content_type: 'social_media' | 'blog' | 'email' | 'ad_copy';
  platform?: 'facebook' | 'instagram' | 'twitter' | 'linkedin' | 'tiktok';
  tone?: 'professional' | 'casual' | 'humorous' | 'inspirational';
  include_hashtags?: boolean;
  max_posts?: number;
}

export interface ContentGenerationResponse {
  campaign_id: string;
  content_type: string;
  platform?: string;
  posts: Array<{
    id: string;
    content: string;
    hashtags?: string[];
    platform_specific?: any;
  }>;
  total_posts: number;
  generation_metadata: {
    creativity_level: number;
    tone: string;
    generated_at: string;
  };
}

export interface UrlAnalysisRequest {
  urls: string[];
  analysis_type?: 'business_context' | 'competitor_analysis' | 'content_analysis';
}

export interface UrlAnalysisResponse {
  analysis_results: {
    business_context?: {
      industry: string;
      target_audience: string;
      key_products: string[];
      brand_voice: string;
      competitive_advantages: string[];
    };
    content_insights?: {
      main_topics: string[];
      content_style: string;
      key_messages: string[];
    };
    technical_details?: {
      site_structure: string[];
      performance_notes: string[];
    };
  };
  analysis_metadata: {
    urls_analyzed: string[];
    analysis_type: string;
    analyzed_at: string;
  };
  extracted_insights: string[];
}

export interface FileAnalysisRequest {
  analysis_type?: 'document_analysis' | 'image_analysis' | 'mixed_analysis';
}

export interface FileAnalysisResponse {
  analysis_results: {
    document_insights?: {
      key_topics: string[];
      content_summary: string;
      extracted_text: string;
    };
    image_insights?: {
      visual_elements: string[];
      brand_colors: string[];
      style_analysis: string;
    };
  };
  analysis_metadata: {
    files_analyzed: string[];
    analysis_type: string;
    analyzed_at: string;
  };
  extracted_insights: string[];
}

// API Client Class
export class VideoVentureLaunchAPI {
  
  // Campaign Management
  static async createCampaign(campaignData: CreateCampaignRequest): Promise<Campaign> {
    try {
      // Convert frontend format to backend format
      const backendData = {
        name: campaignData.name,
        objective: campaignData.objective,
        business_description: campaignData.businessDescription,
        example_content: campaignData.exampleContent,
        business_url: campaignData.businessUrl,
        about_page_url: campaignData.aboutPageUrl,
        product_service_url: campaignData.productServiceUrl,
        campaign_type: campaignData.campaignType,
        creativity_level: campaignData.creativityLevel,
      };

      const response = await apiClient.post<ApiResponse<Campaign>>('/api/v1/campaigns/create', backendData);
      
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to create campaign');
      }
      
      return response.data.data;
    } catch (error) {
      console.error('Create campaign error:', error);
      throw this.handleApiError(error);
    }
  }

  static async getCampaigns(page: number = 1, limit: number = 10): Promise<{ campaigns: Campaign[], total: number }> {
    try {
      const response = await apiClient.get<ApiResponse<{ campaigns: Campaign[], total: number }>>(`/api/v1/campaigns/?page=${page}&limit=${limit}`);
      
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to fetch campaigns');
      }
      
      return response.data.data;
    } catch (error) {
      console.error('Get campaigns error:', error);
      throw this.handleApiError(error);
    }
  }

  static async getCampaign(campaignId: string): Promise<Campaign> {
    try {
      const response = await apiClient.get<ApiResponse<Campaign>>(`/api/v1/campaigns/${campaignId}`);
      
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to fetch campaign');
      }
      
      return response.data.data;
    } catch (error) {
      console.error('Get campaign error:', error);
      throw this.handleApiError(error);
    }
  }

  static async updateCampaign(campaignId: string, updates: Partial<CreateCampaignRequest>): Promise<Campaign> {
    try {
      const response = await apiClient.put<ApiResponse<Campaign>>(`/api/v1/campaigns/${campaignId}`, updates);
      
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to update campaign');
      }
      
      return response.data.data;
    } catch (error) {
      console.error('Update campaign error:', error);
      throw this.handleApiError(error);
    }
  }

  static async deleteCampaign(campaignId: string): Promise<void> {
    try {
      const response = await apiClient.delete<ApiResponse>(`/api/v1/campaigns/${campaignId}`);
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to delete campaign');
      }
    } catch (error) {
      console.error('Delete campaign error:', error);
      throw this.handleApiError(error);
    }
  }

  // Content Generation
  static async generateContent(request: ContentGenerationRequest): Promise<ContentGenerationResponse> {
    try {
      const response = await apiClient.post<ApiResponse<ContentGenerationResponse>>('/api/v1/content/generate', request);
      
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to generate content');
      }
      
      return response.data.data;
    } catch (error) {
      console.error('Generate content error:', error);
      throw this.handleApiError(error);
    }
  }

  static async regenerateContent(campaignId: string, postId: string): Promise<ContentGenerationResponse> {
    try {
      const response = await apiClient.post<ApiResponse<ContentGenerationResponse>>('/api/v1/content/regenerate', {
        campaign_id: campaignId,
        post_id: postId
      });
      
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to regenerate content');
      }
      
      return response.data.data;
    } catch (error) {
      console.error('Regenerate content error:', error);
      throw this.handleApiError(error);
    }
  }

  // Bulk content generation for specific post types (used by IdeationPage)
  static async generateBulkContent(request: {
    post_type: 'text_url' | 'text_image' | 'text_video';
    regenerate_count: number;
    business_context: {
      company_name: string;
      objective: string;
      campaign_type: string;
      target_audience?: string;
      business_description?: string;
      business_website?: string;
      product_service_url?: string;
    };
    creativity_level: number;
  }): Promise<{
    new_posts: Array<{
      id: string;
      type: string;
      content: string;
      url?: string;
      image_prompt?: string;
      video_prompt?: string;
      hashtags: string[];
      platform_optimized: any;
      engagement_score: number;
      selected: boolean;
    }>;
    regeneration_metadata: any;
    processing_time: number;
  }> {
    try {
      const response = await apiClient.post('/api/v1/content/regenerate', request);
      
      if (!response.data) {
        throw new Error('No response data received');
      }
      
      return response.data;
    } catch (error) {
      console.error('Generate bulk content error:', error);
      throw this.handleApiError(error);
    }
  }

  // Visual Content Generation
  static async generateVisualContent(request: {
    social_posts: Array<{
      id: string | number;
      type: 'text_image' | 'text_video' | 'text_url';
      content: string;
      platform: string;
      hashtags?: string[];
    }>;
    business_context: {
      business_name?: string;
      industry?: string;
      objective?: string;
      target_audience?: string;
      brand_voice?: string;
    };
    campaign_objective: string;
    target_platforms?: string[];
  }): Promise<{
    posts_with_visuals: Array<{
      id: string | number;
      type: string;
      content: string;
      platform: string;
      hashtags?: string[];
      image_prompt?: string;
      image_url?: string;
      video_prompt?: string;
      video_url?: string;
    }>;
    visual_strategy: any;
    generation_metadata: any;
    created_at: string;
  }> {
    try {
      const response = await apiClient.post('/api/v1/content/generate-visuals', request);
      
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to generate visual content');
      }
      
      return response.data.data;
    } catch (error) {
      console.error('Generate visual content error:', error);
      throw this.handleApiError(error);
    }
  }

  // URL Analysis
  static async analyzeUrls(request: UrlAnalysisRequest): Promise<UrlAnalysisResponse> {
    try {
      const response = await apiClient.post<ApiResponse<UrlAnalysisResponse>>('/api/v1/analysis/url', request);
      
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to analyze URLs');
      }
      
      return response.data.data;
    } catch (error) {
      console.error('Analyze URLs error:', error);
      throw this.handleApiError(error);
    }
  }

  // File Analysis
  static async analyzeFiles(files: File[], request?: FileAnalysisRequest): Promise<FileAnalysisResponse> {
    try {
      const formData = new FormData();
      files.forEach((file, index) => {
        formData.append(`files`, file);
      });
      
      if (request?.analysis_type) {
        formData.append('analysis_type', request.analysis_type);
      }

      const response = await apiClient.post<ApiResponse<FileAnalysisResponse>>('/api/v1/analysis/files', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      if (!response.data.success || !response.data.data) {
        throw new Error(response.data.error || 'Failed to analyze files');
      }
      
      return response.data.data;
    } catch (error) {
      console.error('Analyze files error:', error);
      throw this.handleApiError(error);
    }
  }

  // Error handling helper
  private static handleApiError(error: any): Error {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiResponse>;
      
      if (axiosError.response?.data?.error) {
        return new Error(axiosError.response.data.error);
      } else if (axiosError.response?.data?.message) {
        return new Error(axiosError.response.data.message);
      } else if (axiosError.message) {
        return new Error(`API Error: ${axiosError.message}`);
      }
    }
    
    return error instanceof Error ? error : new Error('Unknown API error');
  }
}

// Export default instance for convenience
export default VideoVentureLaunchAPI; 