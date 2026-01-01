import { useMemo } from 'react';
import { useAuthStore } from './store';

export interface FeatureAccess {
  tier: string;
  // Free tier
  topProps: boolean;
  basicAnalysis: boolean;
  teamFilters: boolean;
  
  // Basic tier
  allProps: boolean;
  fullAnalysis: boolean;
  smartProjections: boolean;
  oddsComparison: boolean;
  playerSearch: boolean;
  last10Trends: boolean;
  
  // Pro tier
  dvpAnalysis: boolean;
  advancedProjections: boolean;
  apiAccess: boolean;
  prioritySupport: boolean;
  earlyAccess: boolean;
  customAlerts: boolean;
  exportData: boolean;
}

export function useFeatures(): FeatureAccess {
  const { user } = useAuthStore();
  
  const features = useMemo(() => {
    const tier = user?.subscription_tier || 'free';
    
    return {
      tier,
      // Free tier - always available
      topProps: true,
      basicAnalysis: true,
      teamFilters: true,
      
      // Basic tier - requires basic or pro
      allProps: tier !== 'free',
      fullAnalysis: tier !== 'free',
      smartProjections: tier !== 'free',
      oddsComparison: tier !== 'free',
      playerSearch: tier !== 'free',
      last10Trends: tier !== 'free',
      
      // Pro tier - requires pro only
      dvpAnalysis: tier === 'pro',
      advancedProjections: tier === 'pro',
      apiAccess: tier === 'pro',
      prioritySupport: tier === 'pro',
      earlyAccess: tier === 'pro',
      customAlerts: tier === 'pro',
      exportData: tier === 'pro',
    };
  }, [user?.subscription_tier]);
  
  return features;
}

export function useFeatureGate(feature: keyof FeatureAccess): boolean {
  const features = useFeatures();
  return features[feature] as boolean;
}

export function getRequiredTier(feature: keyof FeatureAccess): 'free' | 'basic' | 'pro' {
  const proFeatures: (keyof FeatureAccess)[] = [
    'dvpAnalysis',
    'advancedProjections',
    'apiAccess',
    'prioritySupport',
    'earlyAccess',
    'customAlerts',
    'exportData',
  ];
  
  const basicFeatures: (keyof FeatureAccess)[] = [
    'allProps',
    'fullAnalysis',
    'smartProjections',
    'oddsComparison',
    'playerSearch',
    'last10Trends',
  ];
  
  if (proFeatures.includes(feature)) return 'pro';
  if (basicFeatures.includes(feature)) return 'basic';
  return 'free';
}
