from django.db import migrations, models


def set_initial_active_campaign(apps, schema_editor):
    Campaign = apps.get_model("api", "Campaign")
    if Campaign.objects.filter(is_active=True).exists():
        return

    first_campaign = Campaign.objects.order_by("id").first()
    if first_campaign:
        first_campaign.is_active = True
        first_campaign.save(update_fields=["is_active"])


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0006_video_upload_status_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="campaign",
            name="is_active",
            field=models.BooleanField(
                default=False,
                help_text="Determines which campaign is shown on the frontend home page.",
            ),
        ),
        migrations.RunPython(set_initial_active_campaign, migrations.RunPython.noop),
    ]
