import React, { useState } from 'react';
import {
  Share2,
  CheckCircle,
  AlertCircle,
  Plus,
  RefreshCw,
  Sparkles,
  Trash2,
  ExternalLink,
  ShieldAlert,
  BookOpen,
  UserCheck,
  Eye,
  Layers,
  X
} from 'lucide-react';
import { SocialAccount, HistoricalPost } from '../types';
import { api } from '../services/api';

interface ConnectedAccountsProps {
  accounts: SocialAccount[];
  onRefresh: () => void;
  onSelectAccount: (id: string) => void;
}

export const ConnectedAccounts: React.FC<ConnectedAccountsProps> = ({
  accounts,
  onRefresh,
  onSelectAccount
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [platform, setPlatform] = useState<'instagram' | 'linkedin'>('instagram');
  const [brandName, setBrandName] = useState('TechPulse Innovations');
  const [username, setUsername] = useState('techpulse_official');
  const [isLoading, setIsLoading] = useState(false);
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  // Historical Posts & Pillar Inspection Modal State
  const [inspectModalOpen, setInspectModalOpen] = useState(false);
  const [inspectAccount, setInspectAccount] = useState<SocialAccount | null>(null);
  const [inspectPosts, setInspectPosts] = useState<HistoricalPost[]>([]);
  const [isLoadingPosts, setIsLoadingPosts] = useState(false);

  const handleOpenInspect = async (acc: SocialAccount) => {
    setInspectAccount(acc);
    setInspectModalOpen(true);
    setIsLoadingPosts(true);
    try {
      const posts = await api.getHistoricalPosts(acc.id);
      setInspectPosts(posts || []);
    } catch (e) {
      console.error('Failed to load historical posts', e);
    } finally {
      setIsLoadingPosts(false);
    }
  };

  const handleConnectMock = async () => {
    setIsLoading(true);
    try {
      const newAcc = await api.connectMockAccount({
        platform,
        account_username: username,
        display_name: brandName,
        brand_name: brandName
      });
      if (newAcc) {
        setIsModalOpen(false);
        setActionNotice(`Connected @${newAcc.account_username} with historical festival posts!`);
        onRefresh();
        onSelectAccount(newAcc.id);
        setTimeout(() => setActionNotice(null), 5000);
      }
    } catch (e: any) {
      alert('Error connecting account: ' + (e?.message || 'Check network'));
    } finally {
      setIsLoading(false);
    }
  };

  const handleDisconnect = async (id: string) => {
    if (!confirm('Are you sure you want to disconnect this account? Scheduled campaigns will be paused.')) return;
    try {
      await api.disconnectAccount(id);
      onRefresh();
    } catch (e: any) {
      alert('Failed to disconnect: ' + (e?.message || 'Error'));
    }
  };

  const handleAnalyze = async (id: string) => {
    setIsLoading(true);
    try {
      await api.triggerAccountAnalysis(id);
      setActionNotice('AI historical analysis completed! Style profile updated.');
      onRefresh();
      setTimeout(() => setActionNotice(null), 4000);
    } catch (e: any) {
      alert('Analysis error: ' + (e?.message || 'Error'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Connected Social Accounts</h1>
          <p className="text-sm text-slate-400">
            Manage authorized Instagram Business & LinkedIn accounts, permissions, and historical data synchronization.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2.5 rounded-xl text-sm font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-md shadow-amber-500/20 transition-all flex items-center space-x-2 shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>Connect Account</span>
        </button>
      </div>

      {actionNotice && (
        <div className="p-4 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-sm flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 shrink-0" />
          <span>{actionNotice}</span>
        </div>
      )}

      {/* Account Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {accounts.map((acc) => (
          <div
            key={acc.id}
            className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5 hover:border-slate-700 transition-all"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3.5">
                <div
                  className={`w-12 h-12 rounded-xl flex items-center justify-center text-white text-xl font-bold shadow-md ${
                    acc.platform === 'instagram'
                      ? 'bg-gradient-to-tr from-amber-500 via-rose-500 to-purple-600'
                      : 'bg-gradient-to-tr from-sky-600 to-blue-700'
                  }`}
                >
                  {acc.platform === 'instagram' ? 'IG' : 'IN'}
                </div>
                <div>
                  <h3 className="text-base font-bold text-white flex items-center space-x-2">
                    <span>{acc.display_name || acc.account_username}</span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-normal">
                      @{acc.account_username}
                    </span>
                  </h3>
                  <p className="text-xs text-slate-400 capitalize">
                    {acc.platform} • {acc.account_type} Account
                  </p>
                </div>
              </div>

              <span
                className={`text-xs px-2.5 py-1 rounded-full font-semibold ${
                  acc.status === 'active'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                }`}
              >
                {acc.status.toUpperCase()}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 py-2 border-y border-slate-800/80 text-xs">
              <div>
                <span className="text-slate-400 block">Historical Posts Synced</span>
                <span className="font-bold text-slate-200 text-sm">{acc.historical_posts_count} Posts</span>
              </div>
              <div>
                <span className="text-slate-400 block">Brand Profile Status</span>
                <span className="font-bold text-emerald-400 text-sm">
                  {acc.has_style_profile ? 'Extracted & Calibrated' : 'Pending Analysis'}
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between pt-1">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleAnalyze(acc.id)}
                  disabled={isLoading}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center space-x-1.5"
                >
                  <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                  <span>Re-Analyze</span>
                </button>

                <button
                  onClick={() => handleOpenInspect(acc)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 flex items-center space-x-1.5"
                >
                  <Layers className="w-3.5 h-3.5" />
                  <span>Post Types & History</span>
                </button>
              </div>

              <button
                onClick={() => handleDisconnect(acc.id)}
                className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-950/30 transition-all"
                title="Disconnect Account"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Inspect Historical Posts & Post Types Modal */}
      {inspectModalOpen && inspectAccount && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-4xl p-6 space-y-5 shadow-2xl max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                  <UserCheck className="w-5 h-5 text-indigo-400" />
                  <span>Analyzed Post Types & Historical Archive</span>
                </h3>
                <p className="text-xs text-slate-400">
                  Showing historical posts and detected content pillars for @{inspectAccount.account_username}
                </p>
              </div>
              <button
                onClick={() => setInspectModalOpen(false)}
                className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="overflow-y-auto space-y-3 pr-1 flex-1">
              {isLoadingPosts ? (
                <div className="text-center py-12 text-slate-400 text-sm">Loading historical posts...</div>
              ) : inspectPosts.length === 0 ? (
                <div className="text-center py-12 text-slate-400 text-sm">No historical posts found for this account.</div>
              ) : (
                inspectPosts.map((post) => (
                  <div
                    key={post.id}
                    className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 flex flex-col md:flex-row gap-4 items-start"
                  >
                    {post.media_url && (
                      <div className="w-20 h-20 rounded-lg overflow-hidden bg-slate-900 shrink-0 border border-slate-700">
                        <img src={post.media_url} alt="Post media" className="w-full h-full object-cover" />
                      </div>
                    )}
                    <div className="space-y-1.5 flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase tracking-wider">
                          {(post.post_pillar || 'thought_leadership').replace('_', ' ')}
                        </span>
                        {post.post_archetype && (
                          <span className="text-[11px] font-medium text-slate-300">
                            • {post.post_archetype}
                          </span>
                        )}
                        {post.is_festival_greeting && (
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                            {post.detected_festival?.toUpperCase() || 'FESTIVAL'} ({(post.festival_confidence * 100).toFixed(0)}%)
                          </span>
                        )}
                        <span className="text-[11px] text-slate-500 ml-auto font-mono">
                          {new Date(post.published_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-xs text-slate-200 line-clamp-3 leading-relaxed">
                        {post.caption}
                      </p>
                      {post.hashtags && post.hashtags.length > 0 && (
                        <div className="flex flex-wrap gap-1 pt-1">
                          {post.hashtags.slice(0, 5).map((ht, idx) => (
                            <span key={idx} className="text-[10px] text-amber-400 font-mono">
                              {ht}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="flex justify-end pt-2 border-t border-slate-800">
              <button
                onClick={() => setInspectModalOpen(false)}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-200 hover:bg-slate-700"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Connect Account Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 space-y-5 shadow-2xl">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-white">Connect Social Media Account</h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-400">
              Connect an official Meta Instagram or LinkedIn account. You can also connect an instant Sandbox/Mock account to test historical ingestion and AI creative generation without waiting for Meta App Review.
            </p>

            <div className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1.5">Social Media Platform</label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setPlatform('instagram')}
                    className={`py-2 px-3 rounded-xl text-xs font-bold border transition-all ${
                      platform === 'instagram'
                        ? 'bg-rose-500/20 border-rose-500 text-rose-300'
                        : 'bg-slate-800/40 border-slate-700 text-slate-400'
                    }`}
                  >
                    📷 Instagram Business
                  </button>
                  <button
                    type="button"
                    onClick={() => setPlatform('linkedin')}
                    className={`py-2 px-3 rounded-xl text-xs font-bold border transition-all ${
                      platform === 'linkedin'
                        ? 'bg-sky-500/20 border-sky-500 text-sky-300'
                        : 'bg-slate-800/40 border-slate-700 text-slate-400'
                    }`}
                  >
                    💼 LinkedIn Page / Profile
                  </button>
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Brand / Company Name</label>
                <input
                  type="text"
                  value={brandName}
                  onChange={(e) => setBrandName(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
                  placeholder="e.g. TechPulse Global"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Account Handle / Username</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
                  placeholder="e.g. techpulse_official"
                />
              </div>

              <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-xs text-amber-300 space-y-1">
                <span className="font-bold flex items-center space-x-1">
                  <span>⚡ Instant Sandbox Ingestion</span>
                </span>
                <p className="text-[11px] text-amber-200/80">
                  Will automatically seed multi-year sample posts for Diwali, Holi, and New Year, train the writing style, and calibrate your color palette.
                </p>
              </div>
            </div>

            <div className="flex items-center justify-end space-x-3 pt-2">
              <button
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleConnectMock}
                disabled={isLoading}
                className="px-5 py-2 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-md shadow-amber-500/20"
              >
                {isLoading ? 'Connecting...' : 'Connect & Ingest Data'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
