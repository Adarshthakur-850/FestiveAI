import React, { useState, useEffect } from 'react';
import {
  Sliders,
  CheckCircle,
  Clock,
  Globe,
  Bell,
  ShieldCheck,
  Save,
  Zap,
  UserCheck,
  Sparkles,
  ExternalLink,
  Layers,
  Send,
  Loader2
} from 'lucide-react';
import { AutomationConfig, SocialAccount, AutoPostResult } from '../types';
import { api } from '../services/api';

interface AutomationSettingsProps {
  selectedAccount: SocialAccount | null;
  onRefresh: () => void;
}

export const AutomationSettingsPage: React.FC<AutomationSettingsProps> = ({
  selectedAccount,
  onRefresh
}) => {
  const [config, setConfig] = useState<AutomationConfig | null>(null);
  const [mode, setMode] = useState<'approval' | 'autonomous'>('autonomous');
  const [autoPostPillars, setAutoPostPillars] = useState<boolean>(true);
  const [postingCadence, setPostingCadence] = useState<string>('daily');
  const [leadDays, setLeadDays] = useState<number>(7);
  const [publishTime, setPublishTime] = useState<string>('09:00:00');
  const [timezone, setTimezone] = useState<string>('Asia/Kolkata');
  const [maxRetries, setMaxRetries] = useState<number>(3);
  const [notifyEmail, setNotifyEmail] = useState<string>('marketing@techpulse.io');
  const [isLoading, setIsLoading] = useState(false);
  const [isTriggeringAutoPost, setIsTriggeringAutoPost] = useState(false);
  const [autoPostResult, setAutoPostResult] = useState<AutoPostResult | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    if (selectedAccount) {
      loadConfig(selectedAccount.id);
    }
  }, [selectedAccount]);

  const loadConfig = async (accountId: string) => {
    try {
      const cfg = await api.getAutomationConfig(accountId);
      setConfig(cfg);
      setMode(cfg.mode || 'autonomous');
      setAutoPostPillars(cfg.auto_post_pillars !== false);
      setPostingCadence(cfg.posting_cadence || 'daily');
      setLeadDays(cfg.lead_time_days || 7);
      setPublishTime(cfg.target_publish_time || '09:00:00');
      setTimezone(cfg.timezone || 'Asia/Kolkata');
      setMaxRetries(cfg.max_retry_attempts || 3);
      setNotifyEmail(cfg.notify_email || 'marketing@techpulse.io');
    } catch (e) {
      console.error(e);
    }
  };

  const handleSave = async () => {
    if (!selectedAccount) return;
    setIsLoading(true);
    try {
      const updated = await api.updateAutomationConfig(selectedAccount.id, {
        mode,
        auto_post_pillars: autoPostPillars,
        posting_cadence: postingCadence,
        lead_time_days: leadDays,
        target_publish_time: publishTime,
        timezone,
        max_retry_attempts: maxRetries,
        notify_email: notifyEmail
      });
      setConfig(updated);
      setNotice(`Automation rules updated! Mode set to ${mode.toUpperCase()}.`);
      onRefresh();
      setTimeout(() => setNotice(null), 4000);
    } catch (e: any) {
      alert('Error updating automation settings: ' + e?.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTriggerAutoPostNow = async () => {
    if (!selectedAccount) return;
    setIsTriggeringAutoPost(true);
    try {
      const response = await api.triggerAutoPostNow(selectedAccount.id);
      if (response.success && response.data) {
        setAutoPostResult(response.data);
        setNotice(`⚡ Autonomous post published successfully to ${selectedAccount.platform.toUpperCase()}!`);
        onRefresh();
      } else {
        alert('Autonomous trigger failed: ' + (response.message || 'Unknown error'));
      }
    } catch (e: any) {
      alert('Error triggering autonomous post: ' + (e?.message || 'Check connected account credentials'));
    } finally {
      setIsTriggeringAutoPost(false);
    }
  };

  if (!selectedAccount) {
    return (
      <div className="p-12 text-center text-slate-400">
        Please select or connect an account from the header to configure automation rules.
      </div>
    );
  }

  const isInstagram = selectedAccount.platform.toLowerCase() === 'instagram';

  return (
    <div className="space-y-6 max-w-4xl animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight flex items-center space-x-2">
            <span>Automation & Autonomous Publishing Engine</span>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
              Autonomous v1.1
            </span>
          </h1>
          <p className="text-sm text-slate-400">
            Configure hands-free content synthesis, brand guardrails, and autonomous publishing to{' '}
            <span className="font-semibold text-slate-200">@{selectedAccount.account_username}</span> on{' '}
            <span className="capitalize font-semibold text-amber-400">{selectedAccount.platform}</span>.
          </p>
        </div>

        <div className="flex items-center space-x-3 shrink-0">
          <button
            onClick={handleTriggerAutoPostNow}
            disabled={isTriggeringAutoPost}
            className="px-4 py-2.5 rounded-xl text-sm font-bold bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 shadow-lg shadow-amber-500/20 transition-all flex items-center space-x-2 disabled:opacity-50"
            title="Immediately synthesizes creative & caption and publishes directly to social platform"
          >
            {isTriggeringAutoPost ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Publishing Now...</span>
              </>
            ) : (
              <>
                <Zap className="w-4 h-4 fill-current text-slate-950" />
                <span>⚡ Trigger Auto-Post Now</span>
              </>
            )}
          </button>

          <button
            onClick={handleSave}
            disabled={isLoading}
            className="px-5 py-2.5 rounded-xl text-sm font-bold bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 transition-all flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>{isLoading ? 'Saving...' : 'Save Settings'}</span>
          </button>
        </div>
      </div>

      {notice && (
        <div className="p-4 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-sm flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 shrink-0" />
          <span>{notice}</span>
        </div>
      )}

      {/* Autonomous Post Success Card */}
      {autoPostResult && (
        <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-amber-500/40 rounded-2xl p-6 shadow-xl shadow-amber-500/5 space-y-4 animate-fade-in relative overflow-hidden">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white flex items-center space-x-2">
                  <span>Autonomous Post Live on {autoPostResult.platform.toUpperCase()}</span>
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    {autoPostResult.status.toUpperCase()}
                  </span>
                </h3>
                <p className="text-xs text-slate-400">
                  Headline: <span className="text-slate-200 font-semibold">{autoPostResult.headline}</span> · Pillar: <span className="capitalize text-amber-400">{autoPostResult.post_pillar.replace('_', ' ')}</span>
                </p>
              </div>
            </div>

            <button
              onClick={() => setAutoPostResult(null)}
              className="text-slate-400 hover:text-slate-200 text-xs px-2 py-1"
            >
              Dismiss
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-center pt-2">
            <div className="md:col-span-1 rounded-xl overflow-hidden border border-slate-800 bg-slate-950 aspect-square flex items-center justify-center">
              {autoPostResult.image_url ? (
                <img
                  src={autoPostResult.image_url}
                  alt={autoPostResult.headline}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="text-slate-600 text-xs">Generated Artwork</div>
              )}
            </div>

            <div className="md:col-span-3 space-y-3">
              <div className="p-3.5 bg-slate-950/80 rounded-xl border border-slate-800/80 text-xs text-slate-300 font-sans leading-relaxed max-h-28 overflow-y-auto whitespace-pre-line">
                {autoPostResult.caption}
              </div>

              <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                <div className="flex items-center space-x-2 font-mono text-[11px] text-slate-400">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span>Platform ID: <strong className="text-slate-200">{autoPostResult.platform_post_id}</strong></span>
                </div>

                {autoPostResult.permalink && (
                  <a
                    href={autoPostResult.permalink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-bold transition-all"
                  >
                    <span>View Live {isInstagram ? 'Instagram' : 'LinkedIn'} Post</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Mode Selector Card */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
            Publishing Operating Mode
          </label>
          <span className="text-[11px] text-slate-500">
            Controls whether FestiveAI publishes on its own or queues for manual review
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            onClick={() => setMode('autonomous')}
            className={`p-5 rounded-2xl border cursor-pointer transition-all space-y-2 relative ${
              mode === 'autonomous'
                ? 'bg-amber-500/10 border-amber-500 text-white shadow-lg shadow-amber-500/10 ring-1 ring-amber-500/30'
                : 'bg-slate-800/30 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <div className={`p-2 rounded-xl ${mode === 'autonomous' ? 'bg-amber-500 text-slate-950 font-bold' : 'bg-slate-800 text-slate-400'}`}>
                  <Zap className="w-4 h-4 fill-current" />
                </div>
                <h3 className="text-sm font-bold">Autonomous Mode (Recommended)</h3>
              </div>
              {mode === 'autonomous' && (
                <span className="text-[10px] uppercase font-black px-2 py-0.5 rounded-full bg-amber-500 text-slate-950">
                  Fully Autonomous
                </span>
              )}
            </div>
            <p className="text-xs leading-relaxed text-slate-400">
              The AI automatically synthesizes creative artwork, drafts captions matching host persona, enforces brand safety rules, and posts directly to your connected Instagram/LinkedIn account on schedule without requiring per-post manual approval.
            </p>
          </div>

          <div
            onClick={() => setMode('approval')}
            className={`p-5 rounded-2xl border cursor-pointer transition-all space-y-2 relative ${
              mode === 'approval'
                ? 'bg-sky-500/10 border-sky-500 text-white shadow-lg shadow-sky-500/10 ring-1 ring-sky-500/30'
                : 'bg-slate-800/30 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <div className={`p-2 rounded-xl ${mode === 'approval' ? 'bg-sky-500 text-slate-950 font-bold' : 'bg-slate-800 text-slate-400'}`}>
                  <UserCheck className="w-4 h-4" />
                </div>
                <h3 className="text-sm font-bold">Approval Mode (Manual Review)</h3>
              </div>
              {mode === 'approval' && (
                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-sky-500 text-slate-950">
                  Manual Gate
                </span>
              )}
            </div>
            <p className="text-xs leading-relaxed text-slate-400">
              Content is generated ahead of time and queued in Content Studio. Posts remain on hold and are published only after an administrator clicks 'Approve Campaign'.
            </p>
          </div>
        </div>
      </div>

      {/* Routine Content Pillars & Cadence */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-4">
        <div className="flex items-center space-x-2 text-amber-400 font-bold text-sm">
          <Layers className="w-4 h-4" />
          <span>Routine Content Pillars & Cadence</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
          <div className="flex items-start space-x-3 p-4 rounded-xl bg-slate-800/40 border border-slate-700/60">
            <input
              type="checkbox"
              id="autoPostPillars"
              checked={autoPostPillars}
              onChange={(e) => setAutoPostPillars(e.target.checked)}
              className="mt-1 w-4 h-4 accent-amber-500 rounded cursor-pointer"
            />
            <label htmlFor="autoPostPillars" className="text-xs cursor-pointer select-none space-y-1">
              <span className="font-bold text-slate-200 block">Daily Host Persona Content Feed</span>
              <span className="text-slate-400 block leading-relaxed">
                When no astronomical festival is due, autonomously post daily Thought Leadership, Tech Tips, Behind the Scenes, and Product Showcase content on its own.
              </span>
            </label>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 block">Publishing Frequency Cadence</label>
            <select
              value={postingCadence}
              onChange={(e) => setPostingCadence(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-amber-500"
            >
              <option value="daily">Daily Continuous Autonomous Posting (Recommended)</option>
              <option value="festival_only">Cultural Festivals & Custom Milestones Only</option>
              <option value="twice_daily">Twice Daily (Morning Thought Leadership + Evening Wrap)</option>
            </select>
            <p className="text-[11px] text-slate-500">
              Autonomous daemon cycles run in the background and publish automatically according to cadence.
            </p>
          </div>
        </div>
      </div>

      {/* Timing & Timezone Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-4">
          <div className="flex items-center space-x-2 text-amber-400 font-bold text-sm">
            <Clock className="w-4 h-4" />
            <span>Preparation Lead Window</span>
          </div>

          <div>
            <div className="flex items-center justify-between text-xs mb-1.5">
              <span className="text-slate-300 font-semibold">Generation Lead Time</span>
              <span className="text-amber-400 font-bold">{leadDays} Days Before Festival</span>
            </div>
            <input
              type="range"
              min="1"
              max="21"
              value={leadDays}
              onChange={(e) => setLeadDays(parseInt(e.target.value))}
              className="w-full accent-amber-500 bg-slate-800 cursor-pointer"
            />
            <p className="text-[11px] text-slate-500 mt-1">
              FestiveAI will generate and validate artwork {leadDays} days in advance of any festival date.
            </p>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Target Publishing Time</label>
            <input
              type="time"
              step="1"
              value={publishTime}
              onChange={(e) => setPublishTime(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
            />
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-4">
          <div className="flex items-center space-x-2 text-amber-400 font-bold text-sm">
            <Globe className="w-4 h-4" />
            <span>Timezone & Failure Policies</span>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Account Local Timezone</label>
            <select
              value={timezone}
              onChange={(e) => setTimezone(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
            >
              <option value="Asia/Kolkata">Asia/Kolkata (IST +05:30)</option>
              <option value="UTC">UTC (+00:00)</option>
              <option value="America/New_York">America/New_York (EST/EDT)</option>
              <option value="America/Los_Angeles">America/Los_Angeles (PST/PDT)</option>
              <option value="Europe/London">Europe/London (GMT/BST)</option>
              <option value="Asia/Dubai">Asia/Dubai (GST +04:00)</option>
              <option value="Asia/Singapore">Asia/Singapore (SGT +08:00)</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Max Retry Attempts on Transient Error</label>
            <input
              type="number"
              min="1"
              max="5"
              value={maxRetries}
              onChange={(e) => setMaxRetries(parseInt(e.target.value))}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
