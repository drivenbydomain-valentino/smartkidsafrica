import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Safely import users and genuine posts from data.json on a fresh or existing DB"

    def handle(self, *args, **options):
        from club.models import Post

        try:
            from club.models import User
        except ImportError:
            try:
                from club.models import CustomUser as User
            except ImportError:
                from django.contrib.auth import get_user_model
                User = get_user_model()

        # 1. Clean up any accidental session/empty posts
        deleted_count, _ = Post.objects.filter(title__startswith="Imported Post #").delete()
        if deleted_count:
            self.stdout.write(self.style.WARNING(f"Removed {deleted_count} invalid imported posts."))

        json_path = os.path.join(settings.BASE_DIR, "data.json")
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f"data.json NOT found at {json_path}!"))
            return

        with open(json_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        # -------------------------------------------------------------
        # PASS 1: Sync all User accounts from data.json
        # -------------------------------------------------------------
        user_pk_map = {}
        user_count = 0
        for item in raw_data:
            model_name = item.get("model", "").lower()
            if model_name in ["club.user", "club.customuser", "auth.user"] or model_name.endswith(".user"):
                pk = item.get("pk")
                fields = item.get("fields", {})
                username = fields.get("username")
                if username:
                    user_obj, _ = User.objects.update_or_create(
                        username=username,
                        defaults={
                            "email": fields.get("email", ""),
                            "password": fields.get("password", ""),
                            "first_name": fields.get("first_name", ""),
                            "last_name": fields.get("last_name", ""),
                            "is_staff": fields.get("is_staff", False),
                            "is_superuser": fields.get("is_superuser", False),
                            "is_active": fields.get("is_active", True),
                        }
                    )
                    if pk is not None:
                        user_pk_map[str(pk)] = user_obj
                        try:
                            user_pk_map[int(pk)] = user_obj
                        except (ValueError, TypeError):
                            pass
                    user_count += 1

        self.stdout.write(self.style.SUCCESS(f"Synced {user_count} user accounts from fixture."))

        # Guarantee a non-null fallback author exists even on a brand-new empty DB
        fallback_author = User.objects.first()
        if not fallback_author:
            fallback_author = User.objects.create_superuser(
                username="smartkids_admin",
                email="mgt@smartkidsafrica.com",
                password="ChangeMe123!"
            )

        # -------------------------------------------------------------
        # PASS 2: Strictly import club.post records only
        # -------------------------------------------------------------
        count = 0
        for item in raw_data:
            model_name = item.get("model", "").lower()
            if model_name != "club.post":
                continue

            pk = item.get("pk")
            fields = item.get("fields", {})

            title = fields.get("title")
            content = fields.get("content") or fields.get("body") or fields.get("text")
            slug = fields.get("slug") or (slugify(title) if title else f"post-{pk}")

            if not title or not content or len(str(content).strip()) < 10:
                continue

            author_id = fields.get("author") or fields.get("user")
            assigned_author = None
            if author_id is not None:
                if isinstance(author_id, list):
                    author_id = author_id[0] if author_id else None
                if author_id is not None:
                    assigned_author = user_pk_map.get(author_id) or user_pk_map.get(str(author_id))
                    if not assigned_author:
                        try:
                            assigned_author = User.objects.filter(pk=int(author_id)).first()
                        except Exception:
                            assigned_author = User.objects.filter(username=str(author_id)).first()

            final_author = assigned_author or fallback_author

            defaults = {
                "title": title,
                "content": content,
                "author": final_author,
            }

            for field_name in ["image", "thumbnail", "featured_image", "is_published", "status", "created_at"]:
                if field_name in fields:
                    defaults[field_name] = fields[field_name]

            post, created = Post.objects.update_or_create(
                slug=slug,
                defaults=defaults,
            )

            action = "Created" if created else "Updated"
            author_name = getattr(post.author, "username", str(post.author))
            self.stdout.write(f"{action} Post: '{title}' -> Author: {author_name}")
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully processed {count} genuine posts!"))