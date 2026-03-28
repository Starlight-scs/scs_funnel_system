import json
import csv

from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html

from .admin_forms import BranchAdminForm, CTAAdminForm, CampaignAdminForm
from .models import (
    Assessment,
    AssessmentQuestion,
    AssessmentResponse,
    Branch,
    CTA,
    Campaign,
    CampaignStatus,
    LeadSubmission,
    VideoUploadState,
)
from .upload_utils import (
    UploadThingUploadError,
    delete_uploadthing_file,
    prepare_uploadthing_upload,
)


def _read_upload_request(request):
    payload = json.loads(request.body or "{}")
    file_name = payload.get("file_name")
    file_size = payload.get("file_size")
    file_type = payload.get("file_type") or "video/mp4"

    if not file_name or not isinstance(file_size, int) or file_size <= 0:
        raise ValueError("A valid file name and file size are required.")

    return file_name, file_size, file_type


class UploadPrepareAdminMixin:
    prepare_upload_url_name = None
    delete_upload_url_name = None

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "prepare-video-upload/",
                self.admin_site.admin_view(self.prepare_video_upload_view),
                name=self.prepare_upload_url_name,
            ),
            path(
                "delete-video-upload/",
                self.admin_site.admin_view(self.delete_video_upload_view),
                name=self.delete_upload_url_name,
            ),
        ]
        return custom_urls + urls

    def prepare_video_upload_view(self, request):
        if request.method != "POST":
            return JsonResponse({"error": "Method not allowed."}, status=405)

        try:
            file_name, file_size, file_type = _read_upload_request(request)
            payload = prepare_uploadthing_upload(file_name, file_size, file_type)
            return JsonResponse(payload)
        except (ValueError, json.JSONDecodeError) as exc:
            return JsonResponse({"error": str(exc)}, status=400)
        except UploadThingUploadError as exc:
            return JsonResponse({"error": str(exc)}, status=502)

    def delete_video_upload_view(self, request):
        if request.method != "POST":
            return JsonResponse({"error": "Method not allowed."}, status=405)

        try:
            payload = json.loads(request.body or "{}")
            file_url = payload.get("file_url", "")
            if not file_url:
                return JsonResponse({"deleted": True, "cleared_only": True})

            deleted = delete_uploadthing_file(file_url)
            return JsonResponse({"deleted": True, "cleared_only": not deleted})
        except (ValueError, json.JSONDecodeError) as exc:
            return JsonResponse({"error": str(exc)}, status=400)
        except UploadThingUploadError as exc:
            return JsonResponse({"error": str(exc)}, status=502)


class BranchInline(admin.TabularInline):
    model = Branch
    form = BranchAdminForm
    extra = 1
    fields = (
        "name",
        "slug",
        "audience_type",
        "label",
        "video_direct_upload",
        "video_url",
        "video_link_preview",
    )
    readonly_fields = ("video_link_preview",)

    @admin.display(description="Current video")
    def video_link_preview(self, obj):
        if not obj or not obj.video_url:
            return "No video"
        return format_html(
            '<a href="{}" target="_blank" rel="noreferrer">View</a>',
            obj.video_url,
        )


