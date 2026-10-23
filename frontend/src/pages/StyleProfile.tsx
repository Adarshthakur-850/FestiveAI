import React, { useState, useEffect } from 'react';
import {
  Palette,
  CheckCircle,
  Sparkles,
  Sliders,
  Type,
  Layout,
  MessageSquare,
  Shield,
  Save,
  UserCheck,
  Compass,
  BarChart3,
  Target,
  Bookmark
} from 'lucide-react';
import { StyleProfile, SocialAccount } from '../types';
import { api } from '../services/api';

interface StyleProfileProps {
  selectedAccount: SocialAccount | null;
  onRefresh: () => void;
}

export const StyleProfilePage: React.FC<StyleProfileProps> = ({
  selectedAccount,
  onRefresh
}) => {
  const [profile, setProfile] = useState<StyleProfile | null>(null);
  const [dominantColors, setDominantColors] = useState<string[]>(['#1E3A8A', '#D97706', '#F59E0B']);
  const [secondaryColors, setSecondaryColors] = useState<string[]>(['#FFFFFF', '#0F172A']);
  const [formality, setFormality] = useState<number>(0.6);
  const [emojiFreq, setEmojiFreq] = useState<string>('moderate');
  const [typography, setTypography] = useState<string>('serif_classic');
  const [logoPlacement, setLogoPlacement] = useState<string>('top_right');
  const [brandName, setBrandName] = useState<string>('');
  const [signOff, setSignOff] = useState<string>('');
  const [languages, setLanguages] = useState<string[]>(['en', 'hi']);
  const [prohibited, setProhibited] = useState<string>('discount, sale, limited time');
  
  // Host Persona & Post Type Intelligence
  const [personaType, setPersonaType] = useState<string>('Tech Founder & Innovator');
  const [industryNiche, setIndustryNiche] = useState<string>('Technology & Software Engineering');
  const [targetAudience, setTargetAudience] = useState<string>('Developers, Founders, and Tech Decision-Makers');
  const [visualArchetype, setVisualArchetype] = useState<string>('tech_innovator');
  
  const [isLoading, setIsLoading] = useState(false);
  const [saveNotice, setSaveNotice] = useState<string | null>(null);

  useEffect(() => {
    if (selectedAccount) {
      loadProfile(selectedAccount.id);
    }
  }, [selectedAccount]);

  const loadProfile = async (accountId: string) => {
    try {
      const p = await api.getStyleProfile(accountId);
      setProfile(p);
      setDominantColors(p.dominant_colors || ['#1E3A8A', '#D97706', '#F59E0B']);
      setSecondaryColors(p.secondary_colors || ['#FFFFFF', '#0F172A']);
      setFormality(p.formality_score || 0.6);
      setEmojiFreq(p.emoji_frequency || 'moderate');
      setTypography(p.typography_style || 'serif_classic');
      setLogoPlacement(p.logo_placement || 'top_right');
      setBrandName(p.brand_name || selectedAccount?.display_name || '');
      setSignOff(p.required_sign_off || '');
      setLanguages(p.preferred_languages || ['en', 'hi']);
      setProhibited((p.prohibited_terms || []).join(', '));
      setPersonaType(p.persona_type || 'Tech Founder & Innovator');
      setIndustryNiche(p.industry_niche || 'Technology & Software Engineering');
      setTargetAudience(p.target_audience || 'Developers, Founders, and Tech Decision-Makers');
      setVisualArchetype(p.visual_archetype || 'tech_innovator');
    } catch (e) {
      console.error('Failed to load profile', e);
    }
  };

  const handleSave = async () => {
    if (!selectedAccount) return;
    setIsLoading(true);
    try {
      const prohibitedList = prohibited.split(',').map((s) => s.trim()).filter(Boolean);
      const updated = await api.updateStyleProfile(selectedAccount.id, {
        brand_name: brandName,
        dominant_colors: dominantColors,
        secondary_colors: secondaryColors,
        formality_score: formality,
        emoji_frequency: emojiFreq,
        typography_style: typography,
        logo_placement: logoPlacement,
        required_sign_off: signOff,
        preferred_languages: languages,
        prohibited_terms: prohibitedList,
        persona_type: personaType,
        industry_niche: industryNiche,
        target_audience: targetAudience,
        visual_archetype: visualArchetype
      });
      setProfile(updated);
      setSaveNotice('Brand & Host Persona Profile calibrated and saved to database!');
      onRefresh();
      setTimeout(() => setSaveNotice(null), 4000);
    } catch (e: any) {
      alert('Error updating profile: ' + (e?.message || 'Error'));
    } finally {
      setIsLoading(false);
    }
  };

  const toggleLanguage = (lang: string) => {
    if (languages.includes(lang)) {
      if (languages.length > 1) {
        setLanguages(languages.filter((l) => l !== lang));
      }
    } else {
      setLanguages([...languages, lang]);
    }
  };

  if (!selectedAccount) {
    return (
      <div className="p-12 text-center text-slate-400">
        Please select or connect an account from the header to view its style profile.
      </div>
    );
  }

  const contentPillars = profile?.content_pillars || {
    thought_leadership: 35,
    product_showcase: 25,
    behind_the_scenes: 15,
    educational: 15,
    festive_greeting: 10
  };

  const pillarColorMap: Record<string, string> = {
    thought_leadership: 'bg-indigo-500',
    product_showcase: 'bg-emerald-500',
    behind_the_scenes: 'bg-amber-500',
    educational: 'bg-sky-500',
    community_engagement: 'bg-purple-500',
    festive_greeting: 'bg-rose-500'
  };

  const pillarNameMap: Record<string, string> = {
    thought_leadership: 'Thought Leadership',
    product_showcase: 'Product Feature & Launches',
    behind_the_scenes: 'Behind the Scenes & Culture',
    educational: 'Tech Tips & Tutorials',
    community_engagement: 'Community Engagement',
    festive_greeting: 'Festivals & Occasions'
  };

  return (
    <div className="space-y-6 max-w-5xl animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-black text-white tracking-tight">Brand & Style Profile</h1>
            {profile && (
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
                Version {profile.version} • {(profile.confidence_score * 100).toFixed(0)}% Confidence
              </span>
            )}
          </div>
          <p className="text-sm text-slate-400">
            Learned from historical posts of <span className="font-semibold text-slate-200">@{selectedAccount.account_username}</span>.
            Calibrate brand rules, typography, and tone.
          </p>
        </div>

        <button
          onClick={handleSave}
          disabled={isLoading}
          className="px-5 py-2.5 rounded-xl text-sm font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-md shadow-amber-500/20 transition-all flex items-center space-x-2 shrink-0"
        >
          <Save className="w-4 h-4" />
          <span>{isLoading ? 'Saving...' : 'Save & Calibrate'}</span>
        </button>
      </div>

      {saveNotice && (
        <div className="p-4 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-sm flex items-center space-x-2">
          <CheckCircle className="w-4 h-4 shrink-0" />
          <span>{saveNotice}</span>
        </div>
      )}

      {/* Feature Add-on: Host Persona & Content Pillar Intelligence Card */}
      <div className="bg-gradient-to-br from-slate-900/90 via-indigo-950/30 to-slate-900/90 border border-indigo-500/30 rounded-2xl p-6 space-y-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
              <UserCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-lg font-bold text-white">Host Persona & Posting Habit Analysis</h2>
                <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  AI-Extracted
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Learned from historical posts of @{selectedAccount.account_username} to condition greetings and new posts to the host's specific voice.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400 font-medium">Visual Archetype:</span>
            <span className="text-xs font-bold px-2.5 py-1 rounded-lg bg-slate-800 text-amber-300 border border-slate-700 uppercase tracking-wider">
              {visualArchetype.replace('_', ' ')}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Persona Details & Form Inputs */}
          <div className="space-y-4">
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1.5 flex items-center space-x-1.5">
                <Compass className="w-3.5 h-3.5 text-indigo-400" />
                <span>Host Persona Archetype</span>
              </label>
              <select
                value={personaType}
                onChange={(e) => setPersonaType(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 font-medium focus:outline-none focus:border-indigo-500"
              >
                <option value="Tech Founder & Innovator">Tech Founder & Innovator (High-tech, Scaling, Systems)</option>
                <option value="Corporate B2B Leader">Corporate B2B Leader (Enterprise, Strategy, Partnerships)</option>
                <option value="Creative Designer & Studio">Creative Designer & Studio (Aesthetics, Typography, Visuals)</option>
                <option value="Wellness & Mindfulness Guide">Wellness & Mindfulness Guide (Balance, Health, Energy)</option>
                <option value="D2C Brand & Modern Merchant">D2C Brand & Modern Merchant (Product Craft, Customer Love)</option>
                <option value="Educator & Industry Mentor">Educator & Industry Mentor (Tutorials, Frameworks, Growth)</option>
              </select>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1.5">Industry Niche</label>
                <input
                  type="text"
                  value={industryNiche}
                  onChange={(e) => setIndustryNiche(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  placeholder="e.g. AI & Cloud Software"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1.5 flex items-center space-x-1">
                  <Target className="w-3 h-3 text-emerald-400" />
                  <span>Target Audience</span>
                </label>
                <input
                  type="text"
                  value={targetAudience}
                  onChange={(e) => setTargetAudience(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  placeholder="e.g. Developers & CTOs"
                />
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1.5">Visual Aesthetic Archetype</label>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {[
                  { id: 'tech_innovator', label: 'Tech Innovator', desc: 'Futuristic Dark Navy & Circuit Accents' },
                  { id: 'corporate_executive', label: 'Corporate B2B', desc: 'Refined Executive Gold & Deep Slate' },
                  { id: 'creative_studio', label: 'Creative Studio', desc: 'Vibrant Gradients & Artistic Accents' },
                  { id: 'warm_lifestyle', label: 'Warm Lifestyle', desc: 'Soft Earthy Glow & Organic Curves' }
                ].map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setVisualArchetype(item.id)}
                    className={`p-2 rounded-xl border text-left transition-all ${
                      visualArchetype === item.id
                        ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-sm'
                        : 'bg-slate-800/40 border-slate-700/60 text-slate-400 hover:border-slate-600'
                    }`}
                  >
                    <div className="font-bold text-xs">{item.label}</div>
                    <div className="text-[10px] text-slate-400 truncate mt-0.5">{item.desc}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right: Content Pillars Distribution & Signature Hooks */}
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
                  <BarChart3 className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Analyzed Content Pillars Distribution</span>
                </label>
                <span className="text-[11px] text-slate-400">Based on {selectedAccount.historical_posts_count || 8} past posts</span>
              </div>

              {/* Stacked Progress Bar */}
              <div className="h-3 w-full bg-slate-800 rounded-full overflow-hidden flex shadow-inner mb-3">
                {Object.entries(contentPillars).map(([key, val]) => (
                  <div
                    key={key}
                    style={{ width: `${Math.max(5, Number(val))}%` }}
                    className={`${pillarColorMap[key] || 'bg-slate-600'} transition-all`}
                    title={`${pillarNameMap[key] || key}: ${val}%`}
                  />
                ))}
              </div>

              {/* Pillar Legend Items */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                {Object.entries(contentPillars).map(([key, val]) => (
                  <div key={key} className="flex items-center justify-between p-2 rounded-lg bg-slate-800/50 border border-slate-700/50">
                    <div className="flex items-center space-x-1.5 truncate">
                      <span className={`w-2 h-2 rounded-full shrink-0 ${pillarColorMap[key] || 'bg-slate-500'}`} />
                      <span className="text-slate-300 text-[11px] font-medium truncate">{pillarNameMap[key] || key}</span>
                    </div>
                    <span className="font-bold text-slate-200 text-[11px] shrink-0 ml-1">{val}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Signature Hooks */}
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1.5 flex items-center space-x-1.5">
                <Bookmark className="w-3.5 h-3.5 text-amber-400" />
                <span>Host's Signature Post Openers & Hooks</span>
              </label>
              <div className="space-y-1.5">
                {(profile?.signature_hooks && profile.signature_hooks.length > 0
                  ? profile.signature_hooks
                  : [
                      "Here's what building at scale taught us...",
                      "Excited to unveil our latest engineering milestone...",
                      "Behind the code: lessons from our team hackathon sprint..."
                    ]
                ).map((hook, i) => (
                  <div key={i} className="text-xs text-slate-300 bg-slate-800/60 border border-slate-700/60 rounded-lg px-2.5 py-1.5 italic font-mono truncate">
                    "{hook}"
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Learned Post Types Overview */}
        {profile?.post_types && profile.post_types.length > 0 && (
          <div className="border-t border-slate-800 pt-4 space-y-2">
            <label className="text-xs font-semibold text-slate-300 block">Host Post Archetypes Catalog</label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
              {profile.post_types.slice(0, 3).map((pt, i) => (
                <div key={i} className="p-2.5 rounded-xl bg-slate-800/40 border border-slate-700/50 space-y-1 text-xs">
                  <div className="font-bold text-slate-200 text-xs flex items-center justify-between">
                    <span className="truncate">{pt.name}</span>
                    <span className="text-[10px] text-amber-400 font-mono">{pt.percentage}%</span>
                  </div>
                  <div className="text-[11px] text-slate-400">
                    <span className="text-slate-500">Hook:</span> {pt.hook_style}
                  </div>
                  <div className="text-[11px] text-slate-400">
                    <span className="text-slate-500">CTA:</span> {pt.cta_style}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Section 1: Visual Identity & Color Palette */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
          <div className="flex items-center space-x-2 text-amber-400 font-bold text-sm">
            <Palette className="w-4 h-4" />
            <span>Learned Color Palette & Theme</span>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-2">Dominant Brand Colors (Hex)</label>
            <div className="flex items-center space-x-3">
              {dominantColors.map((col, idx) => (
                <div key={idx} className="space-y-1.5 text-center">
                  <div
                    className="w-12 h-12 rounded-xl border border-white/20 shadow-inner flex items-center justify-center cursor-pointer relative overflow-hidden"
                    style={{ backgroundColor: col }}
                  >
                    <input
                      type="color"
                      value={col}
                      onChange={(e) => {
                        const newCols = [...dominantColors];
                        newCols[idx] = e.target.value.toUpperCase();
                        setDominantColors(newCols);
                      }}
                      className="opacity-0 absolute inset-0 cursor-pointer w-full h-full"
                    />
                  </div>
                  <span className="text-[11px] font-mono text-slate-400 block">{col}</span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-2">Official Brand Logo Watermark</label>
            <div className="flex items-center space-x-4 p-3 bg-slate-800/40 rounded-xl border border-slate-700/60">
              <div className="w-16 h-16 rounded-xl bg-slate-900 border border-slate-700 flex items-center justify-center overflow-hidden shrink-0">
                {profile?.brand_logo_url ? (
                  <img
                    src={(() => {
                      if (!profile.brand_logo_url) return '';
                      if (profile.brand_logo_url.startsWith('http')) return profile.brand_logo_url;
                      const apiUrl = import.meta.env.VITE_API_URL || '';
                      const base = apiUrl ? apiUrl.replace(/\/api\/v1\/?$/, '') : '';
                      return `${base}${profile.brand_logo_url.startsWith('/') ? '' : '/'}${profile.brand_logo_url}`;
                    })()}
                    alt="Brand Logo"
                    className="max-h-full max-w-full object-contain p-1"
                  />
                ) : (
                  <span className="text-[10px] font-bold text-slate-500">NO LOGO</span>
                )}
              </div>
              <div className="space-y-1.5 flex-1">
                <label className="cursor-pointer inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-700 hover:bg-slate-600 text-slate-200 transition-all">
                  <span>Upload PNG / SVG</span>
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/svg+xml"
                    className="hidden"
                    onChange={async (e) => {
                      const file = e.target.files?.[0];
                      if (file && selectedAccount) {
                        try {
                          const url = await api.uploadBrandLogo(selectedAccount.id, file);
                          setProfile((prev) => prev ? { ...prev, brand_logo_url: url } : prev);
                          setSaveNotice('Brand logo uploaded successfully!');
                          setTimeout(() => setSaveNotice(null), 3000);
                        } catch (err: any) {
                          alert('Upload failed: ' + err?.message);
                        }
                      }
                    }}
                  />
                </label>
                <p className="text-[11px] text-slate-400">Transparent PNG with 300+ DPI recommended</p>
              </div>
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-2">Logo Placement on Creatives</label>
            <div className="grid grid-cols-2 gap-2 text-xs">
              {['top_right', 'top_left', 'bottom_right', 'bottom_center'].map((loc) => (
                <button
                  key={loc}
                  type="button"
                  onClick={() => setLogoPlacement(loc)}
                  className={`py-2 px-3 rounded-lg border font-medium capitalize transition-all ${
                    logoPlacement === loc
                      ? 'bg-amber-500/20 border-amber-500 text-amber-300'
                      : 'bg-slate-800/40 border-slate-700 text-slate-400'
                  }`}
                >
                  {loc.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-2">Typography Aesthetic</label>
            <div className="grid grid-cols-2 gap-2 text-xs">
              {[
                { id: 'serif_classic', label: 'Classic Serif' },
                { id: 'modern_sans', label: 'Modern Sans' },
                { id: 'traditional_indic', label: 'Indic Traditional' },
                { id: 'bold_display', label: 'Bold Geometric' }
              ].map((font) => (
                <button
                  key={font.id}
                  type="button"
                  onClick={() => setTypography(font.id)}
                  className={`py-2 px-3 rounded-lg border font-medium transition-all ${
                    typography === font.id
                      ? 'bg-amber-500/20 border-amber-500 text-amber-300'
                      : 'bg-slate-800/40 border-slate-700 text-slate-400'
                  }`}
                >
                  {font.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Section 2: Writing Style & Caption Tone */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 space-y-5">
          <div className="flex items-center space-x-2 text-amber-400 font-bold text-sm">
            <MessageSquare className="w-4 h-4" />
            <span>Tone, Formality & Caption Conventions</span>
          </div>

          <div>
            <div className="flex items-center justify-between text-xs mb-1.5">
              <span className="font-semibold text-slate-300">Formality Index</span>
              <span className="text-amber-400 font-bold">
                {formality < 0.4 ? 'Casual & Conversational' : formality < 0.75 ? 'Professional & Warm' : 'Corporate & Formal'} ({(formality * 100).toFixed(0)}%)
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={formality}
              onChange={(e) => setFormality(parseFloat(e.target.value))}
              className="w-full accent-amber-500 bg-slate-800 cursor-pointer"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-2">Emoji Frequency</label>
            <div className="grid grid-cols-4 gap-2 text-xs">
              {['none', 'minimal', 'moderate', 'expressive'].map((freq) => (
                <button
                  key={freq}
                  type="button"
                  onClick={() => setEmojiFreq(freq)}
                  className={`py-2 rounded-lg border font-medium capitalize text-center transition-all ${
                    emojiFreq === freq
                      ? 'bg-amber-500/20 border-amber-500 text-amber-300'
                      : 'bg-slate-800/40 border-slate-700 text-slate-400'
                  }`}
                >
                  {freq}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-2">Supported Greeting Languages</label>
            <div className="flex items-center space-x-2 text-xs">
              {[
                { id: 'en', label: 'English' },
                { id: 'hi', label: 'Hindi (हिंदी)' },
                { id: 'hinglish', label: 'Hinglish' }
              ].map((lang) => (
                <button
                  key={lang.id}
                  type="button"
                  onClick={() => toggleLanguage(lang.id)}
                  className={`px-3 py-1.5 rounded-lg border font-semibold transition-all ${
                    languages.includes(lang.id)
                      ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300'
                      : 'bg-slate-800/40 border-slate-700 text-slate-400'
                  }`}
                >
                  {lang.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Required Brand Sign-Off</label>
            <input
              type="text"
              value={signOff}
              onChange={(e) => setSignOff(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
              placeholder="e.g. Warm regards, Team TechPulse Innovations"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Prohibited Terms (Comma-separated)</label>
            <input
              type="text"
              value={prohibited}
              onChange={(e) => setProhibited(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-amber-500"
              placeholder="e.g. discount, sale, promotion, buy now"
            />
            <p className="text-[11px] text-slate-500 mt-1">Guarantees no fabricated promotional claims appear in festival greetings.</p>
          </div>
        </div>
      </div>
    </div>
  );
};
