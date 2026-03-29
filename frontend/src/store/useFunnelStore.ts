import { create } from 'zustand';
import type { Branch, Campaign } from '@/lib/api';

interface FunnelState {
  campaign: Campaign | null;
  branch: Branch | null;
  setCampaign: (campaign: Campaign) => void;
  setBranch: (branch: Branch) => void;
  clear: () => void;
}

export const useFunnelStore = create<FunnelState>((set) => ({
  campaign: null,
  branch: null,
  setCampaign: (campaign) => set({ campaign }),
  setBranch: (branch) => set({ branch }),
  clear: () => set({ campaign: null, branch: null }),
}));