@admin.register(Campaign)
class CampaignAdmin(UploadPrepareAdminMixin, admin.ModelAdmin):
    form = CampaignAdminForm
    prepare_upload_url_name = "api_campaign_prepare_video_upload"
    delete_upload_url_name = "api_campaign_delete_video_upload"
    list_display = ("name", "slug", "status", "is_active", "activate_campaign_button", "created_at")
    list_filter = ("status", "is_active", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [BranchInline]
    actions = ["set_campaign_active", "publish_campaigns", "archive_campaigns", "draft_campaigns"]
    fieldsets = (
        (None, {
            "fields": ("name", "slug", "status", "is_active", "headline"),
        }),
        ("Video Content", {
            "fields": ("intro_video_upload", "intro_video_url", "video_link_preview"),
            "description": "Choose a file, click Upload, wait for the green check, then save the campaign.",
        }),
    )
    readonly_fields = ("video_link_preview",)

    @admin.display(description="Current video link")
    def video_link_preview(self, obj):
        if not obj or not obj.intro_video_url:
            return "No video uploaded yet."
        return format_html(
            '<a href="{}" target="_blank" rel="noreferrer">{}</a>',
            obj.intro_video_url,
            obj.intro_video_url,
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/set-active/",
                self.admin_site.admin_view(self.set_active_view),
                name="api_campaign_set_active",
            ),
        ]
        return custom_urls + urls

    @admin.display(description="Frontend status")
    def activate_campaign_button(self, obj):
        if obj.status != CampaignStatus.PUBLISHED:
            return "Publish first"
        if obj.is_active:
            return format_html('<strong style="color: #15803d;">{}</strong>', "Homepage default")
        activate_url = reverse("admin:api_campaign_set_active", args=[obj.pk])
        return format_html('<a class="button" href="{}">Set as Homepage</a>', activate_url)

    @admin.action(description="Set selected campaign as homepage default")
    def set_campaign_active(self, request, queryset):
        campaign = queryset.first()
        if not campaign:
            self.message_user(request, "No campaign selected.", level=messages.WARNING)
            return
        if campaign.status != CampaignStatus.PUBLISHED:
            self.message_user(request, "Only published campaigns can be set as the homepage default.", level=messages.WARNING)
            return
        self._activate_campaign(campaign)
        self.message_user(request, f'"{campaign.name}" is now the homepage default.')

    @admin.action(description="Publish selected campaigns")
    def publish_campaigns(self, request, queryset):
        updated = queryset.update(status=CampaignStatus.PUBLISHED)
        self.message_user(request, f"{updated} campaign(s) published.")

    @admin.action(description="Move selected campaigns to draft")
    def draft_campaigns(self, request, queryset):
        updated = queryset.update(status=CampaignStatus.DRAFT, is_active=False)
        self.message_user(request, f"{updated} campaign(s) moved to draft.")

    @admin.action(description="Archive selected campaigns")
    def archive_campaigns(self, request, queryset):
        updated = queryset.update(status=CampaignStatus.ARCHIVED, is_active=False)
        self.message_user(request, f"{updated} campaign(s) archived.")

    def set_active_view(self, request, object_id):
        campaign = self.get_object(request, object_id)
        if campaign is None:
            self.message_user(request, "Campaign not found.", level=messages.ERROR)
            return redirect("admin:api_campaign_changelist")
        if campaign.status != CampaignStatus.PUBLISHED:
            self.message_user(request, "Only published campaigns can be set as the homepage default.", level=messages.WARNING)
            return redirect("admin:api_campaign_changelist")

        self._activate_campaign(campaign)
        self.message_user(request, f'"{campaign.name}" is now the homepage default.')
        return redirect("admin:api_campaign_changelist")

    def _activate_campaign(self, campaign):
        Campaign.objects.exclude(pk=campaign.pk).update(is_active=False)
        Campaign.objects.filter(pk=campaign.pk).update(is_active=True)

    def save_model(self, request, obj, form, change):
        if obj.status != CampaignStatus.PUBLISHED:
            obj.is_active = False
        elif obj.is_active:
            Campaign.objects.exclude(pk=obj.pk).update(is_active=False)
        if obj.intro_video_url:
            obj.video_upload_status = VideoUploadState.COMPLETE
            obj.video_upload_error = ""
        else:
            obj.video_upload_status = VideoUploadState.IDLE
            obj.video_upload_error = ""
        obj.video_upload = None
        super().save_model(request, obj, form, change)


class CTAInline(admin.StackedInline):
    model = CTA
    form = CTAAdminForm
    extra = 1
    fields = ("type", "button_text", "calendly_url", "external_url")


class AssessmentInline(admin.StackedInline):
    model = Assessment
    extra = 1


