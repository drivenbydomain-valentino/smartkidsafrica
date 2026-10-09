import datetime
from decimal import Decimal

from cloudinary_storage.storage import VideoMediaCloudinaryStorage, MediaCloudinaryStorage
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models, IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.timezone import now


# ================= PARENT PROFILE ================= #

class ParentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="parentprofile",
    )

    full_name = models.CharField(
        max_length=255,
        blank=True,
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
    )

    whatsapp_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    email = models.EmailField(
        blank=True,
        null=True,
    )

    address = models.TextField(
        blank=True,
    )

    nearest_bus_stop = models.CharField(
        max_length=255,
        blank=True,
    )

    lga = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    state = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    country = models.CharField(
        max_length=100,
        default="Nigeria",
    )

    occupation = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
    )

    bio = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        default=now,
        db_index=True,
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):

        if not self.slug and self.user.username:

            base_slug = slugify(
                self.user.username
            )

            slug = base_slug
            counter = 1

            while ParentProfile.objects.filter(
                slug=slug
            ).exclude(
                id=self.id
            ).exists():

                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):

        return reverse(
            "club:profile_view",
            kwargs={
                "username": self.user.username
            },
        )

    def __str__(self):

        return (
            f"Parent: "
            f"{self.full_name or self.user.username}"
        )




import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# This model assumes that Child Profile models (StudentProfile, SchoolProfile, etc)
# exist and have a OneToOne link to User, such as:
# user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='studentprofile')

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('school', 'School'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('admin', 'Admin'),
    )
    # Important to set a blank user_type for users created in Admin to define later.
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, blank=True, null=True)

    # These custom related_names are critical to avoid collisions with other apps or auth.User.
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='club_user_set',  # Custom related_name prevents collision
        related_query_name='club_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='club_user_permissions_set',  # Custom related_name prevents collision
        related_query_name='club_user_permission',
    )

    @property
    def profile(self):
        """
        Dynamically fetches the specific profile instance based on user_type.
        """
        if not self.user_type:
            return None
        
        # Mapping user_type values to the related_name on the profile models.
        # This handles the specific cases like 'school' having two possibilities.
        profile_attr_map = {
            'student': 'studentprofile',
            'school': 'school_profile', # Checking this first based on your snippet
            'teacher': 'teacherprofile',
            'parent': 'parentprofile',
            'admin': 'adminprofile',
        }

        # Try to get the profile based on the primary related_name mapping.
        profile_attr = profile_attr_map.get(self.user_type)
        if profile_attr:
            profile = getattr(self, profile_attr, None)
            if profile:
                return profile
            
        # Specific fallback for 'school' if 'school_profile' was missing
        if self.user_type == 'school':
            return getattr(self, 'schoolprofile', None)

        return None

    @property
    def avatar_url(self):
        """
        Returns the specific profile avatar URL.
        If no profile or no avatar exists, returns the default avatar placeholder.
        """
        prof = self.profile
        
        # Path to default avatar within your STATIC_URL
        default_avatar_path = settings.STATIC_URL + 'image/default_avatar.png'

        # Check if a specific profile exists
        if not prof:
            return default_avatar_path

        # Check if the profile model has an avatar field
        if not hasattr(prof, 'avatar'):
            return default_avatar_path

        # Check if the avatar field has an assigned file
        if not prof.avatar:
            return default_avatar_path

        # Final check to verify the avatar file actually exists on storage.
        # This prevents ValueError if the database has a path, but the file was deleted.
        try:
            # Note: Checking existence requires direct storage access or file system check.
            # A simpler way often used (which avoids slow filesystem hits per request)
            # is just to try access the url.
            return prof.avatar.url
        except (ValueError, FileNotFoundError):
            # The file is defined in DB but does not exist on disk/storage.
            return default_avatar_path

class TeacherProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teacherprofile"
    )
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    school_name = models.CharField(max_length=255, blank=True, null=True, help_text="Current school where teaching")
    subject_specialization = models.CharField(max_length=255, help_text="e.g., Mathematics, English, Sciences")
    years_of_experience = models.PositiveIntegerField(default=0)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    
    state = models.CharField(max_length=100, blank=True, null=True)
    lga = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default="Nigeria")

    created_at = models.DateTimeField(default=now, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.user.username:
            base_slug = slugify(self.user.username)
            slug = base_slug
            counter = 1
            while TeacherProfile.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Teacher: {self.full_name or self.user.username}"


# ================= PARENT PROFILE ================= #
class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)


# ================= ADMIN ================= #

class AdminProfile(models.Model):
    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('moderator', 'Moderator'),
        ('editor', 'Editor'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="adminprofile"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    can_manage_users = models.BooleanField(default=False)
    can_manage_posts = models.BooleanField(default=False)
    can_manage_schools = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=now, db_index=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


# ✅ Basic Post Model (enhanced with full SEO integration for Smart Kids Africa)
class Post(models.Model):

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    content = models.TextField()

    image = models.ImageField(
        upload_to="posts/",
        blank=True,
        null=True
    )

    video = models.FileField(
        upload_to="videos/",
        storage=VideoMediaCloudinaryStorage(), 
        null=True, 
        blank=True
    )

    title = models.CharField(
        max_length=255
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # --- SEO INTEGRATIONS ---
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, db_index=True)
    meta_description = models.CharField(
        max_length=160, 
        blank=True, 
        null=True, 
        help_text="Optimal length: 150-160 characters for search snippet previews."
    )
    meta_keywords = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="Comma-separated keywords (e.g., kids education, Africa, learning)"
    )
    is_indexable = models.BooleanField(default=True, help_text="Allow search engines to index this post")

    def get_absolute_url(self):
        # Change 'post_detail' to 'club:post_detail'
        return reverse('club:post_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
            
        if not self.meta_description and self.content:
            # Auto-generate meta description if missing
            clean_content = " ".join(self.content.split())
            self.meta_description = clean_content[:155] + "..." if len(clean_content) > 155 else clean_content

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug or self.id})

    @property
    def seo_title(self):
        return f"{self.title} | Smart Kids Africa"

    @property
    def seo_description(self):
        return self.meta_description or (self.content[:150] + "..." if self.content else "Read more on Smart Kids Africa")

    @property
    def seo_image_url(self):
        if self.image:
            return self.image.url
        return "https://smartkidsafrica.com/static/images/default-post-og.jpg"

    def get_schema_json(self):
        """Schema.org Article JSON-LD for Search Engine Rich Snippets"""
        return {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": self.title,
            "description": self.seo_description,
            "image": [self.seo_image_url] if self.seo_image_url else [],
            "datePublished": self.created_at.isoformat() if self.created_at else "",
            "dateModified": self.updated_at.isoformat() if self.updated_at else "",
            "author": {
                "@type": "Person",
                "name": self.author.get_full_name() or self.author.username
            },
            "publisher": {
                "@type": "Organization",
                "name": "Smart Kids Africa",
                "url": "https://smartkidsafrica.com",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://smartkidsafrica.com/static/images/logo.png"
                }
            }
        }

    def total_likes(self):
        return self.likes.count()

    def total_shares(self):
        return self.shares.count()

    def __str__(self):
        return f"{self.author.username} - {self.title or 'Post'}"


class SocialAccount(models.Model):

    PLATFORM_CHOICES = (
        ('facebook', 'Facebook'),
        ('x', 'X'),
        ('linkedin', 'LinkedIn'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="social_accounts"
    )

    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES
    )

    platform_user_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    access_token = models.TextField(
        blank=True,
        null=True
    )

    refresh_token = models.TextField(
        blank=True,
        null=True
    )

    expires_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


