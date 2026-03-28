from rest_framework import serializers
from .models import Campaign, Branch, CTA, Assessment, AssessmentQuestion, LeadSubmission, AssessmentResponse

class AssessmentQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentQuestion
        fields = ['id', 'text', 'type', 'options', 'order']

class AssessmentSerializer(serializers.ModelSerializer):
    questions = AssessmentQuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Assessment
        fields = ['id', 'title', 'questions']

class CTASerializer(serializers.ModelSerializer):
    class Meta:
        model = CTA
        fields = ['id', 'type', 'config']

class BranchSerializer(serializers.ModelSerializer):
    cta = CTASerializer(read_only=True)
    assessment = AssessmentSerializer(read_only=True)
    class Meta:
        model = Branch
        fields = ['id', 'campaign', 'name', 'slug', 'video_url', 'audience_type', 'description', 'label', 'cta', 'assessment']

class CampaignSerializer(serializers.ModelSerializer):
    branches = BranchSerializer(many=True, read_only=True)
    class Meta:
        model = Campaign
        fields = ['id', 'name', 'slug', 'status', 'is_active', 'intro_video_url', 'headline', 'branches']

class AssessmentResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentResponse
        fields = ['question', 'answer']

class LeadSubmissionSerializer(serializers.ModelSerializer):
    responses = AssessmentResponseSerializer(many=True, required=False)
    
    class Meta:
        model = LeadSubmission
        fields = ['campaign', 'branch', 'cta_type', 'first_name', 'last_name', 'email', 'phone', 'responses']

    def create(self, validated_data):
        responses_data = validated_data.pop('responses', [])
        submission = LeadSubmission.objects.create(**validated_data)
        for response_data in responses_data:
            AssessmentResponse.objects.create(submission=submission, **response_data)
        return submission
