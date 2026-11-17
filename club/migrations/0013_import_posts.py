from django.db import migrations

def safe_noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('club', '0009_alter_schoolprofile_email'),
    ]

    operations = [
        migrations.RunPython(safe_noop),
    ]