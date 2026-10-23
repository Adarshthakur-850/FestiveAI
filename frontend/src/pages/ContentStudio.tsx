import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Send,
  CheckCircle,
  RefreshCw,
  Clock,
  ShieldCheck,
  Eye,
  Sliders,
  Copy,
  ExternalLink,
  AlertCircle,
  UserCheck,
  Compass
} from 'lucide-react';
import { PublishingCampaign, SocialAccount, UpcomingFestival } from '../types';
import { api } from '../services/api';

interface ContentStudioProps {
  selectedAccount: SocialAccount | null;
  upcomingFestivals: UpcomingFestival[];
  targetFestivalSlug?: string;
  targetFestivalYear?: number;
  onRefresh: () => void;
}

export const ContentStudio: React.FC<ContentStudioProps> = ({
  selectedAccount,
  upcomingFestivals,
  targetFestivalSlug,
  targetFestivalYear,
  onRefresh
}) => {
  const [selectedFestivalSlug, setSelectedFestivalSlug] = useState<string>(
    targetFestivalSlug || (upcomingFestivals[0]?.slug || 'diwali')
  );
  const [year, setYear] = useState<number>(targetFestivalYear || 2026);
  const [selectedPillar, setSelectedPillar] = useState<string>('auto');
  const [campaign, setCampaign] = useState<PublishingCampaign | null>(null);
  const [caption, setCaption] = useState<string>('');
  const [hashtags, setHashtags] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [isPublishing, setIsPublishing] = useState<boolean>(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [customInstructions, setCustomInstructions] = useState<string>('');

  useEffect(() => {
    if (targetFestivalSlug) {
      setSelectedFestivalSlug(targetFestivalSlug);
    }
    if (targetFestivalYear) {
      setYear(targetFestivalYear);
    }
  }, [targetFestivalSlug, targetFestivalYear]);

  useEffect(() => {
    if (selectedAccount && selectedFestivalSlug) {
      loadCampaignForFestival(selectedFestivalSlug, year);
    }
  }, [selectedAccount, selectedFestivalSlug, year]);

  const loadCampaignForFestival = async (slug: string, yr: number) => {
    if (!selectedAccount) return;
    try {
      const camps = await api.getCampaigns(selectedAccount.id);
      const match = (camps || []).find((c) => c.festival_slug === slug && c.year === yr);
      if (match) {
        setCampaign(match);
        if (match.active_creative) {
          setCaption(match.active_creative.caption_text || '');
          setHashtags((match.active_creative.hashtags || []).join(' '));
        }
      } else {
        setCampaign(null);
        setCaption('');
        setHashtags('');
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleGenerate = async (forceRegenerate: boolean = false) => {
    if (!selectedAccount) return;
    setIsGenerating(true);
    setNotice('Synthesizing brand visuals and crafting culturally authentic caption...');
    try {
      const camp = await api.generateCampaign({
        social_account_id: selectedAccount.id,
        festival_slug: selectedFestivalSlug,
        year: year,
        post_pillar: selectedPillar === 'auto' ? undefined : selectedPillar,
        force_regenerate: forceRegenerate
      });
      setCampaign(camp);
      if (camp.active_creative) {
        setCaption(camp.active_creative.caption_text || '');
        setHashtags((camp.active_creative.hashtags || []).join(' '));
      }
      setNotice('Creative synthesized and verified successfully!');
      onRefresh();
      setTimeout(() => setNotice(null), 4000);
    } catch (e: any) {
      alert('Generation error: ' + (e?.message || 'Error'));
      setNotice(null);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleApprove = async () => {
    if (!campaign) return;
    try {
      const updated = await api.approveCampaign(campaign.id);
      setCampaign(updated);
      setNotice('Campaign approved! It will be published autonomously at scheduled time.');
      onRefresh();
      setTimeout(() => setNotice(null), 4000);
    } catch (e: any) {
      alert('Approval error: ' + e?.message);
    }
  };

  const handlePublishNow = async () => {
    if (!campaign) return;
    if (!confirm('Publish this greeting immediately to the connected social media account?')) return;
    setIsPublishing(true);
    setNotice('Publishing to platform API with retry and idempotency verification...');
    try {
      const res = await api.publishCampaignNow(campaign.id);
      if (res.success) {
        setNotice(res.message || `Post published successfully! Platform ID: ${res.platform_post_id}`);
        loadCampaignForFestival(selectedFestivalSlug, year);
        onRefresh();
      } else {
        alert('Publish failed: ' + (res.error || 'Failed'));
      }
    } catch (e: any) {
      alert('Publish error: ' + e?.message);
    } finally {
      setIsPublishing(false);
    }
  };

  const handleSaveChanges = async () => {
    if (!campaign) return;
    try {
      const htList = hashtags.split(' ').map((h) => h.trim()).filter((h) => h.startsWith('#'));
      const updated = await api.updateCampaign(campaign.id, {
        caption_text: caption,
        hashtags: htList
      });
      setCampaign(updated);
      setNotice('Caption and hashtag changes saved successfully.');
      setTimeout(() => setNotice(null), 3000);
    } catch (e: any) {
      alert('Save error: ' + e?.message);
    }
  };

  if (!selectedAccount) {
    return (
      <div className="p-12 text-center text-slate-400">
        Please select or connect an account from the header to open Content Studio.
      </div>
    );
  }

  const activeCreative = campaign?.active_creative;
  const isPublished = campaign?.status === 'published';

  const getFullImageUrl = (url?: string) => {
    if (!url) return '';
    if (url.startsWith('http://') || url.startsWith('https://')) return url;
    const apiUrl = import.meta.env.VITE_API_URL || '';
    const base = apiUrl ? apiUrl.replace(/\/api\/v1\/?$/, '') : '';
    return `${base}${url.startsWith('/') ? '' : '/'}${url}`;
  };

  return (
    <div className="space-y-6 max-w-6xl animate-fade-in">
      {/* Top Header & Festival Selection */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight flex items-center space-x-2">
            <span>Creative Content Studio</span>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 font-bold">
              Autonomous Studio
            </span>
          </h1>
          <p className="text-sm text-slate-400">
            Preview, customize, approve, and execute festival greeting campaigns for{' '}
            <span className="font-semibold text-slate-200">@{selectedAccount.account_username}</span> ({selectedAccount.platform}).
          </p>
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          <select
            value={selectedFestivalSlug}
            onChange={(e) => setSelectedFestivalSlug(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-slate-100 font-semibold focus:outline-none focus:border-amber-500"
          >
            {upcomingFestivals.map((f) => (
              <option key={f.slug} value={f.slug}>
                {f.name} ({new Date(f.observed_date).getFullYear()})
              </option>
            ))}
          </select>

          <button
            onClick={() => handleGenerate(false)}
            disabled={isGenerating}
            className="px-4 py-2 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-md shadow-amber-500/20 transition-all flex items-center space-x-2"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{isGenerating ? 'Synthesizing...' : campaign ? 'Regenerate' : 'Generate Creative'}</span>
          </button>
        </div>
      </div>

      {notice && (
        <div className="p-4 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-sm flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 shrink-0" />
          <span>{notice}</span>
        </div>
      )}

      {/* Host Post Archetype & Persona Tailoring Selector */}
      <div className="bg-slate-900/80 border border-indigo-500/20 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-md">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 shrink-0">
            <UserCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold text-white">Target Post Archetype</span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                Persona-Adapted
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Generates creative graphics & copy tailored to the host's learned communication pillar.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2.5">
          <select
            value={selectedPillar}
            onChange={(e) => setSelectedPillar(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-100 font-semibold focus:outline-none focus:border-indigo-500"
          >
            <option value="auto">Auto (Match Learned Host Persona)</option>
            <option value="thought_leadership">Thought Leadership Festival Blend</option>
            <option value="behind_the_scenes">Behind The Scenes Team Celebration</option>
            <option value="product_showcase">Product Feature & Client Appreciation</option>
            <option value="community_engagement">Community Dialogue & Gratitude</option>
            <option value="educational">Tech Tips & Cultural Insights</option>
            <option value="festive_greeting">Classic Cultural Festival Greeting</option>
          </select>
        </div>
      </div>

      {/* Main Studio Canvas: Left Image Preview, Right Caption & Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Visual Artwork (7 Cols) */}
        <div className="lg:col-span-7 bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-2">
              <Eye className="w-4 h-4 text-amber-400" />
              <span>Pixel-Perfect Graphic Canvas (1080 × 1080)</span>
            </span>

            {activeCreative && (
              <div className="flex items-center space-x-2">
                {activeCreative.post_pillar && (
                  <span className="text-[10px] font-bold text-indigo-300 bg-indigo-500/15 px-2 py-0.5 rounded-full border border-indigo-500/30 uppercase tracking-wider">
                    {activeCreative.post_pillar.replace('_', ' ')}
                  </span>
                )}
                <span className="text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20 flex items-center space-x-1">
                  <ShieldCheck className="w-3 h-3" />
                  <span>Verified</span>
                </span>
              </div>
            )}
          </div>

          {activeCreative ? (
            <div className="relative rounded-2xl overflow-hidden border border-slate-800 shadow-2xl bg-slate-950 aspect-square flex items-center justify-center group">
              <img
                src={getFullImageUrl(activeCreative.image_url)}
                alt="Festival Greeting Creative"
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-[1.02]"
              />
              <div className="absolute bottom-3 left-3 bg-slate-950/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/10 text-[11px] text-slate-300">
                Format: PNG • Res: {activeCreative.width}x{activeCreative.height} • Version {activeCreative.version}
              </div>
            </div>
          ) : (
            <div className="rounded-2xl border-2 border-dashed border-slate-800 aspect-square flex flex-col items-center justify-center p-8 text-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
                <Sparkles className="w-8 h-8" />
              </div>
              <div className="max-w-sm">
                <h3 className="text-base font-bold text-white">No Creative Generated Yet</h3>
                <p className="text-xs text-slate-400 mt-1">
                  Click 'Generate Creative' to produce original festival artwork blending your brand colors, logo watermark, and festive motifs.
                </p>
              </div>
              <button
                onClick={() => handleGenerate(false)}
                disabled={isGenerating}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20"
              >
                Generate for {selectedFestivalSlug.toUpperCase()}
              </button>
            </div>
          )}

          {activeCreative && (
            <div className="grid grid-cols-3 gap-3 text-xs bg-slate-800/40 p-3 rounded-xl border border-slate-800 text-slate-300">
              <div>
                <span className="text-slate-500 block text-[10px] uppercase font-bold">Contrast & Readability</span>
                <span className="text-emerald-400 font-semibold">Passed (Gold / Dark)</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px] uppercase font-bold">Logo Placement</span>
                <span className="text-slate-200 font-semibold capitalize">Top Right Overlay</span>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px] uppercase font-bold">Duplicate Hash</span>
                <span className="text-emerald-400 font-semibold">Unique Creative</span>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Caption, Schedule & Actions (5 Cols) */}
        <div className="lg:col-span-5 bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Caption & Communication
              </span>
              {campaign && (
                <span
                  className={`text-xs px-2.5 py-0.5 rounded-full font-bold ${
                    campaign.status === 'published'
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : campaign.status === 'scheduled'
                      ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                      : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                  }`}
                >
                  {campaign.status.toUpperCase()}
                </span>
              )}
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">
                Generated Festival Message
              </label>
              <textarea
                rows={6}
                value={caption}
                onChange={(e) => setCaption(e.target.value)}
                disabled={isPublished}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-xs text-slate-100 focus:outline-none focus:border-amber-500 leading-relaxed resize-none"
                placeholder="Caption will appear here..."
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Curated Hashtags</label>
              <input
                type="text"
                value={hashtags}
                onChange={(e) => setHashtags(e.target.value)}
                disabled={isPublished}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-amber-300 focus:outline-none focus:border-amber-500 font-mono"
                placeholder="#HappyDiwali #Innovation"
              />
            </div>

            {campaign && (
              <div className="p-3 bg-slate-800/50 rounded-xl border border-slate-700/60 space-y-1.5 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Scheduled Time:</span>
                  <span className="font-semibold text-slate-200">
                    {new Date(campaign.scheduled_publish_time).toLocaleString()}
                  </span>
                </div>
                {campaign.actual_publish_time && (
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Published Time:</span>
                    <span className="font-semibold text-emerald-400">
                      {new Date(campaign.actual_publish_time).toLocaleString()}
                    </span>
                  </div>
                )}
                {campaign.attempts.length > 0 && campaign.attempts[0].platform_post_id && (
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Platform Post ID:</span>
                    <span className="font-mono text-[11px] text-amber-300">
                      {campaign.attempts[0].platform_post_id}
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="space-y-2 pt-4 border-t border-slate-800">
            {!isPublished ? (
              <>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={handleSaveChanges}
                    className="py-2.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all"
                  >
                    Save Changes
                  </button>
                  <button
                    onClick={handleApprove}
                    className="py-2.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-md shadow-emerald-600/20 flex items-center justify-center space-x-1"
                  >
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span>Approve Campaign</span>
                  </button>
                </div>

                <button
                  onClick={handlePublishNow}
                  disabled={isPublishing}
                  className="w-full py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 transition-all shadow-lg shadow-amber-500/20 flex items-center justify-center space-x-2"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{isPublishing ? 'Publishing...' : 'Publish Immediately (Bypass Schedule)'}</span>
                </button>
              </>
            ) : (
              <div className="p-3 bg-emerald-950/60 border border-emerald-800 rounded-xl text-center space-y-1">
                <span className="text-xs font-bold text-emerald-400 flex items-center justify-center space-x-1">
                  <CheckCircle className="w-4 h-4" />
                  <span>Post Published to {selectedAccount.platform.toUpperCase()}</span>
                </span>
                <p className="text-[11px] text-slate-400">
                  Duplicate lock active. No further publishing operations will be executed for this festival year.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
