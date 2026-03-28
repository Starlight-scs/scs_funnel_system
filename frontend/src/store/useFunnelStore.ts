import { create } from 'zustand';

interface FunnelState {
  campaign: any | null;
  branch: any | null;
  setCampaign: (campaign: any) => void;
  setBranch: (branch: any) => void;
  clear: () => void;
}

export const useFunnelStore = create<FunnelState>((set) => ({
  campaign: null,
  branch: null,
  setCampaign: (campaign) => set({ campaign }),
  setBranch: (branch) => set({ branch }),
  clear: () => set({ campaign: null, branch: null }),
}));
