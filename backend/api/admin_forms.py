from django import forms
from django.urls import reverse_lazy

from .models import Branch, CTA, Campaign


READONLY_URL_WIDGET = forms.URLInput(
    attrs={
        "readonly": "readonly",
        "class": "vTextField",
    }
)


class UploadThingVideoWidget(forms.Widget):
    template_name = "admin/widgets/uploadthing_video_widget.html"

    class Media:
        css = {
            "all": ("admin/uploadthing_video_widget.css",),
        }
        js = ("admin/uploadthing_video_widget.js",)

    def __init__(self, *, target_field_name, prepare_url_name, delete_url_name, attrs=None):
        super().__init__(attrs)
        self.target_field_name = target_field_name
        self.prepare_url_name = prepare_url_name
        self.delete_url_name = delete_url_name

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        widget_attrs = context["widget"]["attrs"]
        widget_attrs["target_field_name"] = self.target_field_name
        widget_attrs["prepare_url"] = str(reverse_lazy(self.prepare_url_name))
        widget_attrs["delete_url"] = str(reverse_lazy(self.delete_url_name))
        widget_attrs["current_url"] = value or ""
        return context


class CampaignAdminForm(forms.ModelForm):
    intro_video_upload = forms.FileField(
        required=False,
        label="Video file",
        widget=UploadThingVideoWidget(
            target_field_name="intro_video_url",
            prepare_url_name="admin:api_campaign_prepare_video_upload",
            delete_url_name="admin:api_campaign_delete_video_upload",
        ),
    )

    class Meta:
        model = Campaign
        fields = "__all__"
        widgets = {
            "intro_video_url": READONLY_URL_WIDGET,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["intro_video_upload"].widget.attrs["current_url"] = self.instance.intro_video_url or ""


class BranchAdminForm(forms.ModelForm):
    video_direct_upload = forms.FileField(
        required=False,
        label="Video file",
        widget=UploadThingVideoWidget(
            target_field_name="video_url",
            prepare_url_name="admin:api_branch_prepare_video_upload",
            delete_url_name="admin:api_branch_delete_video_upload",
        ),
    )

    class Meta:
        model = Branch
        fields = "__all__"
        widgets = {
            "video_url": READONLY_URL_WIDGET,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["video_direct_upload"].widget.attrs["current_url"] = self.instance.video_url or ""


class CTAAdminForm(forms.ModelForm):
    calendly_url = forms.URLField(
        required=False,
        label="Calendly URL",
        help_text="Used when CTA type is Schedule a Call.",
    )
    external_url = forms.URLField(
        required=False,
        label="External URL",
        help_text="Used when CTA type is Download a Guide.",
    )
    button_text = forms.CharField(
        required=False,
        max_length=255,
        label="Button text",
    )

    class Meta:
        model = CTA
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = self.instance.config or {}
        cta_type = self.initial.get("type") or getattr(self.instance, "type", "")

        if cta_type == "schedule":
            self.fields["calendly_url"].initial = config.get("url", "")
        elif cta_type == "download":
            self.fields["external_url"].initial = config.get("url", "")

        self.fields["button_text"].initial = config.get("button_text", "")

    def clean(self):
        cleaned_data = super().clean()
        cta_type = cleaned_data.get("type")
        calendly_url = (cleaned_data.get("calendly_url") or "").strip()
        external_url = (cleaned_data.get("external_url") or "").strip()
        button_text = (cleaned_data.get("button_text") or "").strip()

        if cta_type == "schedule" and not calendly_url:
            self.add_error("calendly_url", "Calendly URL is required for schedule CTAs.")
        if cta_type == "download" and not external_url:
            self.add_error("external_url", "External URL is required for download CTAs.")

        config = {}
        if cta_type == "schedule" and calendly_url:
            config["url"] = calendly_url
        elif cta_type == "download" and external_url:
            config["url"] = external_url

        if button_text:
            config["button_text"] = button_text

        cleaned_data["config"] = config
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.config = self.cleaned_data.get("config", {})
        if commit:
            instance.save()
        return instance
