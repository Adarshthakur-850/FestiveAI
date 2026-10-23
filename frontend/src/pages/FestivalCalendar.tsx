import React, { useState } from 'react';
import {
  CalendarDays,
  Sparkles,
  CheckCircle,
  ShieldCheck,
  Search,
  Filter,
  ArrowRight
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

  const filtered = (upcomingFestivals || []).filter((f) => {
    const matchName = (f.name || '').toLowerCase().includes(searchTerm.toLowerCase()) || (f.slug || '').includes(searchTerm.toLowerCase());
    const matchCat = filterCategory === 'all' || f.category === filterCategory;
    return matchName && matchCat;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight">Intelligent Festival Calendar</h1>
          <p className="text-sm text-slate-400">
            Astronomically calculated lunar, solar, and Gregorian dates with multi-signal brand relevance scoring.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search festivals..."
              className="bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500 w-48 sm:w-64"
            />
          </div>

          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none"
          >
            <option value="all">All Categories</option>
            <option value="cultural">Cultural</option>
            <option value="religious">Religious</option>
            <option value="national">National Days</option>
          </select>
        </div>
      </div>

      {notice && (
        <div className="p-4 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-sm flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 shrink-0" />
          <span>{notice}</span>
        </div>
      )}

      {/* Festival Observances Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.map((fest) => {
          const festDate = new Date(fest.observed_date);
          const isHighRelevance = fest.relevance_score >= 0.70;

          return (
            <div
              key={fest.festival_id}
              className={`bg-slate-900/60 border rounded-2xl p-5 space-y-4 transition-all relative overflow-hidden ${
                fest.is_enabled ? 'border-slate-800 hover:border-slate-700' : 'border-slate-800/40 opacity-60'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex flex-col items-center justify-center text-amber-400">
                    <span className="text-[10px] uppercase font-bold">
                      {festDate.toLocaleString('default', { month: 'short' })}
                    </span>
                    <span className="text-base font-black leading-none">{festDate.getDate()}</span>
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white leading-snug">{fest.name}</h3>
                    <span className="text-[11px] text-slate-400 block capitalize">
                      {fest.category} • {festDate.getFullYear()}
                    </span>
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
                  <span className="font-semibold text-slate-200">{fest.days_until} days until observance</span>
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
                    <span>Ephemeris Verified</span>
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
    </div>
  );
};
