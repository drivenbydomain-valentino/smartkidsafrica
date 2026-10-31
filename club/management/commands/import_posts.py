import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from club.models import Post


class Command(BaseCommand):
    help = "Imports posts from data.json into the database"

    def handle(self, *args, **options):
        # Path to data.json located in your project root directory (next to manage.py)
        json_path = os.path.join(settings.BASE_DIR, "data.json")

        if not os.path.exists(json_path):
            self.stderr.write(self.style.ERROR(f"File not found at: {json_path}"))
            return

        with open(json_path, "r", encoding="utf-8") as f:
            posts_data = json.load(f)

        count = 0
        for item in posts_data:
            post, created = Post.objects.update_or_create(
                slug=item.get("slug"),
                defaults={
                    "title": item.get("title", ""),
                    "content": item.get("content", ""),
                    "snippet": item.get("snippet", ""),
                    "is_published": item.get("is_published", True),
                },
            )
            count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully processed {count} post(s) from data.json!"
            )
        )