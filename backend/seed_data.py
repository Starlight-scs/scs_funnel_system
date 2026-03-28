import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Campaign, Branch, CTA, Assessment, AssessmentQuestion, CampaignStatus

def seed():
    # 1. Create Campaign
    campaign, created = Campaign.objects.get_or_create(
        slug='financial-advisor',
        defaults={
            'name': 'Starlight Wealth Management',
            'status': CampaignStatus.PUBLISHED,
            'is_active': True,
            'headline': "There's a place for you here — let's find it.",
            'intro_video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', # Placeholder
        }
    )
    if not created:
        print("Campaign already exists. Skipping seed.")
        return

    # 2. Create Branches
    branches_data = [
        {
            'name': 'Career Changers',
            'slug': 'career-changers',
            'audience_type': 'career_changer',
            'label': 'Looking for a new career?',
            'description': 'Transition into advising with mentorship and training.',
            'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'cta_type': 'assessment',
            'assessment_title': 'Career Fit Assessment',
            'questions': [
                {'text': 'What is your current profession?', 'type': 'text'},
                {'text': 'What is your primary motivation for a change?', 'type': 'multiple_choice', 'options': ['Income potential', 'Autonomy', 'Helping others', 'Growth']},
                {'text': 'Are you comfortable building new client relationships?', 'type': 'multiple_choice', 'options': ['Very comfortable', 'Somewhat comfortable', 'I need training']},
            ]
        },
        {
            'name': 'Interns and Early Talent',
            'slug': 'interns',
            'audience_type': 'intern',
            'label': 'Student or recent graduate?',
            'description': 'Start your journey with exposure and learning.',
            'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'cta_type': 'download',
            'cta_config': {'url': 'https://example.com/program-overview.pdf', 'button_text': 'Download Program Overview'}
        },
        {
            'name': 'Experienced Advisors',
            'slug': 'experienced-advisors',
            'audience_type': 'advisor',
            'label': 'Already an advisor?',
            'description': 'Better support, improved payout, and a culture of growth.',
            'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'cta_type': 'schedule',
            'cta_config': {'url': 'https://calendly.com/example', 'button_text': 'Schedule a Confidential Conversation'}
        },
        {
            'name': 'Potential Clients',
            'slug': 'clients',
            'audience_type': 'client',
            'label': 'Looking for financial guidance?',
            'description': 'Trust, planning, and long-term partnership.',
            'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'cta_type': 'assessment',
            'assessment_title': 'Financial Health Assessment',
            'questions': [
                {'text': 'What are your primary financial goals?', 'type': 'multiple_choice', 'options': ['Retirement', 'Education', 'Estate Planning', 'Investment Growth']},
                {'text': 'What is your current investment horizon?', 'type': 'multiple_choice', 'options': ['< 5 years', '5-10 years', '10+ years']},
            ]
        }
    ]

    for b_data in branches_data:
        branch = Branch.objects.create(
            campaign=campaign,
            name=b_data['name'],
            slug=b_data['slug'],
            audience_type=b_data['audience_type'],
            label=b_data['label'],
            description=b_data['description'],
            video_url=b_data['video_url']
        )
        
        # Create CTA
        CTA.objects.create(
            branch=branch,
            type=b_data['cta_type'],
            config=b_data.get('cta_config', {})
        )

        # Create Assessment if applicable
        if b_data['cta_type'] == 'assessment':
            assessment = Assessment.objects.create(
                branch=branch,
                title=b_data['assessment_title']
            )
            for i, q_data in enumerate(b_data['questions']):
                AssessmentQuestion.objects.create(
                    assessment=assessment,
                    text=q_data['text'],
                    type=q_data['type'],
                    options=q_data.get('options'),
                    order=i
                )

    print("Database seeded successfully with Financial Advisor campaign.")

if __name__ == '__main__':
    seed()
