import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartkids.settings")  # Replace with your actual settings module
django.setup()

from django.db import connection

def fix_schema():
    with connection.cursor() as cursor:
        # Drop the stale column safely
        cursor.execute("ALTER TABLE django_content_type DROP COLUMN IF EXISTS name;")
        print("Successfully dropped column 'name' from django_content_type.")

if __name__ == "__main__":
    fix_schema()