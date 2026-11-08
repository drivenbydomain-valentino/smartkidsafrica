import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.text import slugify
from django.db.models import Q


class Command(BaseCommand):
    help = "Imports genuine posts from data.json and cleans up empty posts"

    def handle(self, *args, **options):
        from club.models import Post

        # 1. Clean up empty/dummy posts
        empty_posts = Post.objects.filter(
            Q(content__isnull=True) | 
            Q(content="") | 
            Q(content="No content provided.") | 
            Q(title__icontains="Untitled") |
            Q(title="")
        )
        deleted_count, _ = empty_posts.delete()
        self.stdout.write(f"Cleaned up {deleted_count} empty/dummy posts.")

        # 2. Get author
        try:
            from club.models import User
        except ImportError:
            try:
                from club.models import CustomUser as User
            except ImportError:
                from django.contrib.auth import get_user_model
                User = get_user_model()

        author = User.objects.first()

        # 3. Load data.json
        json_path = os.path.join(settings.BASE_DIR, "data.json")
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f"data.json NOT found at {json_path}!"))
            return

        with open(json_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

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
            self.stdout.write(f"{action} Post: '{title}'")
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} genuine blog posts!"))