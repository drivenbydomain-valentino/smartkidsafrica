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
        try:
            User = apps.get_model("club", "CustomUser")
        except LookupError:
            from django.contrib.auth import get_user_model
            User = get_user_model()

    author = User.objects.first()

    json_path = os.path.join(settings.BASE_DIR, "data.json")
    print(f"\n[Migration 0011 Debug] Looking for data.json at: {json_path}")

    if not os.path.exists(json_path):
        print(f"[Migration 0011 Debug] ERROR: data.json NOT found at {json_path}!")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    print(f"[Migration 0011 Debug] Loaded {len(raw_data)} items from data.json.")

    count = 0
    for idx, item in enumerate(raw_data):
        fields = item.get("fields", item) if isinstance(item, dict) else {}
        
        title = (
            fields.get("title")
            or fields.get("headline")
            or fields.get("name")
            or fields.get("caption")
            or f"Post #{idx+1}"
        )
        
        raw_content = (
            fields.get("content")
            or fields.get("body")
            or fields.get("text")
            or fields.get("description")
            or ""
        )
        content = str(raw_content) if raw_content is not None else ""

        slug = fields.get("slug") or slugify(title) or f"post-{idx+1}"

        defaults = {
            "title": title,
            "content": content,
        }
        if author:
            defaults["author_id"] = author.id

        # Automatically check and set publication flags if your model has them
        model_fields = [f.name for f in Post._meta.get_fields()]
        if "is_published" in model_fields:
            defaults["is_published"] = True
        if "status" in model_fields:
            defaults["status"] = "published"

        post, created = Post.objects.update_or_create(
            slug=slug,
            defaults=defaults,
        )
        action = "Created" if created else "Updated"
        print(f"[Migration 0011 Debug] {action}: '{title}' (slug: {slug})")
        count += 1

    print(f"[Migration 0011 Debug] Successfully processed {count} posts into database!\n")


def reverse_import(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("club", "0010_import_posts"),
    ]

    operations = [
        migrations.RunPython(
            code=import_posts_from_json,
            reverse_code=reverse_import,
        ),
    ]