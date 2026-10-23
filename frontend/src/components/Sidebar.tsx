import React from 'react';
import {
  LayoutDashboard,
  Share2,
  Palette,
  CalendarDays,
  Sparkles,
  Sliders,
  History,
  ShieldCheck
} from 'lucide-react';

export type TabType =
  | 'overview'
  | 'accounts'
  | 'profile'
  | 'calendar'
  | 'studio'
  | 'automation'
  | 'history';

interface SidebarProps {
  currentTab: TabType;
  onTabChange: (tab: TabType) => void;
  pendingApprovalsCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onTabChange,
  pendingApprovalsCount = 0
}) => {
  const menuItems = [
    { id: 'overview', label: 'Command Overview', icon: LayoutDashboard },
    { id: 'accounts', label: 'Connected Accounts', icon: Share2 },
    { id: 'profile', label: 'Brand & Style Profile', icon: Palette },
    { id: 'calendar', label: 'Festival Calendar', icon: CalendarDays },
    { id: 'studio', label: 'Content Studio', icon: Sparkles, badge: pendingApprovalsCount > 0 ? pendingApprovalsCount : undefined },
    { id: 'automation', label: 'Automation Rules', icon: Sliders },
    { id: 'history', label: 'Publishing History', icon: History },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-900/40 p-4 flex flex-col justify-between shrink-0">
      <div className="space-y-1">
        <p className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-2">
          Platform Navigation
        </p>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id as TabType)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                isActive
                  ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-amber-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && (
                <span className="bg-amber-500 text-slate-950 font-bold text-xs px-2 py-0.5 rounded-full">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      <div className="p-3 bg-slate-800/40 border border-slate-800 rounded-xl space-y-2">
        <div className="flex items-center space-x-2 text-xs text-emerald-400">
          <ShieldCheck className="w-4 h-4" />
          <span className="font-semibold">Enterprise Safe</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          Zero Duplicate Posting constraints active. Multi-tenant token encryption enabled.
        </p>
      </div>
    </aside>
  );
};
