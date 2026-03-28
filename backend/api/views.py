from rest_framework import viewsets, generics, status
from django.http import Http404
from rest_framework.response import Response
from .models import Campaign, Branch, CampaignStatus, LeadSubmission
from .serializers import CampaignSerializer, BranchSerializer, LeadSubmissionSerializer

class ActiveCampaignView(generics.RetrieveAPIView):
    serializer_class = CampaignSerializer

    def get_object(self):
        campaign = Campaign.objects.filter(
            status=CampaignStatus.PUBLISHED,
            is_active=True,
        ).first()
        if campaign:
            return campaign
        fallback_campaign = Campaign.objects.filter(
            status=CampaignStatus.PUBLISHED
        ).order_by("id").first()
        if fallback_campaign:
            return fallback_campaign
        raise Http404("No campaigns found.")

class CampaignDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = CampaignSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.method in {"GET", "HEAD", "OPTIONS"}:
            return Campaign.objects.filter(status=CampaignStatus.PUBLISHED)
        return Campaign.objects.all()

class BranchDetailView(generics.RetrieveAPIView):
    serializer_class = BranchSerializer
    
    def get_object(self):
        campaign_slug = self.kwargs.get('campaign_slug')
        branch_slug = self.kwargs.get('branch_slug')
        return Branch.objects.get(
            campaign__slug=campaign_slug,
            campaign__status=CampaignStatus.PUBLISHED,
            slug=branch_slug,
        )

class LeadSubmissionCreateView(generics.CreateAPIView):
    queryset = LeadSubmission.objects.all()
    serializer_class = LeadSubmissionSerializer