# ✅ Enhanced Share Model (internal + external)
class Share(models.Model):

    SHARE_TYPE = (
        ('internal', 'Internal'),
        ('external', 'External'),
    )

    PLATFORM_CHOICES = (
        ('facebook', 'Facebook'),
        ('x', 'X'),
        ('linkedin', 'LinkedIn'),
        ('whatsapp', 'WhatsApp'),
        ('copy', 'Copy Link'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shares"
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="shares"
    )

    share_type = models.CharField(
        max_length=10,
        choices=SHARE_TYPE,
        default='external'
    )

    # Internal sharing
    shared_with = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="received_shares"
    )

    # External platform
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'user',
                    'post',
                    'shared_with',
                    'platform'
                ],
                name='unique_share_combination'
            )
        ]

    def __str__(self):
        if self.share_type == "internal":
            return (
                f"{self.user.username} shared "
                f"{self.post.title} with "
                f"{self.shared_with.username}"
            )

        return (
            f"{self.user.username} shared "
            f"{self.post.title} to {self.platform}"
        )    


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        related_name="likes"
    )

    # FIX: allow migration without errors for existing rows
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        null=True,   # temporary safety for migration
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_like')
        ]
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['user']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} likes {self.post}"


from django.db import models
from django.conf import settings

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user}: {self.text[:20]}"

class StudentProfile(models.Model):
    USER_TYPES = (
        ('student', 'Student'),
        ('school', 'School'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="studentprofile")
    user_type = models.CharField(max_length=10, choices=USER_TYPES, blank=True, null=True)

    parent_name = models.CharField(max_length=100, blank=True, null=True)
    parent_phone = models.CharField(max_length=20, blank=True, null=True)
    parent_whatsapp = models.CharField(max_length=20, blank=True, null=True)

    # CORRECT: Allow null/blank and let the template render a static fallback
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    user_class = models.CharField(max_length=100, blank=True)
    school = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(default=now, db_index=True)

    # --- SEO INTEGRATIONS ---
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.user.username:
            self.slug = slugify(self.user.username)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('student_profile_detail', kwargs={'slug': self.slug or self.id})

    def __str__(self):
        return f"{self.user.username} Profile"


class SchoolProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="school_profile")

    school_name = models.CharField(max_length=255, db_index=True)
    director_name = models.CharField(max_length=255)

    email = models.EmailField(unique=True, db_index=True)

    # CORRECT: Allow null/blank and let the template render a static fallback
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20)
    contact_number = models.CharField(max_length=20, blank=True, null=True)

    registration_number = models.CharField(max_length=50, unique=True, blank=True, null=True)

    address = models.TextField()
    nearest_bus_stop = models.CharField(max_length=255)
    lga = models.CharField(max_length=100, db_index=True)
    state = models.CharField(max_length=100, db_index=True)
    country = models.CharField(max_length=100, db_index=True)

    num_students = models.IntegerField(null=True, blank=True)

    school_type = models.CharField(max_length=100)
    website = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(default=now, db_index=True)

    # --- SEO INTEGRATIONS ---
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, db_index=True)
    meta_description = models.CharField(
        max_length=160, 
        blank=True, 
        null=True,
        help_text="Search engine summary for school profile."
    )
    is_indexable = models.BooleanField(default=True, help_text="Allow indexing on school directory")

    class Meta:
        ordering = ['school_name']
        indexes = [
            models.Index(fields=['country', 'state', 'lga']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug and self.school_name:
            base_slug = slugify(f"{self.school_name}-{self.state}-{self.lga}")
            slug = base_slug
            counter = 1
            while SchoolProfile.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        if not self.meta_description:
            self.meta_description = f"{self.school_name} in {self.lga}, {self.state}, {self.country}. Top rated {self.school_type} on Smart Kids Africa."

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('school_detail', kwargs={'slug': self.slug or self.id})

    @property
    def seo_title(self):
        return f"{self.school_name} - {self.state}, {self.country} | Smart Kids Africa"

    def get_schema_json(self):
        """Schema.org School JSON-LD for Local SEO and Google Search Directory"""
        return {
            "@context": "https://schema.org",
            "@type": "School",
            "name": self.school_name,
            "description": self.meta_description,
            "url": f"https://smartkidsafrica.com{self.get_absolute_url()}",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": f"{self.address}, Near {self.nearest_bus_stop}",
                "addressLocality": self.lga,
                "addressRegion": self.state,
                "addressCountry": self.country
            },
            "telephone": self.whatsapp_number or self.contact_number,
            "email": self.email,
            "image": self.avatar.url if self.avatar else "https://smartkidsafrica.com/static/images/default-school.jpg"
        }

    def __str__(self):
        return self.school_name


# ================= CONSOLIDATED PROFILE CREATION SIGNAL ================= #

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'student':
            StudentProfile.objects.get_or_create(user=instance)
        elif instance.user_type == 'teacher':
            TeacherProfile.objects.get_or_create(user=instance)
        elif instance.user_type == 'parent':
            ParentProfile.objects.get_or_create(user=instance)
        elif instance.user_type == 'school':
            SchoolProfile.objects.get_or_create(user=instance)

            
# ✅ Integrated Social Media (works for both Profile & School)
class SocialMedia(models.Model):
    PLATFORM_CHOICES = [
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('linkedin', 'LinkedIn'),
    ]

    profile = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='socials', null=True, blank=True)
    school_profile = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name='socials', null=True, blank=True)

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    handle = models.CharField(max_length=100)

    def __str__(self):
        owner = self.profile or self.school_profile
        return f"{owner} - {self.platform}: {self.handle}"


