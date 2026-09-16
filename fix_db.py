import os
import sys
import django

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try setting default module or fall back to finding settings dynamically
if not os.environ.get("DJANGO_SETTINGS_MODULE"):
    # Replace 'smartkidsafrica.settings' below if your inner folder is named differently (e.g., 'config.settings')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartkids.settings")

try:
    django.setup()
except ModuleNotFoundError:
    # Fallback common folder names if 'smartkidsafrica' directory isn't named that way
    for folder in ["config", "core", "smartkids", "app"]:
        if os.path.exists(os.path.join(os.path.dirname(__file__), folder, "settings.py")):
            os.environ["DJANGO_SETTINGS_MODULE"] = f"{folder}.settings"
            django.setup()
            break

from django.db import connection

def safe_fix():
    with connection.cursor() as cursor:
        # 1. Ensure 'name' column exists so Django won't fail during ALTER
        cursor.execute("""
            ALTER TABLE django_content_type ADD COLUMN IF NOT EXISTS name varchar(100);
        """)
        print("Successfully ensured 'name' column exists on django_content_type.")

        # 2. Mark the migration as applied so Django skips altering it
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES ('contenttypes', '0002_remove_content_type_name', NOW())
            ON CONFLICT DO NOTHING;
        """)
        print("Successfully registered migration contenttypes.0002_remove_content_type_name.")

if __name__ == "__main__":
    safe_fix()