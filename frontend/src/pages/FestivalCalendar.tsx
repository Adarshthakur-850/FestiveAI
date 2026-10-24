import React, { useState } from 'react';
import {
  CalendarDays,
  Sparkles,
  CheckCircle,
  ShieldCheck,
  Search,
  Filter,
  ArrowRight,
  Zap,
  Plus,
  X,
  Send,
  Radio
} from 'lucide-react';
import { UpcomingFestival, SocialAccount } from '../types';
import { api } from '../services/api';
import { TabType } from '../components/Sidebar';

interface FestivalCalendarProps {
  upcomingFestivals: UpcomingFestival[];
  selectedAccount: SocialAccount | null;
  onRefresh: () => void;
  onNavigate: (tab: TabType) => void;
  onSelectFestivalForStudio: (slug: string, year: number) => void;
}

export const FestivalCalendarPage: React.FC<FestivalCalendarProps> = ({
  upcomingFestivals,
  selectedAccount,
  onRefresh,
  onNavigate,
  onSelectFestivalForStudio
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  // Custom Event Creation Modal & Test Trigger States
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isQuickTesting, setIsQuickTesting] = useState(false);
  const [isCreatingCustom, setIsCreatingCustom] = useState(false);

  const [customName, setCustomName] = useState('');
  const [customCategory, setCustomCategory] = useState('milestone');
  const [customDate, setCustomDate] = useState(new Date().toISOString().split('T')[0]);
  const [customGreeting, setCustomGreeting] = useState('');
  const [autoPublish, setAutoPublish] = useState(true);

  const handleToggleEnable = async (fest: UpcomingFestival) => {
    if (!selectedAccount) return;
    try {
      await api.updateFestivalPreference(selectedAccount.id, fest.festival_id, {
        is_enabled: !fest.is_enabled
      });
      onRefresh();
    } catch (e: any) {
      alert('Error updating preference: ' + e?.message);
    }
  };

  const handleQuickRandomEvent = async () => {
    setIsQuickTesting(true);
    setNotice('Generating random celebration event, synthesizing branded artwork & posting directly to social account...');
    try {
      const res = await api.createRandomTestEvent({
        social_account_id: selectedAccount?.id,
        auto_publish_now: true
      });
      setNotice(res.message);
      onRefresh();
      setTimeout(() => setNotice(null), 8000);
    } catch (e: any) {
      alert('Error triggering random test event: ' + (e?.message || 'Error'));
      setNotice(null);
    } finally {
      setIsQuickTesting(false);
    }
  };

  const handleCreateCustomEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customName.trim()) {
      alert('Please enter an event name');
      return;
    }
    setIsCreatingCustom(true);
    try {
      const res = await api.createCustomEvent({
        name: customName.trim(),
        category: customCategory,
        observed_date: customDate,
        default_greeting_phrases: customGreeting ? [customGreeting] : undefined,
        social_account_id: selectedAccount?.id,
        auto_publish_now: autoPublish
      });
      setIsModalOpen(false);
      setCustomName('');
      setCustomGreeting('');
      setNotice(res.message);
      onRefresh();
      setTimeout(() => setNotice(null), 8000);
    } catch (e: any) {
      alert('Error creating custom event: ' + (e?.message || 'Error'));
    } finally {
      setIsCreatingCustom(false);
    }
  };

  const filtered = (upcomingFestivals || []).filter((f) => {
    const matchName = (f.name || '').toLowerCase().includes(searchTerm.toLowerCase()) || (f.slug || '').includes(searchTerm.toLowerCase());
    const matchCat = filterCategory === 'all' || f.category === filterCategory;
    return matchName && matchCat;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Header & Action Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-black text-white tracking-tight">Intelligent Festival & Event Calendar</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
              Autonomous Sync
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Astronomically calculated lunisolar dates, Gregorian holidays, and custom host-created celebration events.
          </p>
        </div>

        {/* Custom Event & Test Triggers */}
        <div className="flex flex-wrap items-center gap-2.5 shrink-0">
          <button
            onClick={handleQuickRandomEvent}
            disabled={isQuickTesting}
            title="Automatically generates a random milestone event, synthesizes artwork, and publishes to your connected account"
            className="px-4 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-amber-500 via-rose-500 to-indigo-600 hover:from-amber-400 hover:to-indigo-500 text-white shadow-lg shadow-amber-500/20 transition-all flex items-center space-x-2 disabled:opacity-50"
          >
            <Zap className={`w-4 h-4 fill-current ${isQuickTesting ? 'animate-spin' : 'animate-pulse'}`} />
            <span>{isQuickTesting ? 'Publishing Test Event...' : '⚡ Quick Random Test Event'}</span>
          </button>

          <button
            onClick={() => setIsModalOpen(true)}
            className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all flex items-center space-x-1.5"
          >
            <Plus className="w-4 h-4 text-amber-400" />
            <span>Create Custom Event</span>
          </button>
        </div>
      </div>

      {notice && (
        <div className="p-4 rounded-xl bg-emerald-950/70 border border-emerald-700 text-emerald-200 text-xs sm:text-sm flex items-start sm:items-center space-x-2.5 shadow-lg animate-fade-in">
          <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5 sm:mt-0" />
          <span className="flex-1 font-medium">{notice}</span>
          <button onClick={() => setNotice(null)} className="text-emerald-400 hover:text-white p-1">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 bg-slate-900/60 p-3.5 rounded-2xl border border-slate-800/80">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search festivals or custom milestone events..."
            className="bg-slate-800/80 border border-slate-700 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500 w-full"
          />
        </div>

        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          className="bg-slate-800/80 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-slate-300 focus:outline-none w-full sm:w-auto font-medium"
        >
          <option value="all">All Categories</option>
          <option value="cultural">Cultural</option>
          <option value="religious">Religious</option>
          <option value="national">National Days</option>
          <option value="milestone">Milestones & Custom</option>
          <option value="corporate">Corporate & Tech</option>
        </select>
      </div>

      {/* Festival Observances Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.map((fest) => {
          const festDate = new Date(fest.observed_date);
          const isHighRelevance = fest.relevance_score >= 0.70;
          const isCustom = fest.category === 'milestone' || fest.slug.startsWith('custom_');

          return (
            <div
              key={fest.festival_id}
              className={`bg-slate-900/60 border rounded-2xl p-5 space-y-4 transition-all relative overflow-hidden ${
                isCustom
                  ? 'border-indigo-500/40 bg-gradient-to-br from-slate-900/90 via-indigo-950/20 to-slate-900/90 shadow-md'
                  : fest.is_enabled
                  ? 'border-slate-800 hover:border-slate-700'
                  : 'border-slate-800/40 opacity-60'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div
                    className={`w-12 h-12 rounded-xl flex flex-col items-center justify-center ${
                      isCustom
                        ? 'bg-indigo-500/15 border border-indigo-500/30 text-indigo-300'
                        : 'bg-amber-500/10 border border-amber-500/20 text-amber-400'
                    }`}
                  >
                    <span className="text-[10px] uppercase font-bold">
                      {festDate.toLocaleString('default', { month: 'short' })}
                    </span>
                    <span className="text-base font-black leading-none">{festDate.getDate()}</span>
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white leading-snug">{fest.name}</h3>
                    <div className="flex items-center space-x-1.5 mt-0.5">
                      <span className="text-[11px] text-slate-400 capitalize">
                        {fest.category} • {festDate.getFullYear()}
                      </span>
                      {isCustom && (
                        <span className="text-[9px] font-extrabold uppercase px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                          Host Event
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleToggleEnable(fest)}
                  className={`text-xs px-2.5 py-1 rounded-full font-semibold transition-all ${
                    fest.is_enabled
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : 'bg-slate-800 text-slate-500 border border-slate-700'
                  }`}
                >
                  {fest.is_enabled ? 'TRACKED' : 'MUTED'}
                </button>
              </div>

              <div className="space-y-1.5 text-xs border-y border-slate-800/80 py-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Countdown:</span>
                  <span className="font-semibold text-slate-200">
                    {fest.days_until <= 0 ? 'Observed Today' : `In ${fest.days_until} days`}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Account Relevance:</span>
                  <span className={`font-bold ${isHighRelevance ? 'text-amber-400' : 'text-slate-400'}`}>
                    {(fest.relevance_score * 100).toFixed(0)}% match
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Verification:</span>
                  <span className="text-[11px] text-slate-400 flex items-center space-x-1">
                    <ShieldCheck className="w-3 h-3 text-emerald-400" />
                    <span>{isCustom ? 'Host Verified' : 'Ephemeris Verified'}</span>
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-1">
                <span
                  className={`text-xs px-2 py-0.5 rounded font-medium ${
                    fest.status === 'published'
                      ? 'bg-emerald-500/10 text-emerald-400'
                      : fest.status === 'scheduled'
                      ? 'bg-sky-500/10 text-sky-400'
                      : fest.status === 'generated'
                      ? 'bg-amber-500/10 text-amber-400'
                      : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  Status: {fest.status.toUpperCase()}
                </span>

                <button
                  onClick={() => {
                    onSelectFestivalForStudio(fest.slug, festDate.getFullYear());
                    onNavigate('studio');
                  }}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/30 flex items-center space-x-1.5 transition-all"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Open Studio</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Create Custom Event Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-5 sm:p-6 space-y-5 shadow-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center space-x-2">
                  <Sparkles className="w-5 h-5 text-amber-400" />
                  <span>Create Custom Event / Milestone</span>
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Test the pipeline by adding a custom celebration to your calendar.
                </p>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateCustomEvent} className="space-y-4 text-xs">
              <div>
                <label className="font-semibold text-slate-300 block mb-1">Event / Milestone Name *</label>
                <input
                  type="text"
                  required
                  value={customName}
                  onChange={(e) => setCustomName(e.target.value)}
                  placeholder="e.g. Series A Funding Celebration, Global Developer Day"
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="font-semibold text-slate-300 block mb-1">Category</label>
                  <select
                    value={customCategory}
                    onChange={(e) => setCustomCategory(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  >
                    <option value="milestone">Company Milestone</option>
                    <option value="corporate">Tech & Corporate Day</option>
                    <option value="cultural">Cultural Celebration</option>
                    <option value="seasonal">Seasonal Occasion</option>
                  </select>
                </div>

                <div>
                  <label className="font-semibold text-slate-300 block mb-1">Observance Date</label>
                  <input
                    type="date"
                    value={customDate}
                    onChange={(e) => setCustomDate(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  />
                </div>
              </div>

              <div>
                <label className="font-semibold text-slate-300 block mb-1">Custom Headline / Greeting</label>
                <input
                  type="text"
                  value={customGreeting}
                  onChange={(e) => setCustomGreeting(e.target.value)}
                  placeholder="e.g. Celebrating Our Biggest Engineering Milestone Yet!"
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-amber-500"
                />
              </div>

              {/* Instant Auto-Publish Toggle */}
              <div className="p-3.5 bg-indigo-950/40 border border-indigo-500/30 rounded-xl space-y-2">
                <label className="flex items-center space-x-2.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={autoPublish}
                    onChange={(e) => setAutoPublish(e.target.checked)}
                    className="w-4 h-4 rounded text-amber-500 focus:ring-amber-500 bg-slate-800 border-slate-700 cursor-pointer"
                  />
                  <span className="font-bold text-white text-xs">
                    Synthesize Creative & Post Automatically
                  </span>
                </label>
                <p className="text-[11px] text-slate-400 pl-6 leading-relaxed">
                  {selectedAccount ? (
                    <>
                      Will immediately compose a pixel-perfect branded graphic with your logo and post to{' '}
                      <span className="font-bold text-indigo-300">@{selectedAccount.account_username}</span> ({selectedAccount.platform.toUpperCase()}).
                    </>
                  ) : (
                    'Select an account in the header to enable automatic instant posting.'
                  )}
                </p>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isCreatingCustom}
                  className="px-5 py-2.5 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-md shadow-amber-500/20 flex items-center space-x-1.5 disabled:opacity-50"
                >
                  {isCreatingCustom ? (
                    <span>Processing Event...</span>
                  ) : (
                    <>
                      <Send className="w-3.5 h-3.5" />
                      <span>{autoPublish ? 'Create & Post Immediately' : 'Save Event to Calendar'}</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
