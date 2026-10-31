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
    print(f"\n[Migration 0012 Debug] Looking for data.json at: {json_path}")

    if not os.path.exists(json_path):
        print(f"[Migration 0012 Debug] ERROR: data.json NOT found at {json_path}!")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    print(f"[Migration 0012 Debug] Loaded {len(raw_data)} items from data.json.")

    if len(raw_data) > 0:
        print(f"[Migration 0012 Debug] Sample first item structure: {raw_data[0]}")

    valid_model_fields = [f.name for f in Post._meta.get_fields()]

    count = 0
    for idx, item in enumerate(raw_data):
        fields = item.get("fields", item) if isinstance(item, dict) else {}
        
        if isinstance(item, dict):
            for k, v in item.items():
                if k not in fields and k not in ['model', 'pk']:
                    fields[k] = v

        defaults = {}
        for key, value in fields.items():
            if key in valid_model_fields and key not in ['id', 'slug', 'author']:
                defaults[key] = value

        title = (
            fields.get("title") 
            or fields.get("heading") 
            or fields.get("name") 
            or fields.get("headline")
            or f"Post #{idx+1}"
        )
        defaults["title"] = title

        raw_content = (
            fields.get("content") 
            or fields.get("body") 
            or fields.get("text") 
            or fields.get("description") 
            or ""
        )
        defaults["content"] = str(raw_content) if raw_content is not None else ""

        if author:
            if "author" in valid_model_fields:
                defaults["author"] = author
            elif "author_id" in valid_model_fields:
                defaults["author_id"] = author.id

        slug = fields.get("slug") or slugify(title) or f"post-{idx+1}"

        post, created = Post.objects.update_or_create(
            slug=slug,
            defaults=defaults,
        )
        action = "Created" if created else "Updated"
        print(f"[Migration 0012 Debug] {action}: '{title}' (slug: {slug})")
        count += 1

    print(f"[Migration 0012 Debug] Successfully processed {count} posts!\n")


def reverse_import(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("club", "0011_import_posts"),
    ]

    operations = [
        migrations.RunPython(
            code=import_posts_from_json,
            reverse_code=reverse_import,
        ),
    ]