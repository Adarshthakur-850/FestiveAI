import React, { useState, useEffect } from 'react';
import {
  History,
  CheckCircle,
  AlertTriangle,
  Clock,
  ExternalLink,
  RefreshCw,
  Search,
  ShieldCheck
} from 'lucide-react';
import { PublishingCampaign, SocialAccount } from '../types';
import { api } from '../services/api';

interface PublishingHistoryProps {
  selectedAccount: SocialAccount | null;
  onRefresh: () => void;
}

export const PublishingHistoryPage: React.FC<PublishingHistoryProps> = ({
  selectedAccount,
  onRefresh
}) => {
  const [campaigns, setCampaigns] = useState<PublishingCampaign[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    loadHistory();
  }, [selectedAccount]);

  const loadHistory = async () => {
    try {
      const data = await api.getCampaigns(selectedAccount?.id);
      setCampaigns(data);
    } catch (e) {
      console.error(e);
    }
  };

  const filtered = (campaigns || []).filter((c) => {
    const campId = c.campaign_identifier || '';
    const festName = c.festival_name || '';
    const username = c.account_username || '';
    const matchTerm =
      campId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      festName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      username.toLowerCase().includes(searchTerm.toLowerCase());
    const matchStatus = statusFilter === 'all' || c.status === statusFilter;
    return matchTerm && matchStatus;
  });

  return (
    <div className="space-y-6 max-w-6xl animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-white tracking-tight flex items-center space-x-2">
            <span>Publishing Audit Trail</span>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 font-bold">
              Idempotent Log
            </span>
          </h1>
          <p className="text-sm text-slate-400">
            Immutable log of publishing attempts, verified platform post IDs, and automated campaign lifecycles.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search campaigns..."
              className="bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500 w-48 sm:w-64"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none"
          >
            <option value="all">All Statuses</option>
            <option value="published">Published</option>
            <option value="scheduled">Scheduled</option>
            <option value="generated">Generated</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {/* Audit Table */}
      <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-800/50 text-slate-400 uppercase tracking-wider font-bold border-b border-slate-800 text-[11px]">
              <tr>
                <th className="py-3.5 px-4">Campaign Identifier</th>
                <th className="py-3.5 px-4">Platform / Account</th>
                <th className="py-3.5 px-4">Festival & Year</th>
                <th className="py-3.5 px-4">Target Publish Time</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4">Platform Post ID</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500">
                    No publishing campaigns found. Click 'Generate Creative' in Content Studio or trigger an AI cycle.
                  </td>
                </tr>
              ) : (
                filtered.map((c) => {
                  const latestAttempt = c.attempts.length > 0 ? c.attempts[0] : null;
                  const postId = latestAttempt?.platform_post_id;

                  return (
                    <tr key={c.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-3 px-4 font-mono font-medium text-slate-200">
                        {c.campaign_identifier}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2">
                          <span>{c.platform === 'instagram' ? '📷' : '💼'}</span>
                          <span className="font-semibold text-slate-200">@{c.account_username}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="font-bold text-white">{c.festival_name}</span>{' '}
                        <span className="text-slate-500">({c.year})</span>
                      </td>
                      <td className="py-3 px-4 text-slate-400">
                        {new Date(c.scheduled_publish_time).toLocaleString()}
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-2.5 py-1 rounded-full text-[11px] font-bold ${
                            c.status === 'published'
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                              : c.status === 'scheduled'
                              ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                              : c.status === 'generated'
                              ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                              : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                          }`}
                        >
                          {c.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-[11px]">
                        {postId ? (
                          <div className="flex items-center space-x-1.5 text-amber-400">
                            <span>{postId}</span>
                            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                          </div>
                        ) : (
                          <span className="text-slate-500 italic">None yet</span>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
