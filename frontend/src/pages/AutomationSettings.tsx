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
  UserCheck
} from 'lucide-react';
import { AutomationConfig, SocialAccount } from '../types';
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
  const [mode, setMode] = useState<'approval' | 'autonomous'>('approval');
  const [leadDays, setLeadDays] = useState<number>(7);
  const [publishTime, setPublishTime] = useState<string>('09:00:00');
  const [timezone, setTimezone] = useState<string>('Asia/Kolkata');
  const [maxRetries, setMaxRetries] = useState<number>(3);
  const [notifyEmail, setNotifyEmail] = useState<string>('marketing@techpulse.io');
  const [isLoading, setIsLoading] = useState(false);
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
      setMode(cfg.mode);
      setLeadDays(cfg.lead_time_days);
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

  if (!selectedAccount) {
    return (
      <div className="p-12 text-center text-slate-400">
        Please select or connect an account from the header to configure automation rules.
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Automation & Scheduling Engine</h1>
          <p className="text-sm text-slate-400">
            Define autonomous lead windows, time-zone offsets, and operating mode for{' '}
            <span className="font-semibold text-slate-200">@{selectedAccount.account_username}</span>.
          </p>
        </div>

        <button
          onClick={handleSave}
          disabled={isLoading}
          className="px-5 py-2.5 rounded-xl text-sm font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-md shadow-amber-500/20 transition-all flex items-center space-x-2 shrink-0"
        >
          <Save className="w-4 h-4" />
          <span>{isLoading ? 'Saving...' : 'Save Settings'}</span>
        </button>
      </div>

      {notice && (
        <div className="p-4 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-sm flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 shrink-0" />
          <span>{notice}</span>
        </div>
      )}

      {/* Mode Selector Card */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-4">
        <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
          Publishing Operating Mode
        </label>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            onClick={() => setMode('autonomous')}
            className={`p-5 rounded-2xl border cursor-pointer transition-all space-y-2 relative ${
              mode === 'autonomous'
                ? 'bg-amber-500/10 border-amber-500 text-white shadow-lg shadow-amber-500/10'
                : 'bg-slate-800/30 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <div className={`p-2 rounded-xl ${mode === 'autonomous' ? 'bg-amber-500 text-slate-950' : 'bg-slate-800 text-slate-400'}`}>
                  <Zap className="w-4 h-4" />
                </div>
                <h3 className="text-sm font-bold">Autonomous Mode</h3>
              </div>
              {mode === 'autonomous' && (
                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-amber-500 text-slate-950">
                  Active Target
                </span>
              )}
            </div>
            <p className="text-xs leading-relaxed text-slate-400">
              The AI detects upcoming festivals, generates customized creatives, validates brand rules, and publishes automatically at the scheduled time without requiring manual per-post approval.
            </p>
          </div>

          <div
            onClick={() => setMode('approval')}
            className={`p-5 rounded-2xl border cursor-pointer transition-all space-y-2 relative ${
              mode === 'approval'
                ? 'bg-sky-500/10 border-sky-500 text-white shadow-lg shadow-sky-500/10'
                : 'bg-slate-800/30 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <div className={`p-2 rounded-xl ${mode === 'approval' ? 'bg-sky-500 text-slate-950' : 'bg-slate-800 text-slate-400'}`}>
                  <UserCheck className="w-4 h-4" />
                </div>
                <h3 className="text-sm font-bold">Approval Mode</h3>
              </div>
              {mode === 'approval' && (
                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-full bg-sky-500 text-slate-950">
                  Selected
                </span>
              )}
            </div>
            <p className="text-xs leading-relaxed text-slate-400">
              Content is generated ahead of time and queued in Content Studio. Posts are published only after an administrator clicks 'Approve Campaign'.
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
              FestiveAI will generate and validate artwork {leadDays} days in advance of the festival date.
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
