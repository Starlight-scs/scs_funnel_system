from django.test import TestCase
from django.urls import reverse

from .models import (
    Assessment,
    AssessmentQuestion,
    Branch,
    CTA,
    Campaign,
    CampaignStatus,
    LeadSubmission,
)


class ApiEndpointTests(TestCase):
    def setUp(self):
        self.campaign = Campaign.objects.create(
            name="Financial Advisor",
            slug="financial-advisor",
            status=CampaignStatus.PUBLISHED,
            is_active=True,
            intro_video_url="https://example.com/intro.mp4",
            headline="There is a place for you here.",
        )
        self.draft_campaign = Campaign.objects.create(
            name="Private Preview",
            slug="private-preview",
            status=CampaignStatus.DRAFT,
            headline="Preview campaign",
        )
        self.branch = Branch.objects.create(
            campaign=self.campaign,
            name="Experienced Advisors",
            slug="experienced-advisors",
            video_url="https://example.com/experienced.mp4",
            audience_type="advisor",
            description="Better support and a stronger platform.",
            label="Already an advisor?",
        )
        self.cta = CTA.objects.create(
            branch=self.branch,
            type="schedule",
            config={
                "url": "https://calendly.com/example/confidential-conversation",
                "button_text": "Schedule a Confidential Conversation",
            },
        )
        self.assessment = Assessment.objects.create(
            branch=self.branch,
            title="Advisor Qualification Assessment",
        )
        self.question = AssessmentQuestion.objects.create(
            assessment=self.assessment,
            text="How many years have you been advising clients?",
            type="text",
            order=0,
        )

    def test_active_campaign_endpoint_returns_active_campaign(self):
        response = self.client.get(reverse("active-campaign"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["slug"], self.campaign.slug)
        self.assertTrue(payload["is_active"])
        self.assertEqual(payload["status"], CampaignStatus.PUBLISHED)

    def test_campaign_detail_endpoint_returns_branch_context(self):
        response = self.client.get(
            reverse("campaign-detail", kwargs={"slug": self.campaign.slug})
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["slug"], self.campaign.slug)
        self.assertEqual(len(payload["branches"]), 1)
        self.assertEqual(payload["branches"][0]["slug"], self.branch.slug)
        self.assertEqual(payload["branches"][0]["cta"]["type"], self.cta.type)

    def test_draft_campaign_is_not_publicly_accessible(self):
        response = self.client.get(
            reverse("campaign-detail", kwargs={"slug": self.draft_campaign.slug})
        )

        self.assertEqual(response.status_code, 404)

    def test_branch_detail_endpoint_returns_branch_video_and_assessment(self):
        response = self.client.get(
            reverse(
                "branch-detail",
                kwargs={
                    "campaign_slug": self.campaign.slug,
                    "branch_slug": self.branch.slug,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["campaign"], self.campaign.id)
        self.assertEqual(payload["video_url"], self.branch.video_url)
        self.assertEqual(payload["assessment"]["title"], self.assessment.title)
        self.assertEqual(payload["assessment"]["questions"][0]["text"], self.question.text)

    def test_lead_submission_endpoint_creates_submission_and_response_records(self):
        payload = {
            "campaign": self.campaign.id,
            "branch": self.branch.id,
            "cta_type": "assessment",
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "phone": "555-0100",
            "responses": [
                {
                    "question": self.question.id,
                    "answer": "7 years",
                }
            ],
        }

        response = self.client.post(
            reverse("lead-create"),
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        submission = LeadSubmission.objects.get(email="jane@example.com")
        self.assertEqual(submission.branch, self.branch)
        self.assertEqual(submission.responses.count(), 1)
        self.assertEqual(submission.responses.first().answer, "7 years")

    def test_schedule_lead_submission_endpoint_creates_submission_without_responses(self):
        payload = {
            "campaign": self.campaign.id,
            "branch": self.branch.id,
            "cta_type": "schedule",
            "first_name": "Alex",
            "last_name": "Taylor",
            "email": "alex@example.com",
            "phone": "555-0199",
            "responses": [],
        }

        response = self.client.post(
            reverse("lead-create"),
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        submission = LeadSubmission.objects.get(email="alex@example.com")
        self.assertEqual(submission.cta_type, "schedule")
        self.assertEqual(submission.responses.count(), 0)
