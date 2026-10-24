import React, { useState } from 'react';
import { Sparkles, Play, CheckCircle, RefreshCw, Bell, Menu, X } from 'lucide-react';
import { api } from '../services/api';
import { SocialAccount } from '../types';

interface NavbarProps {
  accounts: SocialAccount[];
  selectedAccountId: string | null;
  onSelectAccount: (id: string) => void;
  onRefreshData: () => void;
  isMobileMenuOpen?: boolean;
  onToggleMobileMenu?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  accounts,
  selectedAccountId,
  onSelectAccount,
  onRefreshData,
  isMobileMenuOpen,
  onToggleMobileMenu
}) => {
  const [isRunningCycle, setIsRunningCycle] = useState(false);
  const [cycleNotice, setCycleNotice] = useState<string | null>(null);

  const handleRunCycle = async () => {
    setIsRunningCycle(true);
    try {
      const summary = await api.triggerAutonomousCycle();
      setCycleNotice(`Cycle complete: ${summary.campaigns_generated} generated, ${summary.campaigns_published} published.`);
      onRefreshData();
      setTimeout(() => setCycleNotice(null), 5000);
    } catch (e: any) {
      setCycleNotice('Error running cycle: ' + (e?.message || 'Network error'));
      setTimeout(() => setCycleNotice(null), 5000);
    } finally {
      setIsRunningCycle(false);
    }
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/90 backdrop-blur-md px-3 sm:px-6 flex items-center justify-between sticky top-0 z-40">
      <div className="flex items-center space-x-2 sm:space-x-3">
        {/* Mobile Hamburger Menu Toggle */}
        <button
          onClick={onToggleMobileMenu}
          aria-label={isMobileMenuOpen ? 'Close Menu' : 'Open Menu'}
          className="md:hidden p-2 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
        >
          {isMobileMenuOpen ? (
            <X className="w-5 h-5 text-amber-400" />
          ) : (
            <Menu className="w-5 h-5" />
          )}
        </button>

        <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-rose-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-amber-500/20 shrink-0">
          <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-white animate-pulse" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-extrabold text-base sm:text-lg tracking-tight bg-gradient-to-r from-amber-400 via-rose-300 to-indigo-300 bg-clip-text text-transparent">
              FestiveAI
            </span>
            <span className="text-[9px] sm:text-[10px] uppercase font-bold tracking-wider px-1.5 sm:px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hidden xs:inline-block">
              Autonomous
            </span>
          </div>
          <p className="text-[11px] text-slate-400 hidden lg:block">AI Social Profile Learning & Festival Publishing Engine</p>
        </div>
      </div>

      <div className="flex items-center space-x-2 sm:space-x-4">
        {/* Account Selector */}
        {accounts.length > 0 && (
          <div className="flex items-center space-x-1.5 sm:space-x-2 bg-slate-800/80 rounded-lg px-2 sm:px-3 py-1.5 border border-slate-700/60 max-w-[140px] sm:max-w-none">
            <span className="text-[11px] sm:text-xs text-slate-400 hidden sm:inline">Account:</span>
            <select
              value={selectedAccountId || ''}
              onChange={(e) => onSelectAccount(e.target.value)}
              className="bg-transparent text-xs sm:text-sm text-slate-200 font-medium focus:outline-none cursor-pointer truncate max-w-[120px] sm:max-w-none"
            >
              {accounts.map((acc) => (
                <option key={acc.id} value={acc.id} className="bg-slate-900 text-slate-200">
                  {acc.platform === 'instagram' ? '📷' : '💼'} @{acc.account_username}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Manual Trigger Button */}
        <button
          onClick={handleRunCycle}
          disabled={isRunningCycle}
          title="Trigger Autonomous Pipeline Cycle"
          className="flex items-center space-x-1.5 sm:space-x-2 px-2.5 sm:px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 shadow-md shadow-amber-500/20 transition-all disabled:opacity-50 shrink-0"
        >
          {isRunningCycle ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              <span className="hidden sm:inline">Running Cycle...</span>
              <span className="sm:hidden">Running...</span>
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-current" />
              <span className="hidden sm:inline">Trigger Pipeline</span>
              <span className="sm:hidden">Run</span>
            </>
          )}
        </button>

        {cycleNotice && (
          <div className="hidden xl:flex items-center space-x-1.5 text-xs text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-3 py-1 rounded-full animate-fade-in">
            <CheckCircle className="w-3.5 h-3.5" />
            <span>{cycleNotice}</span>
          </div>
        )}
      </div>
    </header>
  );
};
