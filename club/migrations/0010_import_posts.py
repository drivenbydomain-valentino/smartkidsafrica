import json
import os
from django.db import migrations
from django.conf import settings
from django.utils.text import slugify


def import_posts_from_json(apps, schema_editor):
    Post = apps.get_model("club", "Post")
    
    try:
        User = apps.get_model("club", "User")
    except LookupError:
        from django.contrib.auth import get_user_model
        User = get_user_model()

    author = User.objects.first()

    json_path = os.path.join(settings.BASE_DIR, "data.json")
    if not os.path.exists(json_path):
        print(f"\n[Migration Debug] ERROR: data.json NOT found at {json_path}!")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    print(f"\n[Migration Debug] Loaded {len(raw_data)} raw items from data.json.")

    count = 0
    for idx, item in enumerate(raw_data):
        fields = item.get("fields", item) if isinstance(item, dict) else {}
        
        # Check all possible title variations
        title = (
            fields.get("title")
            or fields.get("headline")
            or fields.get("name")
            or fields.get("caption")
            or (item.get("title") if isinstance(item, dict) else None)
        )
        
        # Check all possible content variations and default to string if None
        raw_content = (
            fields.get("content")
            or fields.get("body")
            or fields.get("text")
            or fields.get("description")
            or (item.get("content") if isinstance(item, dict) else None)
        )
        
        # CRITICAL FIX: Ensure content is never None / NULL
        content = str(raw_content) if raw_content is not None else "No content provided."

        pk = item.get("pk") if isinstance(item, dict) else idx + 1
        raw_slug = fields.get("slug") or (slugify(title) if title else None)

        if not title:
            title = f"Imported Post #{pk}"
        if not raw_slug:
            raw_slug = f"imported-post-{pk}"

        defaults = {
            "title": title,
            "content": content,
        }
        if author:
            defaults["author_id"] = author.id

        post, created = Post.objects.update_or_create(
            slug=raw_slug,
            defaults=defaults,
        )
        action = "Created" if created else "Updated"
        print(f"[Migration Debug] {action} [{idx+1}/{len(raw_data)}]: '{title}' (slug: {raw_slug})")
        count += 1

    print(f"[Migration Debug] Successfully imported {count} unique post(s) into database!\n")


def reverse_import(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("club", "0009_alter_schoolprofile_email"),
    ]

    operations = [
        migrations.RunPython(
            code=import_posts_from_json,
            reverse_code=reverse_import,
        ),
    ]