import json
import os
from django.db import migrations
from django.conf import settings


def import_posts_from_json(apps, schema_editor):
    Post = apps.get_model("club", "Post")
    
    # Use dynamic model lookup to safely get your custom user model or fallback to auth.User
    try:
        User = apps.get_model("club", "CustomUser") # or whatever your user model name is
    except LookupError:
        try:
            User = apps.get_model("users", "User")
        except LookupError:
            from django.contrib.auth import get_user_model
            User = get_user_model()

    author = User.objects.first()
    
    json_path = os.path.join(settings.BASE_DIR, "data.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            posts_data = json.load(f)
            for item in posts_data:
                defaults = {
                    "title": item.get("title", "Untitled"),
                    "content": item.get("content", ""),
                }
                if author:
                    defaults["author_id"] = author.id

                Post.objects.update_or_create(
                    slug=item.get("slug"),
                    defaults=defaults,
                )


class Migration(migrations.Migration):

    dependencies = [
        ("club", "0009_alter_schoolprofile_email"),
    ]

    operations = [
        migrations.RunPython(import_posts_from_json),
    ]