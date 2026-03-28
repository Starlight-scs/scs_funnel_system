from django.db import migrations, models


def populate_campaign_status(apps, schema_editor):
    Campaign = apps.get_model("api", "Campaign")
    Campaign.objects.filter(is_active=True).update(status="published")
    Campaign.objects.filter(is_active=False).update(status="published")


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0007_campaign_is_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="campaign",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("published", "Published"),
                    ("archived", "Archived"),
                ],
                default="draft",
                help_text="Published campaigns can be accessed publicly by slug.",
                max_length=20,
            ),
        ),
        migrations.RunPython(populate_campaign_status, migrations.RunPython.noop),
    ]
