export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: string;
  organization?: {
    id: string;
    name: string;
    slug: string;
  };
}

export interface SocialAccount {
  id: string;
  platform: 'instagram' | 'linkedin';
  account_type: string;
  platform_account_id: string;
  account_username: string;
  display_name?: string;
  profile_picture_url?: string;
  is_connected: boolean;
  status: string;
  has_credentials: boolean;
  historical_posts_count: number;
  has_style_profile: boolean;
  automation_mode?: string;
  created_at: string;
}

export interface HistoricalPost {
  id: string;
  platform_post_id: string;
  published_at: string;
  caption?: string;
  hashtags: string[];
  media_type: string;
  media_url?: string;
  image_width?: number;
  image_height?: number;
  detected_festival?: string;
  is_festival_greeting: boolean;
  festival_confidence: number;
  language: string;
  post_pillar?: string;
  post_archetype?: string;
}

export interface PostTypeItem {
  pillar: string;
  name: string;
  percentage: number;
  hook_style: string;
  cta_style: string;
  engagement_vibe: string;
}

export interface StyleProfile {
  id: string;
  social_account_id: string;
  brand_name?: string;
  brand_logo_url?: string;
  dominant_colors: string[];
  secondary_colors: string[];
  background_style: string;
  typography_style: string;
  logo_placement: string;
  formality_score: number;
  emoji_frequency: string;
  preferred_languages: string[];
  default_aspect_ratio: string;
  prohibited_terms: string[];
  required_sign_off?: string;
  festival_overrides: Record<string, any>;
  persona_type?: string;
  industry_niche?: string;
  target_audience?: string;
  content_pillars?: Record<string, number>;
  post_types?: PostTypeItem[];
  signature_hooks?: string[];
  visual_archetype?: string;
  confidence_score: number;
  version: number;
  last_analyzed_at: string;
}

export interface UpcomingFestival {
  festival_id: string;
  slug: string;
  name: string;
  category: string;
  observed_date: string;
  year: number;
  days_until: number;
  relevance_score: number;
  is_enabled: boolean;
  status: string;
  campaign_id?: string;
  verification_source: string;
}

export interface GeneratedCreative {
  id: string;
  campaign_id: string;
  version: number;
  image_url: string;
  local_image_path: string;
  caption_text: string;
  hashtags: string[];
  width: number;
  height: number;
  aspect_ratio: string;
  post_pillar?: string;
  model_used: string;
  quality_score: number;
  quality_checks: Record<string, any>;
  is_selected: boolean;
  created_at: string;
}

export interface PublishingAttempt {
  id: string;
  campaign_id: string;
  attempt_number: number;
  started_at: string;
  finished_at?: string;
  status: string;
  platform_post_id?: string;
  platform_response: Record<string, any>;
  error_code?: string;
  error_traceback?: string;
}

export interface PublishingCampaign {
  id: string;
  social_account_id: string;
  festival_id: string;
  festival_name?: string;
  festival_slug?: string;
  platform?: string;
  account_username?: string;
  year: number;
  campaign_identifier: string;
  scheduled_publish_time: string;
  actual_publish_time?: string;
  status: 'detected' | 'planned' | 'generating' | 'generated' | 'scheduled' | 'publishing' | 'published' | 'failed' | 'needs_authorization';
  post_pillar?: string;
  error_message?: string;
  retry_count: number;
  is_approved: boolean;
  active_creative?: GeneratedCreative;
  creatives: GeneratedCreative[];
  attempts: PublishingAttempt[];
  created_at: string;
}

export interface AutomationConfig {
  id: string;
  social_account_id: string;
  mode: 'approval' | 'autonomous';
  lead_time_days: number;
  target_publish_time: string;
  timezone: string;
  auto_regenerate_on_rejection: boolean;
  max_retry_attempts: number;
  notify_email?: string;
  notify_on_generation: boolean;
  notify_on_publish: boolean;
}

export interface DashboardAnalytics {
  total_accounts: number;
  connected_accounts: number;
  upcoming_festivals_30d: number;
  posts_generated: number;
  posts_scheduled: number;
  posts_published: number;
  failed_attempts: number;
  autonomous_mode_enabled_count: number;
  system_health: string;
}
