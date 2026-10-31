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
    if not os.path.exists(json_path):
        print(f"\n[Migration Auto-Map] ERROR: data.json NOT found at {json_path}!")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    print(f"\n[Migration Auto-Map] Loaded {len(raw_data)} items from data.json.")

    # Get all valid field names on the Post model
    valid_model_fields = [f.name for f in Post._meta.get_fields()]

    count = 0
    for idx, item in enumerate(raw_data):
        # Extract fields dictionary (supports Django fixtures or flat dicts)
        fields = item.get("fields", item) if isinstance(item, dict) else {}
        
        # Also check top-level item keys if nested
        if isinstance(item, dict):
            for k, v in item.items():
                if k not in fields and k not in ['model', 'pk']:
                    fields[k] = v

        print(f"[Migration Auto-Map] Item {idx+1} keys: {list(fields.keys())}")

        # Build defaults dynamically based on matching model fields
        defaults = {}
        for key, value in fields.items():
            if key in valid_model_fields and key not in ['id', 'slug', 'author']:
                defaults[key] = value

        # Ensure title and content have safe fallbacks if missing or None
        title = (
            fields.get("title") 
            or fields.get("heading") 
            or fields.get("name") 
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

        # Handle author foreign key if model has 'author' or 'author_id'
        if author:
            if "author" in valid_model_fields:
                defaults["author"] = author
            elif "author_id" in valid_model_fields:
                defaults["author_id"] = author.id

        # Generate unique slug
        slug = fields.get("slug") or slugify(title) or f"post-{idx+1}"

        post, created = Post.objects.update_or_create(
            slug=slug,
            defaults=defaults,
        )
        action = "Created" if created else "Updated"
        print(f"[Migration Auto-Map] {action}: '{title}' (slug: {slug}) with fields: {list(defaults.keys())}")
        count += 1

    print(f"[Migration Auto-Map] Successfully processed {count} posts with full data mapping!\n")


def reverse_import(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("club", "0010_import_posts"), # or club, 0011_import_posts depending on your latest
    ]

    operations = [
        migrations.RunPython(
            code=import_posts_from_json,
            reverse_code=reverse_import,
        ),
    ]