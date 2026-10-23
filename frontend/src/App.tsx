import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar, TabType } from './components/Sidebar';
import { Overview } from './pages/Overview';
import { ConnectedAccounts } from './pages/ConnectedAccounts';
import { StyleProfilePage } from './pages/StyleProfile';
import { FestivalCalendarPage } from './pages/FestivalCalendar';
import { ContentStudio } from './pages/ContentStudio';
import { AutomationSettingsPage } from './pages/AutomationSettings';
import { PublishingHistoryPage } from './pages/PublishingHistory';
import { SocialAccount, UpcomingFestival, DashboardAnalytics, PublishingCampaign } from './types';
import { api } from './services/api';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<TabType>('overview');
  const [accounts, setAccounts] = useState<SocialAccount[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState<string | null>(null);
  const [upcomingFestivals, setUpcomingFestivals] = useState<UpcomingFestival[]>([]);
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [recentCampaigns, setRecentCampaigns] = useState<PublishingCampaign[]>([]);
  const [studioTargetFestival, setStudioTargetFestival] = useState<{ slug: string; year: number } | undefined>(undefined);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const loadData = async () => {
    try {
      const [accs, anl, fests] = await Promise.all([
        api.getAccounts(),
        api.getAnalytics(),
        api.getUpcomingFestivals(undefined, 180)
      ]);
      setAccounts(accs);
      setAnalytics(anl);
      setUpcomingFestivals(fests);

      if (accs.length > 0 && !selectedAccountId) {
        setSelectedAccountId(accs[0].id);
      }

      const camps = await api.getCampaigns();
      setRecentCampaigns(camps);
    } catch (e) {
      console.error('Error loading initial FestiveAI data:', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const selectedAccount = accounts.find((a) => a.id === selectedAccountId) || accounts[0] || null;
  const pendingApprovals = recentCampaigns.filter((c) => c.status === 'generated' && !c.is_approved).length;

  const handleSelectFestivalForStudio = (slug: string, year: number) => {
    setStudioTargetFestival({ slug, year });
    setCurrentTab('studio');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar
        accounts={accounts}
        selectedAccountId={selectedAccountId}
        onSelectAccount={(id) => setSelectedAccountId(id)}
        onRefreshData={loadData}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          currentTab={currentTab}
          onTabChange={(tab) => setCurrentTab(tab)}
          pendingApprovalsCount={pendingApprovals}
        />

        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-gradient-to-b from-slate-950 via-slate-900/30 to-slate-950">
          {isLoading ? (
            <div className="h-full flex items-center justify-center space-x-3 text-slate-400">
              <div className="w-5 h-5 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
              <span>Connecting to FestiveAI Engine...</span>
            </div>
          ) : (
            <>
              {currentTab === 'overview' && (
                <Overview
                  analytics={analytics}
                  upcomingFestivals={upcomingFestivals}
                  recentCampaigns={recentCampaigns}
                  accounts={accounts}
                  onNavigate={(tab) => setCurrentTab(tab)}
                />
              )}

              {currentTab === 'accounts' && (
                <ConnectedAccounts
                  accounts={accounts}
                  onRefresh={loadData}
                  onSelectAccount={(id) => setSelectedAccountId(id)}
                />
              )}

              {currentTab === 'profile' && (
                <StyleProfilePage
                  selectedAccount={selectedAccount}
                  onRefresh={loadData}
                />
              )}

              {currentTab === 'calendar' && (
                <FestivalCalendarPage
                  upcomingFestivals={upcomingFestivals}
                  selectedAccount={selectedAccount}
                  onRefresh={loadData}
                  onNavigate={(tab) => setCurrentTab(tab)}
                  onSelectFestivalForStudio={handleSelectFestivalForStudio}
                />
              )}

              {currentTab === 'studio' && (
                <ContentStudio
                  selectedAccount={selectedAccount}
                  upcomingFestivals={upcomingFestivals}
                  targetFestivalSlug={studioTargetFestival?.slug}
                  targetFestivalYear={studioTargetFestival?.year}
                  onRefresh={loadData}
                />
              )}

              {currentTab === 'automation' && (
                <AutomationSettingsPage
                  selectedAccount={selectedAccount}
                  onRefresh={loadData}
                />
              )}

              {currentTab === 'history' && (
                <PublishingHistoryPage
                  selectedAccount={selectedAccount}
                  onRefresh={loadData}
                />
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
