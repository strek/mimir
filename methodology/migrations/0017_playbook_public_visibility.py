# Generated manually for public/private visibility MVP.

from django.db import migrations, models


def migrate_legacy_visibility_to_private(apps, schema_editor):
    Playbook = apps.get_model("methodology", "Playbook")
    Playbook.objects.filter(visibility__in=["family", "local"]).update(visibility="private")


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("methodology", "0016_alter_processimprovementproposal_options_and_more"),
    ]

    operations = [
        migrations.RunPython(migrate_legacy_visibility_to_private, noop_reverse),
        migrations.AlterField(
            model_name="playbook",
            name="visibility",
            field=models.CharField(
                choices=[("private", "Private"), ("public", "Public")],
                default="private",
                max_length=20,
            ),
        ),
    ]
