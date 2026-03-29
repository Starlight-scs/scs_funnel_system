import axios from 'axios';

export interface AssessmentQuestion {
  id: number;
  text: string;
  type: string;
  options: unknown;
  order: number;
}

export interface Assessment {
  id: number;
  title: string;
  questions: AssessmentQuestion[];
}

export interface CTAConfig {
  url?: string;
  [key: string]: unknown;
}

export interface CTA {
  id: number;
  type: string;
  config: CTAConfig;
}

export interface Branch {
  id: number;
  campaign: number | { id: number };
  name: string;
  slug: string;
  video_url: string;
  audience_type: string;
  description: string;
  label: string;
  cta: CTA;
  assessment: Assessment | null;
}

export interface Campaign {
  id: number;
  name: string;
  slug: string;
  status: string;
  is_active: boolean;
  intro_video_url: string;
  headline: string;
  branches: Branch[];
}

const defaultApiBaseUrl = '/backend-api/';
const baseURL =
  process.env.NODE_ENV === 'development'
    ? process.env.NEXT_PUBLIC_API_URL || defaultApiBaseUrl
    : defaultApiBaseUrl;

const api = axios.create({
  baseURL,
});

export default api;

const getApiErrorMessage = (error: unknown, fallbackMessage: string) => {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const data = error.response?.data;

    if (status === 404) {
      return fallbackMessage;
    }

    if (typeof data === 'string' && data.trim()) {
      return data;
    }

    if (data && typeof data === 'object') {
      const detail =
        ('detail' in data && typeof data.detail === 'string' && data.detail) ||
        ('message' in data && typeof data.message === 'string' && data.message);

      if (detail) {
        return detail;
      }
    }

    if (status) {
      return `API request failed with status ${status}.`;
    }

    if (error.message) {
      return error.message;
    }
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return fallbackMessage;
};

export const getCampaignErrorMessage = (error: unknown) =>
  getApiErrorMessage(error, 'Campaign not found');

export const getBranchErrorMessage = (error: unknown) =>
  getApiErrorMessage(error, 'Branch not found');

export const fetchCampaign = async (slug: string) => {
  const response = await api.get<Campaign>(`campaigns/${slug}/`);
  return response.data;
};

export const fetchActiveCampaign = async () => {
  const response = await api.get<Campaign>('campaigns/active/');
  return response.data;
};

export const updateCampaign = async (slug: string, data: Record<string, unknown>) => {
  const response = await api.patch(`campaigns/${slug}/`, data);
  return response.data;
};

export const fetchBranch = async (campaignSlug: string, branchSlug: string) => {
  const response = await api.get<Branch>(`campaigns/${campaignSlug}/branches/${branchSlug}/`);
  return response.data;
};

export const submitLead = async (data: Record<string, unknown>) => {
  const response = await api.post('leads/', data);
  return response.data;
};
