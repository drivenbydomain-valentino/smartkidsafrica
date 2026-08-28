import datetime
from decimal import Decimal

from cloudinary_storage.storage import VideoMediaCloudinaryStorage, MediaCloudinaryStorage
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models, IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import now


# ================= ADMIN ================= #

class AdminProfile(models.Model):
    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('moderator', 'Moderator'),
        ('editor', 'Editor'),
    )

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="adminprofile"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    can_manage_users = models.BooleanField(default=False)
    can_manage_posts = models.BooleanField(default=False)
    can_manage_schools = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=now, db_index=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

# ✅ Basic Post Model (needed for sharing)
class Post(models.Model):

    author = models.ForeignKey(
        User,
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
        User,
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
        User,
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
        User,
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
        User,
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

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")

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

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
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


    def __str__(self):
        return f"{self.user.username} Profile"


class SchoolProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="school_profile")

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

    class Meta:
        ordering = ['school_name']
        indexes = [
            models.Index(fields=['country','state', 'lga']),
        ]

    def __str__(self):
        return self.school_name


# # ================= SIGNALS ================= #

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        StudentProfile.objects.get_or_create(user=instance)

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
    slug = models.SlugField(max_length=255, null=True, blank=True)
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

    def __str__(self):
        return self.title

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return self.book.rrp_price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.book.title} for {self.user.username}"