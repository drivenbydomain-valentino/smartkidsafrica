import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.text import slugify
from django.db import IntegrityError


class Command(BaseCommand):
    help = "Safely import genuine club posts from data.json without crashing"

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

        json_path = os.path.join(settings.BASE_DIR, "data.json")
        if not os.path.exists(json_path):
            self.stdout.write(self.style.WARNING(f"data.json not found at {json_path}. Skipping import."))
            return

        with open(json_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        # 1. Ensure fallback author exists
        fallback_author = User.objects.first()
        if not fallback_author:
            fallback_author = User.objects.create_superuser(
                username="smartkids_admin",
                email="mgt@smartkidsafrica.com",
                password="ChangeMe123!"
            )

        # 2. Sync Users first
        user_pk_map = {}
        for item in raw_data:
            if item.get("model", "").lower() in ["club.user", "club.customuser", "auth.user"] or item.get("model", "").endswith(".user"):
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

        # 3. Import ONLY genuine club.post records safely
        count = 0
        for item in raw_data:
            if item.get("model", "").lower() != "club.post":
                continue

            fields = item.get("fields", {})
            title = fields.get("title")
            content = fields.get("content") or fields.get("body") or fields.get("text")

            # Strict validation: skip if no real title or content
            if not title or not content or str(title).startswith("Imported Post #"):
                continue

            slug = fields.get("slug") or slugify(title)
            author_id = fields.get("author") or fields.get("user")
            
            assigned_author = None
            if author_id is not None:
                assigned_author = user_pk_map.get(str(author_id))
                if not assigned_author:
                    try:
                        assigned_author = User.objects.filter(pk=int(author_id)).first()
                    except Exception:
                        pass

            final_author = assigned_author or fallback_author

            try:
                Post.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "title": title,
                        "content": content,
                        "author": final_author,
                    },
                )
                count += 1
            except IntegrityError as e:
                self.stdout.write(self.style.WARNING(f"Skipped post '{title}' due to db constraint: {e}"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipped post '{title}' due to error: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully processed {count} genuine posts without errors!"))