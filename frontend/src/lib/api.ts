import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/',
});

export default api;

export const fetchCampaign = async (slug: string) => {
  const response = await api.get(`campaigns/${slug}/`);
  return response.data;
};

export const fetchActiveCampaign = async () => {
  const response = await api.get('campaigns/active/');
  return response.data;
};

export const updateCampaign = async (slug: string, data: Record<string, unknown>) => {
  const response = await api.patch(`campaigns/${slug}/`, data);
  return response.data;
};

export const fetchBranch = async (campaignSlug: string, branchSlug: string) => {
  const response = await api.get(`campaigns/${campaignSlug}/branches/${branchSlug}/`);
  return response.data;
};

export const submitLead = async (data: Record<string, unknown>) => {
  const response = await api.post('leads/', data);
  return response.data;
};
