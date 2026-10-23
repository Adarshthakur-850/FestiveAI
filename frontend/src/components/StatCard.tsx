import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtext?: string;
  icon: LucideIcon;
  color?: 'amber' | 'emerald' | 'blue' | 'purple' | 'rose';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtext,
  icon: Icon,
  color = 'amber'
}) => {
  const colorMap = {
    amber: 'from-amber-500/20 to-amber-600/5 text-amber-400 border-amber-500/30',
    emerald: 'from-emerald-500/20 to-emerald-600/5 text-emerald-400 border-emerald-500/30',
    blue: 'from-sky-500/20 to-sky-600/5 text-sky-400 border-sky-500/30',
    purple: 'from-purple-500/20 to-purple-600/5 text-purple-400 border-purple-500/30',
    rose: 'from-rose-500/20 to-rose-600/5 text-rose-400 border-rose-500/30',
  };

  return (
    <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 shadow-sm hover:border-slate-700/80 transition-all">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        <div className={`w-9 h-9 rounded-xl bg-gradient-to-br border flex items-center justify-center ${colorMap[color]}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="mt-3">
        <span className="text-2xl font-black tracking-tight text-white">{value}</span>
        {subtext && <p className="text-xs text-slate-400 mt-1">{subtext}</p>}
      </div>
    </div>
  );
};