@admin.register(Branch)
class BranchAdmin(UploadPrepareAdminMixin, admin.ModelAdmin):
    form = BranchAdminForm
    prepare_upload_url_name = "api_branch_prepare_video_upload"
    delete_upload_url_name = "api_branch_delete_video_upload"
    list_display = ("name", "campaign", "audience_type")
    list_filter = ("campaign", "audience_type")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CTAInline, AssessmentInline]
    fieldsets = (
        (None, {
            "fields": ("campaign", "name", "slug", "audience_type", "label", "description"),
        }),
        ("Video Content", {
            "fields": ("video_direct_upload", "video_url", "video_link_preview"),
            "description": "Choose a file, click Upload, wait for the green check, then save the branch.",
        }),
    )
    readonly_fields = ("video_link_preview",)

    @admin.display(description="Current video link")
    def video_link_preview(self, obj):
        if not obj or not obj.video_url:
            return "No video uploaded yet."
        return format_html(
            '<a href="{}" target="_blank" rel="noreferrer">{}</a>',
            obj.video_url,
            obj.video_url,
        )

    def save_model(self, request, obj, form, change):
        if obj.video_url:
            obj.video_upload_status = VideoUploadState.COMPLETE
            obj.video_upload_error = ""
        else:
            obj.video_upload_status = VideoUploadState.IDLE
            obj.video_upload_error = ""
        obj.video_upload = None
        super().save_model(request, obj, form, change)


class QuestionInline(admin.TabularInline):
    model = AssessmentQuestion
    extra = 3


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("title", "branch")
    inlines = [QuestionInline]


class ResponseInline(admin.TabularInline):
    model = AssessmentResponse
    extra = 0
    readonly_fields = ("question", "answer")


def build_lead_report_response(queryset):
    report_queryset = queryset.select_related(
        "campaign",
        "branch",
        "branch__cta",
        "branch__assessment",
    ).prefetch_related("responses__question")

    def get_related_or_none(instance, attr_name):
        try:
            return getattr(instance, attr_name)
        except Exception:
            return None

    question_headers = []
    seen_headers = set()
    for submission in report_queryset:
        for response in submission.responses.all():
            header = response.question.text.strip()
            if header and header not in seen_headers:
                seen_headers.add(header)
                question_headers.append(header)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="lead-submissions-report.csv"'

    writer = csv.writer(response)
    base_headers = [
        "submission_id",
        "submitted_at",
        "campaign_name",
        "campaign_slug",
        "campaign_headline",
        "branch_name",
        "branch_slug",
        "branch_audience_type",
        "branch_label",
        "branch_description",
        "branch_video_url",
        "cta_type",
        "cta_button_text",
        "cta_destination_url",
        "assessment_title",
        "first_name",
        "last_name",
        "email",
        "phone",
        "responses_summary",
    ]
    writer.writerow(base_headers + question_headers)

    for submission in report_queryset:
        branch_cta = get_related_or_none(submission.branch, "cta")
        assessment = get_related_or_none(submission.branch, "assessment")
        response_map = {
            item.question.text.strip(): item.answer
            for item in submission.responses.all()
            if item.question and item.question.text
        }
        responses_summary = " | ".join(
            f"{question}: {answer}"
            for question, answer in response_map.items()
        )

        writer.writerow([
            submission.id,
            submission.created_at.isoformat(),
            submission.campaign.name,
            submission.campaign.slug,
            submission.campaign.headline,
            submission.branch.name,
            submission.branch.slug,
            submission.branch.audience_type,
            submission.branch.label,
            submission.branch.description,
            submission.branch.video_url,
            submission.cta_type,
            branch_cta.config.get("button_text", "") if branch_cta else "",
            branch_cta.config.get("url", "") if branch_cta else "",
            assessment.title if assessment else "",
            submission.first_name,
            submission.last_name,
            submission.email,
            submission.phone,
            responses_summary,
            *[response_map.get(question, "") for question in question_headers],
        ])

    return response


@admin.register(LeadSubmission)
class LeadSubmissionAdmin(admin.ModelAdmin):
    change_list_template = "admin/api/leadsubmission/change_list.html"
    list_display = ("email", "campaign", "branch", "cta_type", "created_at")
    list_filter = ("campaign", "branch", "cta_type", "created_at")
    readonly_fields = ("created_at",)
    inlines = [ResponseInline]
    actions = ["export_context_report"]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "export-report/",
                self.admin_site.admin_view(self.export_report_view),
                name="api_leadsubmission_export_report",
            ),
        ]
        return custom_urls + urls

    @admin.action(description="Export contextual lead report (CSV)")
    def export_context_report(self, request, queryset):
        return build_lead_report_response(queryset)

    def export_report_view(self, request):
        queryset = self.get_queryset(request)
        return build_lead_report_response(queryset)
