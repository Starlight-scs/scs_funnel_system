from django.urls import path
from .views import ActiveCampaignView, CampaignDetailView, BranchDetailView, LeadSubmissionCreateView

urlpatterns = [
    path('campaigns/active/', ActiveCampaignView.as_view(), name='active-campaign'),
    path('campaigns/<slug:slug>/', CampaignDetailView.as_view(), name='campaign-detail'),
    path('campaigns/<slug:campaign_slug>/branches/<slug:branch_slug>/', BranchDetailView.as_view(), name='branch-detail'),
    path('leads/', LeadSubmissionCreateView.as_view(), name='lead-create'),
]
