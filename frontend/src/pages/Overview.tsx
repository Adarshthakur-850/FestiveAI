import React from 'react';
import {
  Share2,
  Calendar,
  Sparkles,
  Send,
  Sliders,
  CheckCircle2,
  Clock,
  ArrowRight,
  TrendingUp,
  AlertTriangle
} from 'lucide-react';
import { StatCard } from '../components/StatCard';
import { DashboardAnalytics, UpcomingFestival, PublishingCampaign, SocialAccount } from '../types';
import { TabType } from '../components/Sidebar';

interface OverviewProps {
  analytics: DashboardAnalytics | null;
  upcomingFestivals: UpcomingFestival[];
  recentCampaigns: PublishingCampaign[];
  accounts: SocialAccount[];
  onNavigate: (tab: TabType) => void;
}

export const Overview: React.FC<OverviewProps> = ({
  analytics,
  upcomingFestivals,
  recentCampaigns,
  accounts,
  onNavigate
}) => {
  const nextFestival = upcomingFestivals.length > 0 ? upcomingFestivals[0] : null;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero Countdown Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-amber-600/30 via-rose-600/20 to-indigo-900/40 border border-amber-500/30 p-8 shadow-xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-300 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Next Astronomical Festival Approaching</span>
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              {nextFestival ? nextFestival.name : 'All Festival Cycles Synced'}
            </h1>
            <p className="text-sm text-slate-300 max-w-xl">
              {nextFestival ? (
                <>
                  Observed on <span className="font-semibold text-amber-300">{nextFestival.observed_date}</span> (in {nextFestival.days_until} days).
                  Verified by {nextFestival.verification_source}.
                  Relevance score for connected accounts is <span className="font-semibold text-emerald-400">{(nextFestival.relevance_score * 100).toFixed(0)}%</span>.
                </>
              ) : (
                'The calendar engine is tracking astronomical cycles for Diwali, Eid, Holi, Christmas, and regional occasions.'
              )}
            </p>
          </div>

          <div className="flex items-center space-x-3 shrink-0">
            <button
              onClick={() => onNavigate('studio')}
              className="px-5 py-2.5 rounded-xl text-sm font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-lg shadow-amber-500/30 transition-all flex items-center space-x-2"
            >
              <span>Open Content Studio</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => onNavigate('calendar')}
              className="px-4 py-2.5 rounded-xl text-sm font-medium bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 border border-slate-700 transition-all"
            >
              View Calendar
            </button>
          </div>
        </div>
      </div>

      {/* KPI Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Connected Accounts"
          value={analytics?.connected_accounts ?? 0}
          subtext={`${analytics?.total_accounts ?? 0} Total registered`}
          icon={Share2}
          color="blue"
        />
        <StatCard
          title="Upcoming (30 Days)"
          value={analytics?.upcoming_festivals_30d ?? 0}
          subtext="Astronomical observances"
          icon={Calendar}
          color="amber"
        />
        <StatCard
          title="Creatives Ready"
          value={analytics?.posts_generated ?? 0}
          subtext={`${analytics?.posts_scheduled ?? 0} Scheduled to publish`}
          icon={Sparkles}
          color="purple"
        />
        <StatCard
          title="Autonomous Mode"
          value={analytics?.autonomous_mode_enabled_count ?? 0}
          subtext="Accounts hands-off active"
          icon={Sliders}
          color="emerald"
        />
      </div>

      {/* Two Column Layout: Upcoming Pipeline & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upcoming Festivals List */}
        <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-base font-bold text-white">Upcoming Festival Pipeline</h2>
              <p className="text-xs text-slate-400">Calculated according to Hindu Lunisolar & Islamic Hijri Ephemeris</p>
            </div>
            <button
              onClick={() => onNavigate('calendar')}
              className="text-xs font-semibold text-amber-400 hover:text-amber-300 flex items-center space-x-1"
            >
              <span>Explore all</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3">
            {(upcomingFestivals || []).slice(0, 4).map((f) => (
              <div
                key={f.festival_id}
                className="flex items-center justify-between p-3.5 rounded-xl bg-slate-800/40 border border-slate-800 hover:border-slate-700 transition-all"
              >
                <div className="flex items-center space-x-3.5">
                  <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex flex-col items-center justify-center text-amber-400">
                    <span className="text-[10px] uppercase font-bold">{new Date(f.observed_date).toLocaleString('default', { month: 'short' })}</span>
                    <span className="text-sm font-black leading-none">{new Date(f.observed_date).getDate()}</span>
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-100">{f.name}</h3>
                    <div className="flex items-center space-x-2 text-xs text-slate-400">
                      <span>In {f.days_until} days</span>
                      <span>•</span>
                      <span className="text-emerald-400 font-medium">{(f.relevance_score * 100).toFixed(0)}% relevant</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <span
                    className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                      f.status === 'published'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : f.status === 'scheduled'
                        ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                        : f.status === 'generated'
                        ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        : 'bg-slate-700/40 text-slate-400'
                    }`}
                  >
                    {f.status.toUpperCase()}
                  </span>
                  <button
                    onClick={() => onNavigate('studio')}
                    className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300"
                    title="View Creative in Studio"
                  >
                    <Sparkles className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Account Status Quick Card */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <h2 className="text-base font-bold text-white mb-1">Active Accounts</h2>
            <p className="text-xs text-slate-400 mb-4">Learned brand identity & token readiness</p>

            {accounts.length === 0 ? (
              <div className="text-center py-8 space-y-3">
                <p className="text-sm text-slate-400">No social accounts connected yet.</p>
                <button
                  onClick={() => onNavigate('accounts')}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-amber-500 text-slate-950"
                >
                  Connect Account
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {accounts.map((acc) => (
                  <div key={acc.id} className="p-3 bg-slate-800/40 border border-slate-800 rounded-xl space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-bold text-slate-200">@{acc.account_username}</span>
                      <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {acc.status}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs text-slate-400">
                      <span>{acc.historical_posts_count} posts analyzed</span>
                      <span className="text-amber-400 capitalize">{acc.automation_mode || 'Approval'} mode</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-slate-800 mt-4">
            <button
              onClick={() => onNavigate('profile')}
              className="w-full py-2.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all flex items-center justify-center space-x-2"
            >
              <span>Calibrate Style Profile</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