class Marketer(models.Model):
    name = models.CharField(max_length=200)
    business_name = models.CharField(max_length=200, blank=True, null=True)
    referral_code = models.CharField(max_length=50, unique=True)
    region = models.CharField(max_length=100, help_text="City, State, or District covered")
    phone_number = models.CharField(max_length=20)
    whatsapp_number = models.CharField(
        max_length=20, 
        help_text="Include country code without + (e.g., 2348000000000)"
    )
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=datetime.date.today)

    def __str__(self):
        return f"{self.name} ({self.referral_code}) - {self.region}"


class Book(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True, db_index=True)
    author = models.CharField(max_length=200)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='book_covers/')
    rrp_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Recommended Retail Price"
    )
    marketers = models.ManyToManyField(
        Marketer, 
        related_name='books', 
        blank=True,
        help_text="Authorized marketers for this book"
    )

    # --- SEO INTEGRATIONS ---
    meta_description = models.CharField(
        max_length=160, 
        blank=True, 
        null=True,
        help_text="Meta summary of book for Google Search"
    )
    is_indexable = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify(f"{self.title}-{self.author}")
            slug = base_slug
            counter = 1
            while Book.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        if not self.meta_description and self.description:
            clean_desc = " ".join(self.description.split())
            self.meta_description = clean_desc[:155] + "..." if len(clean_desc) > 155 else clean_desc

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('book_detail', kwargs={'slug': self.slug or self.id})

    @property
    def seo_title(self):
        return f"{self.title} by {self.author} | Smart Kids Africa Books"

    def get_schema_json(self):
        """Schema.org Book JSON-LD for Search Engine Shopping/Book listings"""
        return {
            "@context": "https://schema.org",
            "@type": "Book",
            "name": self.title,
            "author": {
                "@type": "Person",
                "name": self.author
            },
            "description": self.meta_description or self.description,
            "image": self.cover_image.url if self.cover_image else "",
            "offers": {
                "@type": "Offer",
                "price": str(self.rrp_price),
                "priceCurrency": "NGN",
                "availability": "https://schema.org/InStock"
            }
        }

    def __str__(self):
        return self.title


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)


# Helper function to safely populate seed data AFTER Django has loaded
def seed_initial_books():
    books_data = [
        {"id": 1, "title": "Strokes", "author": "Murphy A. Rich", "slug": "strokes"},
        {"id": 2, "title": "Patterns", "author": "Murphy A. Rich", "slug": "patterns"},
        {"id": 3, "title": "123 to 10 Vol. 1", "author": "Murphy A. Rich", "slug": "123-10-vol1"},
    ]
    for item in books_data:
        Book.objects.get_or_create(id=item["id"], defaults=item)