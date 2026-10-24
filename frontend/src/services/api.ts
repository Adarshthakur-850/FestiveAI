import axios from 'axios';
import {
  SocialAccount,
  HistoricalPost,
  StyleProfile,
  UpcomingFestival,
  PublishingCampaign,
  AutomationConfig,
  DashboardAnalytics,
  PublishingAttempt,
  CreateCustomEventPayload,
  CreateRandomTestEventPayload,
  CustomEventResponse
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach token if stored
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('festiveai_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to surface human-readable backend error messages
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const serverMessage = error.response?.data?.detail || error.response?.data?.message;
    if (serverMessage) {
      error.message = typeof serverMessage === 'string' ? serverMessage : JSON.stringify(serverMessage);
    }
    return Promise.reject(error);
  }
);

export const api = {
  // Analytics & System
  getAnalytics: async () => {
    const res = await apiClient.get<{ success: boolean; data: DashboardAnalytics }>('/analytics/overview');
    return res.data.data;
  },
  triggerAutonomousCycle: async () => {
    const res = await apiClient.post<{ success: boolean; data: any }>('/scheduler/run-cycle');
    return res.data.data;
  },
  getPublishingAttempts: async () => {
    const res = await apiClient.get<{ success: boolean; data: PublishingAttempt[] }>('/history/attempts');
    return res.data.data;
  },

  // Accounts
  getAccounts: async () => {
    const res = await apiClient.get<{ success: boolean; data: SocialAccount[] }>('/accounts');
    return res.data.data;
  },
  connectMockAccount: async (payload: { platform: string; account_username: string; display_name: string; brand_name: string }) => {
    const res = await apiClient.post<{ success: boolean; message: string; data: SocialAccount }>('/accounts/connect/mock', {
      ...payload,
      account_type: 'business',
      seed_historical_posts: true,
    });
    return res.data.data;
  },
  disconnectAccount: async (accountId: string) => {
    const res = await apiClient.post<{ success: boolean; data: boolean }>(`/accounts/${accountId}/disconnect`);
    return res.data.data;
  },

  // Historical Posts
  getHistoricalPosts: async (accountId: string) => {
    const res = await apiClient.get<{ success: boolean; data: HistoricalPost[] }>(`/accounts/${accountId}/posts`);
    return res.data.data;
  },
  triggerAccountAnalysis: async (accountId: string) => {
    const res = await apiClient.post<{ success: boolean; data: StyleProfile }>(`/accounts/${accountId}/analyze`);
    return res.data.data;
  },

  // Style Profile
  getStyleProfile: async (accountId: string) => {
    const res = await apiClient.get<{ success: boolean; data: StyleProfile }>(`/accounts/${accountId}/profile`);
    return res.data.data;
  },
  updateStyleProfile: async (accountId: string, profile: Partial<StyleProfile>) => {
    const res = await apiClient.put<{ success: boolean; data: StyleProfile }>(`/accounts/${accountId}/profile`, profile);
    return res.data.data;
  },
  uploadBrandLogo: async (accountId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post<{ success: boolean; message: string; data: string }>(
      `/accounts/${accountId}/profile/logo`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return res.data.data;
  },

  // Calendar
  getUpcomingFestivals: async (accountId?: string, daysAhead: number = 180) => {
    const res = await apiClient.get<{ success: boolean; data: UpcomingFestival[] }>('/calendar/upcoming', {
      params: { account_id: accountId, days_ahead: daysAhead }
    });
    return res.data.data;
  },
  updateFestivalPreference: async (accountId: string, festivalId: string, updates: { is_enabled?: boolean; relevance_score?: number }) => {
    const res = await apiClient.put<{ success: boolean; data: boolean }>(`/calendar/accounts/${accountId}/festivals/${festivalId}`, updates);
    return res.data.data;
  },
  createCustomEvent: async (payload: CreateCustomEventPayload) => {
    const res = await apiClient.post<{ success: boolean; message: string; data: CustomEventResponse }>('/calendar/custom-event', payload);
    return res.data.data;
  },
  createRandomTestEvent: async (payload: CreateRandomTestEventPayload) => {
    const res = await apiClient.post<{ success: boolean; message: string; data: CustomEventResponse }>('/calendar/random-test-event', payload);
    return res.data.data;
  },

  // Content Studio & Campaigns
  getCampaigns: async (accountId?: string, status?: string) => {
    const res = await apiClient.get<{ success: boolean; data: PublishingCampaign[] }>('/campaigns', {
      params: { account_id: accountId, status }
    });
    return res.data.data;
  },
  getCampaignById: async (campaignId: string) => {
    const res = await apiClient.get<{ success: boolean; data: PublishingCampaign }>(`/campaigns/${campaignId}`);
    return res.data.data;
  },
  generateCampaign: async (payload: { social_account_id: string; festival_slug: string; year: number; post_pillar?: string; force_regenerate?: boolean }) => {
    const res = await apiClient.post<{ success: boolean; message: string; data: PublishingCampaign }>('/campaigns/generate', payload);
    return res.data.data;
  },
  updateCampaign: async (campaignId: string, payload: { caption_text?: string; hashtags?: string[]; scheduled_publish_time?: string }) => {
    const res = await apiClient.put<{ success: boolean; data: PublishingCampaign }>(`/campaigns/${campaignId}`, payload);
    return res.data.data;
  },
  approveCampaign: async (campaignId: string) => {
    const res = await apiClient.post<{ success: boolean; data: PublishingCampaign }>(`/campaigns/${campaignId}/approve`);
    return res.data.data;
  },
  publishCampaignNow: async (campaignId: string) => {
    const res = await apiClient.post<{ success: boolean; data: any }>(`/campaigns/${campaignId}/publish-now`);
    return res.data.data;
  },
  previewComposite: async (payload: { social_account_id: string; festival_slug: string; greeting_text: string; primary_color: string; accent_color: string }) => {
    const res = await apiClient.post<{ success: boolean; data: { image_url: string; quality_metrics: any } }>('/studio/preview-composite', payload);
    return res.data.data;
  },

  // Automation Settings
  getAutomationConfig: async (accountId: string) => {
    const res = await apiClient.get<{ success: boolean; data: AutomationConfig }>(`/accounts/${accountId}/automation`);
    return res.data.data;
  },
  updateAutomationConfig: async (accountId: string, config: Partial<AutomationConfig>) => {
    const res = await apiClient.put<{ success: boolean; data: AutomationConfig }>(`/accounts/${accountId}/automation`, config);
    return res.data.data;
  },
  triggerAutoPostNow: async (accountId?: string, postPillar?: string) => {
    const res = await apiClient.post<{ success: boolean; message: string; data: any }>(
      '/automation/auto-post-now',
      { account_id: accountId, post_pillar: postPillar }
    );
    return res.data;
  },
  runAutomationCycle: async () => {
    const res = await apiClient.post<{ success: boolean; message: string; data: any }>('/automation/cycle');
    return res.data;
  },
  getAutomationStatus: async () => {
    const res = await apiClient.get<{ success: boolean; data: any }>('/automation/status');
    return res.data.data;
  }
};
