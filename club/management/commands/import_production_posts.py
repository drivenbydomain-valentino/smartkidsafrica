import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Import genuine posts with correct author mapping and purge empty posts"

    def handle(self, *args, **options):
        from club.models import Post

        # 1. Purge all posts with empty/short content
        all_posts = Post.objects.all()
        deleted_count = 0
        for post in all_posts:
            content_str = str(post.content or "").strip()
            title_str = str(post.title or "").strip()
            if len(content_str) < 10 or title_str.lower() in ["untitled", "test", ""] or not title_str:
                post.delete()
                deleted_count += 1
                
        self.stdout.write(self.style.SUCCESS(f"Cleaned up {deleted_count} empty/dummy posts."))

        # 2. Get User model
        try:
            from club.models import User
        except ImportError:
            try:
                from club.models import CustomUser as User
            except ImportError:
                from django.contrib.auth import get_user_model
                User = get_user_model()

        fallback_author = User.objects.first()

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

            if not title or not content or len(str(content).strip()) < 10:
                continue

            defaults = {
                "title": title,
                "content": content,
            }

            # Safely extract and resolve author_id whether it's a list, string, or int
            author_id = fields.get("author") or fields.get("user")
            assigned_author = None
            if author_id:
                if isinstance(author_id, list):
                    author_id = author_id[0] if author_id else None
                if author_id is not None:
                    try:
                        if str(author_id).isdigit():
                            assigned_author = User.objects.filter(pk=int(author_id)).first()
                        else:
                            assigned_author = User.objects.filter(username=str(author_id)).first()
                    except Exception:
                        pass
            
            defaults["author"] = assigned_author or fallback_author
            
            for field_name in ["image", "thumbnail", "featured_image", "is_published", "status", "created_at"]:
                if field_name in fields:
                    defaults[field_name] = fields[field_name]

            post, created = Post.objects.update_or_create(
                slug=slug,
                defaults=defaults,
            )
            
            if assigned_author:
                post.author = assigned_author
                post.save()

            action = "Created" if created else "Updated"
            author_name = getattr(post.author, "username", str(post.author))
            self.stdout.write(f"{action} Post: '{title}' -> Author: {author_name}")
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully processed {count} genuine blog posts!"))