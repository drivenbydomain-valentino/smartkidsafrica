from django.db import migrations

def safe_noop(apps, schema_editor):
    # Safe no-op to prevent crashing migrations on production
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('club', '0009_previous_migration_name'), # Replace with your actual previous migration name
    ]

    operations = [
        migrations.RunPython(safe_noop),
    ]