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
    print(f"\n[Migration 0013 Force Import] Looking for data.json at: {json_path}")

    if not os.path.exists(json_path):
        print(f"[Migration 0013 Force Import] ERROR: data.json NOT found at {json_path}!")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    print(f"[Migration 0013 Force Import] Loaded {len(raw_data)} total items from fixture dump.")

    count = 0
    for item in raw_data:
        model_name = item.get("model", "").lower()
        if not ("post" in model_name or model_name.endswith(".post")):
            continue

        pk = item.get("pk")
        fields = item.get("fields", {})

        title = fields.get("title")
        content = fields.get("content") or fields.get("body") or fields.get("text")
        slug = fields.get("slug") or (slugify(title) if title else f"post-{pk}")

        if not title or not content:
            continue

        defaults = {
            "title": title,
            "content": content,
        }
        
        for field_name in ["image", "thumbnail", "featured_image", "is_published", "status", "created_at"]:
            if field_name in fields:
                defaults[field_name] = fields[field_name]

        if author and "author" in [f.name for f in Post._meta.get_fields()]:
            defaults["author"] = author

        post, created = Post.objects.update_or_create(
            slug=slug,
            defaults=defaults,
        )
        action = "Created" if created else "Updated"
        print(f"[Migration 0013 Force Import] {action} Post: '{title}' (slug: {slug})")
        count += 1

    print(f"[Migration 0013 Force Import] Successfully restored/imported {count} genuine blog posts!\n")


def reverse_import(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("club", "0012_import_posts"),
    ]

    operations = [
        migrations.RunPython(
            code=import_posts_from_json,
            reverse_code=reverse_import,
        ),
    ]