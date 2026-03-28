from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_add_video_upload'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch',
            name='video_upload_error',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='branch',
            name='video_upload_status',
            field=models.CharField(
                choices=[
                    ('idle', 'Idle'),
                    ('pending', 'Pending'),
                    ('uploading', 'Uploading'),
                    ('complete', 'Complete'),
                    ('failed', 'Failed'),
                ],
                default='idle',
                help_text='Background upload status for this branch video.',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='campaign',
            name='video_upload_error',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='campaign',
            name='video_upload_status',
            field=models.CharField(
                choices=[
                    ('idle', 'Idle'),
                    ('pending', 'Pending'),
                    ('uploading', 'Uploading'),
                    ('complete', 'Complete'),
                    ('failed', 'Failed'),
                ],
                default='idle',
                help_text='Background upload status for the intro video.',
                max_length=20,
            ),
        ),
    ]
