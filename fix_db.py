import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartkidsafrica.settings")  # Adjust settings path if different
django.setup()

from django.db import connection

def safe_fix():
    with connection.cursor() as cursor:
        # 1. Ensure 'name' column exists or ignore if missing so Django won't fail during ALTER
        cursor.execute("""
            ALTER TABLE django_content_type ADD COLUMN IF NOT EXISTS name varchar(100);
        """)
        print("Ensured 'name' column exists on django_content_type.")

        # 2. Mark the troublesome contenttypes migration as already applied
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES ('contenttypes', '0002_remove_content_type_name', NOW())
            ON CONFLICT DO NOTHING;
        """)
        print("Faked migration contenttypes.0002_remove_content_type_name.")

if __name__ == "__main__":
    safe_fix()