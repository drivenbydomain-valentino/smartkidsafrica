import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from club.models import Post

User = get_user_model()


class Command(BaseCommand):
    help = "Imports posts from data.json into the database"

    def handle(self, *args, **options):
        json_path = os.path.join(settings.BASE_DIR, "data.json")

        if not os.path.exists(json_path):
            self.stderr.write(self.style.ERROR(f"File not found at: {json_path}"))
            return

        author = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not author:
            self.stderr.write(self.style.ERROR("No users found in the database."))
            return

        with open(json_path, "r", encoding="utf-8") as f:
            posts_data = json.load(f)

        count = 0
        for item in posts_data:
            # Change 'author' below to 'user' if your model uses user = ForeignKey(...)
            post, created = Post.objects.update_or_create(
                slug=item.get("slug"),
                defaults={
                    "title": item.get("title", ""),
                    "content": item.get("content", ""),
                    "author": author, 
                },
            )
            count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully processed {count} post(s) from data.json!"
            )
        )