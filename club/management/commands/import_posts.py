import json
from django.core.management.base import BaseCommand
from .models import Post  # Replace with your actual model

class Command(BaseCommand):
    help = 'Imports posts from data.json into the database'

    def handle(self, *args, **options):
        with open('management\commands\import_posts.py', 'r', encoding='utf-8') as f:
            posts_data = json.load(f)

        for item in posts_data:
            Post.objects.update_or_create(
                slug=item['slug'],  # Unique identifier
                defaults={
                    'title': item['title'],
                    'content': item['content'],
                    'published_date': item['published_date'],
                }
            )
        self.stdout.write(self.style.SUCCESS('Successfully imported posts from data.json'))