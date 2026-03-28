from django.db import models


class VideoUploadState(models.TextChoices):
    IDLE = 'idle', 'Idle'
    PENDING = 'pending', 'Pending'
    UPLOADING = 'uploading', 'Uploading'
    COMPLETE = 'complete', 'Complete'
    FAILED = 'failed', 'Failed'


class CampaignStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'
    ARCHIVED = 'archived', 'Archived'


class Campaign(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    status = models.CharField(
        max_length=20,
        choices=CampaignStatus.choices,
        default=CampaignStatus.DRAFT,
        help_text="Published campaigns can be accessed publicly by slug.",
    )
    is_active = models.BooleanField(default=False, help_text="Determines which published campaign is shown on the frontend home page.")
    intro_video_url = models.URLField(blank=True, help_text="Video URL (auto-filled when uploading)")
    video_upload = models.FileField(upload_to='temp_uploads/', null=True, blank=True, help_text="Upload video to UploadThing")
    video_upload_status = models.CharField(
        max_length=20,
        choices=VideoUploadState.choices,
        default=VideoUploadState.IDLE,
        help_text="Background upload status for the intro video.",
    )
    video_upload_error = models.TextField(blank=True, default="")
    headline = models.CharField(max_length=255, default="There's a place for you here — let's find it.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Branch(models.Model):
    AUDIENCE_CHOICES = [
        ('career_changer', 'Career Changer'),
        ('intern', 'Intern'),
        ('advisor', 'Experienced Advisor'),
        ('client', 'Potential Client'),
    ]

    campaign = models.ForeignKey(Campaign, related_name='branches', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    video_url = models.URLField(blank=True, help_text="Video URL (auto-filled when uploading)")
    video_upload = models.FileField(upload_to='temp_uploads/', null=True, blank=True, help_text="Upload video to UploadThing")
    video_upload_status = models.CharField(
        max_length=20,
        choices=VideoUploadState.choices,
        default=VideoUploadState.IDLE,
        help_text="Background upload status for this branch video.",
    )
    video_upload_error = models.TextField(blank=True, default="")
    audience_type = models.CharField(max_length=50, choices=AUDIENCE_CHOICES)
    description = models.TextField()
    label = models.CharField(max_length=255)  # Text on the selection card

    class Meta:
        unique_together = ('campaign', 'slug')

    def __str__(self):
        return f"{self.campaign.name} - {self.name}"

class CTA(models.Model):
    CTA_TYPES = [
        ('schedule', 'Schedule a Call'),
        ('download', 'Download a Guide'),
        ('assessment', 'Start an Assessment'),
    ]

    branch = models.OneToOneField(Branch, related_name='cta', on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=CTA_TYPES)
    config = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.branch.name} CTA ({self.type})"

class Assessment(models.Model):
    branch = models.OneToOneField(Branch, related_name='assessment', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"Assessment for {self.branch.name}"

class AssessmentQuestion(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('text', 'Text Input'),
    ]

    assessment = models.ForeignKey(Assessment, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    type = models.CharField(max_length=50, choices=QUESTION_TYPES)
    options = models.JSONField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

class LeadSubmission(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    cta_type = models.CharField(max_length=50)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.branch.name}"

class AssessmentResponse(models.Model):
    submission = models.ForeignKey(LeadSubmission, related_name='responses', on_delete=models.CASCADE)
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    answer = models.TextField()
