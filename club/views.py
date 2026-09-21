from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import ParentProfileForm  # Adjust import based on your forms file
from .models import ParentProfile
# ============================================================
# SMART KIDS AFRICA - VIEWS
# USER AUTHENTICATION / REGISTRATION / PROFILES / ADMIN
# ============================================================
from .models import (
    User,
    StudentProfile,
    ParentProfile,
    TeacherProfile,
    SchoolProfile,
    AdminProfile,
    Post,
    Like,
    Comment,
    Share,
    Book,
    Marketer,
)


# ============================================================
# SMART KIDS AFRICA
# HOME / CONTENT / SOCIAL FEED / BOOKS / MARKETERS
# ============================================================

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils.text import slugify

# IMPORTANT:
# These models must be included in the models import section
# at the top of views.py:
#
# Post
# Like
# Comment
# Share
# Book
# Marketer
# StudentProfile
# SchoolProfile
#
# Your existing:
# User = get_user_model()
# can remain unchanged.


# ============================================================
# HOME
# ============================================================

def home(request):
    """
    Main Smart Kids Africa home/feed page.

    Keeps posts available for the social feed while avoiding
    errors if there are no posts.
    """

    posts = (
        Post.objects
        .select_related("author")
        .prefetch_related("likes", "comments", "shares")
        .order_by("-created_at")
    )

    return render(
        request,
        "club/home.html",
        {
            "posts": posts,
        },
    )


# ============================================================
# ABOUT
# ============================================================

def about(request):
    return render(
        request,
        "club/about.html",
    )


# ============================================================
# CONTACT
# ============================================================

def contact_view(request):

    if request.method == "POST":

        # Keep this flexible because your actual contact form
        # fields were not included in the models.py supplied.

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        if not name or not email or not message:

            messages.error(
                request,
                "Please complete all required contact fields.",
            )

        else:

            # Do not pretend to save the message to a model that
            # has not been supplied. This keeps the view safe.
            #
            # If your existing contact view sends email, keep that
            # existing email logic here.

            messages.success(
                request,
                "Thank you for contacting Smart Kids Africa.",
            )

            return redirect("club:contact")

    return render(
        request,
        "club/contact.html",
    )


# ============================================================
# CREATE NEW POST
# ============================================================

@login_required
def newpost(request):

    if request.method == "POST":

        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()

        image = request.FILES.get("image")
        video = request.FILES.get("video")

        if not title:
            messages.error(
                request,
                "Please enter a post title.",
            )

            return render(
                request,
                "club/newpost.html",
                {
                    "title": title,
                    "content": content,
                },
            )

        if not content and not image and not video:

            messages.error(
                request,
                "Please add some content, an image, or a video.",
            )

            return render(
                request,
                "club/newpost.html",
                {
                    "title": title,
                    "content": content,
                },
            )

        post = Post.objects.create(
            author=request.user,
            title=title,
            content=content,
            image=image,
            video=video,
            meta_description=(
                " ".join(content.split())[:155]
                if content
                else title[:155]
            ),
        )

        messages.success(
            request,
            "Your post was published successfully.",
        )

        return redirect(
            "club:post_detail",
            post_id=post.id,
        )

    return render(
        request,
        "club/newpost.html",
    )


# ============================================================
# MY POSTS
# ============================================================

@login_required
def mypost(request):

    posts = (
        Post.objects
        .filter(author=request.user)
        .select_related("author")
        .prefetch_related("likes", "comments", "shares")
        .order_by("-created_at")
    )

    return render(
        request,
        "club/mypost.html",
        {
            "posts": posts,
        },
    )


# ============================================================
# EDIT POST
# ============================================================

@login_required
def edit_post(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id,
    )

    if post.author != request.user and not (
        request.user.is_superuser
        or getattr(request.user, "is_staff", False)
        or getattr(request.user, "user_type", None) == "admin"
    ):

        messages.error(
            request,
            "You do not have permission to edit this post.",
        )

        return redirect(
            "club:post_detail",
            post_id=post.id,
        )

    if request.method == "POST":

        title = request.POST.get(
            "title",
            post.title,
        ).strip()

        content = request.POST.get(
            "content",
            post.content,
        ).strip()

        if not title:

            messages.error(
                request,
                "Post title cannot be empty.",
            )

            return render(
                request,
                "club/edit_post.html",
                {
                    "post": post,
                },
            )

        post.title = title
        post.content = content

        # Only replace the existing image when a new one
        # has actually been uploaded.
        new_image = request.FILES.get("image")

        if new_image:
            post.image = new_image

        # Only replace video when a new video is uploaded.
        new_video = request.FILES.get("video")

        if new_video:
            post.video = new_video

        post.save()

        messages.success(
            request,
            "Post updated successfully.",
        )

        return redirect(
            "club:post_detail",
            post_id=post.id,
        )

    return render(
        request,
        "club/edit_post.html",
        {
            "post": post,
        },
    )


# ============================================================
# POST DETAIL
# ============================================================

def post_detail(request, post_id):

    post = get_object_or_404(
        Post.objects
        .select_related("author")
        .prefetch_related("likes", "comments", "shares"),
        id=post_id,
    )

    comments = post.comments.select_related(
        "user"
    ).order_by("-created_at")

    liked = False

    if request.user.is_authenticated:
        liked = Like.objects.filter(
            user=request.user,
            post=post,
        ).exists()

    return render(
        request,
        "club/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "liked": liked,
        },
    )


# ============================================================
# BOOK DETAIL
# ============================================================

def book_detail(request, pk=None, slug=None):

    if slug is not None:

        book = get_object_or_404(
            Book,
            slug=slug,
        )

    else:

        book = get_object_or_404(
            Book,
            pk=pk,
        )

    return render(
        request,
        "club/book_detail.html",
        {
            "book": book,
        },
    )


# ============================================================
# CAREERS
# ============================================================

def careers(request):

    return render(
        request,
        "club/careers.html",
    )


# ============================================================
# FINANCE LITERACY
# ============================================================

def financeliteracy(request):

    return render(
        request,
        "club/financeliteracy.html",
    )


# ============================================================
# SAVINGS
# ============================================================

def savings(request):

    return render(
        request,
        "club/savings.html",
    )


# ============================================================
# INVESTMENT
# ============================================================

def investment(request):

    return render(
        request,
        "club/investment.html",
    )


# ============================================================
# STENCIL BOOKS
# ============================================================

def stencilbooks(request):

    books = Book.objects.all().order_by("title")

    return render(
        request,
        "club/stencilbooks.html",
        {
            "books": books,
        },
    )


# ============================================================
# DIGITAL ENTREPRENEURSHIP
# ============================================================

def digitalentrepreneurship(request):

    return render(
        request,
        "club/digitalentrepreneurship.html",
    )


# ============================================================
# CHARACTER BUILDING
# ============================================================

def characterbuilding(request):

    return render(
        request,
        "club/characterbuilding.html",
    )


# ============================================================
# DELETE POST
# ============================================================

@login_required
@require_POST
def delete_post(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id,
    )

    is_admin_user = (
        request.user.is_superuser
        or getattr(request.user, "is_staff", False)
        or getattr(request.user, "user_type", None) == "admin"
    )

    if post.author != request.user and not is_admin_user:

        messages.error(
            request,
            "You do not have permission to delete this post.",
        )

        return redirect(
            "club:post_detail",
            post_id=post.id,
        )

    post.delete()

    messages.success(
        request,
        "Post deleted successfully.",
    )

    return redirect(
        "club:home"
    )


# ============================================================
# INCREMENT POST VIEWS
# ============================================================

@require_POST
def increment_views(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id,
    )

    # Your current Post model does not contain a views field.
    # Therefore this endpoint safely returns the post information
    # without attempting to update a nonexistent database column.

    return JsonResponse(
        {
            "success": True,
            "post_id": post.id,
        }
    )


# ============================================================
# LIKE / UNLIKE POST
# ============================================================

@login_required
@require_POST
def like_post(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id,
    )

    like, created = Like.objects.get_or_create(
        user=request.user,
        post=post,
    )

    if created:

        liked = True

    else:

        like.delete()
        liked = False

    return JsonResponse(
        {
            "success": True,
            "liked": liked,
            "likes": post.likes.count(),
        }
    )


# ============================================================
# ADD COMMENT
# ============================================================

@login_required
@require_POST
def add_comment(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id,
    )

    text = request.POST.get(
        "text",
        request.POST.get(
            "comment",
            "",
        ),
    ).strip()

    if not text:

        return JsonResponse(
            {
                "success": False,
                "error": "Comment cannot be empty.",
            },
            status=400,
        )

    comment = Comment.objects.create(
        user=request.user,
        post=post,
        text=text,
    )

    return JsonResponse(
        {
            "success": True,
            "comment": {
                "id": comment.id,
                "text": comment.text,
                "username": comment.user.username,
                "created_at": comment.created_at.strftime(
                    "%Y-%m-%d %H:%M"
                ),
            },
            "comment_count": post.comments.count(),
        }
    )


# ============================================================
# SHARE POST
# ============================================================

@login_required
@require_POST
def share_post(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id,
    )

    platform = request.POST.get(
        "platform",
        "copy",
    ).lower()

    allowed_platforms = {
        "facebook",
        "x",
        "linkedin",
        "whatsapp",
        "copy",
    }

    if platform not in allowed_platforms:

        platform = "copy"

    try:

        share, created = Share.objects.get_or_create(
            user=request.user,
            post=post,
            share_type="external",
            shared_with=None,
            platform=platform,
        )

    except IntegrityError:

        share = Share.objects.filter(
            user=request.user,
            post=post,
            platform=platform,
        ).first()

        created = False

    post_url = request.build_absolute_uri(
        reverse(
            "club:post_detail",
            kwargs={
                "post_id": post.id,
            },
        )
    )

    return JsonResponse(
        {
            "success": True,
            "created": created,
            "share_url": post_url,
            "platform": platform,
            "shares": post.shares.count(),
        }
    )


# ============================================================
# RECORD SHARE
# ============================================================

@login_required
@require_POST
def record_share(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id,
    )

    platform = request.POST.get(
        "platform",
        "copy",
    ).lower()

    allowed_platforms = {
        "facebook",
        "x",
        "linkedin",
        "whatsapp",
        "copy",
    }

    if platform not in allowed_platforms:
        platform = "copy"

    share, created = Share.objects.get_or_create(
        user=request.user,
        post=post,
        share_type="external",
        shared_with=None,
        platform=platform,
    )

    return JsonResponse(
        {
            "success": True,
            "created": created,
            "platform": platform,
            "share_count": post.shares.count(),
        }
    )


# ============================================================
# GET POST SHARE URL
# ============================================================

def get_post_share_url(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id,
    )

    url = request.build_absolute_uri(
        reverse(
            "club:post_detail",
            kwargs={
                "post_id": post.id,
            },
        )
    )

    return JsonResponse(
        {
            "success": True,
            "url": url,
        }
    )


# ============================================================
# RECORD POST SHARE
# ============================================================

@login_required
@require_POST
def record_post_share(request, post_id):

    post = get_object_or_404(
        Post,
        id=post_id,
    )

    platform = request.POST.get(
        "platform",
        "copy",
    ).lower()

    allowed_platforms = {
        "facebook",
        "x",
        "linkedin",
        "whatsapp",
        "copy",
    }

    if platform not in allowed_platforms:
        platform = "copy"

    share, created = Share.objects.get_or_create(
        user=request.user,
        post=post,
        share_type="external",
        shared_with=None,
        platform=platform,
    )

    return JsonResponse(
        {
            "success": True,
            "created": created,
            "platform": platform,
            "share_count": post.shares.count(),
        }
    )


# ============================================================
# DELETE COMMENT
# ============================================================

@login_required
@require_POST
def delete_comment(request, comment_id):

    comment = get_object_or_404(
        Comment,
        id=comment_id,
    )

    is_admin_user = (
        request.user.is_superuser
        or getattr(request.user, "is_staff", False)
        or getattr(request.user, "user_type", None) == "admin"
    )

    if comment.user != request.user and not is_admin_user:

        return JsonResponse(
            {
                "success": False,
                "error": "You do not have permission to delete this comment.",
            },
            status=403,
        )

    post = comment.post

    comment.delete()

    return JsonResponse(
        {
            "success": True,
            "comment_count": post.comments.count(),
        }
    )


# ============================================================
# SEARCH USERS
# ============================================================

@login_required
def search_users(request):

    query = request.GET.get(
        "q",
        "",
    ).strip()

    users = User.objects.none()

    if query:

        users = (
            User.objects
            .filter(
                Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
            )
            .exclude(id=request.user.id)
            .order_by("username")[:50]
        )

    return render(
        request,
        "club/search_users.html",
        {
            "users": users,
            "query": query,
        },
    )


# ============================================================
# CART
# ============================================================
# Your supplied models.py does not contain a Cart or CartItem
# model. Therefore the cart is stored safely in the session.
#
# Session structure:
#
# {
#     "book_id": quantity
# }
#
# This avoids inventing database models that do not exist.
# ============================================================

def _get_cart(request):

    cart = request.session.get(
        "cart",
        {},
    )

    if not isinstance(cart, dict):
        cart = {}

    return cart


def _save_cart(request, cart):

    request.session["cart"] = cart
    request.session.modified = True


def cart_detail(request):

    cart = _get_cart(request)

    books = Book.objects.filter(
        id__in=[
            int(book_id)
            for book_id in cart.keys()
            if str(book_id).isdigit()
        ]
    )

    items = []
    total = Decimal("0.00")

    for book in books:

        quantity = int(
            cart.get(
                str(book.id),
                cart.get(
                    book.id,
                    1,
                ),
            )
        )

        if quantity < 1:
            quantity = 1

        subtotal = book.rrp_price * quantity

        total += subtotal

        items.append(
            {
                "book": book,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    return render(
        request,
        "club/cart.html",
        {
            "cart": cart,
            "items": items,
            "cart_items": items,
            "total": total,
            "cart_total": total,
        },
    )


@require_POST
def add_to_cart(request, book_id):

    book = get_object_or_404(
        Book,
        id=book_id,
    )

    cart = _get_cart(request)

    key = str(book.id)

    try:
        quantity = int(
            request.POST.get(
                "quantity",
                1,
            )
        )

    except (TypeError, ValueError):
        quantity = 1

    quantity = max(
        1,
        quantity,
    )

    cart[key] = int(
        cart.get(
            key,
            0,
        )
    ) + quantity

    _save_cart(
        request,
        cart,
    )

    messages.success(
        request,
        f'"{book.title}" was added to your cart.',
    )

    return redirect(
        "club:cart"
    )


@require_POST
def update_cart(request, item_id):

    book = get_object_or_404(
        Book,
        id=item_id,
    )

    cart = _get_cart(request)

    key = str(book.id)

    try:
        quantity = int(
            request.POST.get(
                "quantity",
                1,
            )
        )

    except (TypeError, ValueError):
        quantity = 1

    if quantity <= 0:

        cart.pop(
            key,
            None,
        )

    else:

        cart[key] = quantity

    _save_cart(
        request,
        cart,
    )

    return redirect(
        "club:cart"
    )


@require_POST
def remove_from_cart(request, item_id):

    cart = _get_cart(request)

    key = str(item_id)

    cart.pop(
        key,
        None,
    )

    _save_cart(
        request,
        cart,
    )

    messages.success(
        request,
        "Item removed from your cart.",
    )

    return redirect(
        "club:cart"
    )


# ============================================================
# MARKETER LIST
# ============================================================

def marketer_list(request):

    marketers = Marketer.objects.filter(
        is_active=True
    ).order_by(
        "region",
        "name",
    )

    return render(
        request,
        "club/marketers.html",
        {
            "marketers": marketers,
        },
    )


# ============================================================
# PARTNER APPLICATION
# ============================================================

def partner_application(request):

    """
    The supplied models.py does not currently contain a
    PartnerApplication model.

    Therefore this view renders the application page and
    does not attempt to save data into a nonexistent model.
    """

    if request.method == "POST":

        messages.info(
            request,
            "Your partner application form was received. "
            "Please connect your PartnerApplication model/form "
            "to enable database saving.",
        )

        return redirect(
            "club:partner_application"
        )

    return render(
        request,
        "club/partner_application.html",
    )


# ============================================================
# TUTOR CHAT API
# ============================================================

@login_required
@require_POST
def tutor_chat_api(request):

    """
    Your supplied models.py does not contain a TutorChat,
    TutorMessage, or ChatMessage model.

    This endpoint therefore provides a safe JSON response
    without pretending to save chat messages to a model that
    does not exist.
    """

    message = request.POST.get(
        "message",
        "",
    ).strip()

    if not message:

        return JsonResponse(
            {
                "success": False,
                "error": "Please enter a message.",
            },
            status=400,
        )

    return JsonResponse(
        {
            "success": True,
            "message": message,
            "response": (
                "Thank you for your message. "
                "Tutor chat is ready to be connected "
                "to your tutor/chat service."
            ),
        }
    )



from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from django.contrib.auth.decorators import (
    login_required,
    user_passes_test,
)
from django.db import transaction
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.csrf import ensure_csrf_cookie

from .forms import (
    UserLoginForm,
    StudentRegistrationForm,
    ParentRegistrationForm,
    TeacherRegistrationForm,
    SchoolRegistrationForm,
)

from .models import (
    StudentProfile,
    ParentProfile,
    TeacherProfile,
    SchoolProfile,
    AdminProfile,
)


User = get_user_model()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def redirect_after_login(user):
    """
    Redirect users according to their role.

    Currently all roles are directed to the home page,
    as requested. Individual dashboards can be enabled
    later without changing the login functions.
    """

    user_type = getattr(user, "user_type", None)

    if user_type in {
        "admin",
        "parent",
        "teacher",
        "school",
        "student",
    }:
        return redirect("club:home")

    return redirect("club:home")


def get_user_profile(user):
    """
    Safely return the correct profile for the logged-in user.

    This avoids relying on user.profile because the project
    has separate profile models for each role.
    """

    user_type = getattr(user, "user_type", None)

    if user_type == "student":
        return StudentProfile.objects.filter(
            user=user
        ).first()

    if user_type == "parent":
        return ParentProfile.objects.filter(
            user=user
        ).first()

    if user_type == "teacher":
        return TeacherProfile.objects.filter(
            user=user
        ).first()

    if user_type == "school":
        return SchoolProfile.objects.filter(
            user=user
        ).first()

    if user_type == "admin":
        return AdminProfile.objects.filter(
            user=user
        ).first()

    return None


def is_admin(user):
    """
    Check whether the current user is an administrator.
    """

    return (
        user.is_authenticated
        and (
            user.is_superuser
            or getattr(user, "user_type", None) == "admin"
            or getattr(user, "is_staff", False)
        )
    )


# ============================================================
# STUDENT REGISTRATION
# ============================================================

@transaction.atomic
def studentregister(request):

    if request.user.is_authenticated:
        logout(request)

    if request.method == "POST":

        form = StudentRegistrationForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data.get(
                    "email",
                    "",
                ),
                password=form.cleaned_data["password"],
                user_type="student",
            )

            profile = StudentProfile.objects.filter(
                user=user
            ).first()

            if profile is None:
                profile = StudentProfile.objects.create(
                    user=user
                )

            profile.full_name = form.cleaned_data.get(
                "full_name",
                "",
            )

            profile.parent_name = form.cleaned_data.get(
                "parent_name",
                "",
            )

            profile.parent_phone = form.cleaned_data.get(
                "parent_phone",
                "",
            )

            profile.parent_whatsapp = form.cleaned_data.get(
                "parent_whatsapp",
                "",
            )

            profile.age = form.cleaned_data.get(
                "age"
            )

            profile.user_class = form.cleaned_data.get(
                "user_class",
                "",
            )

            profile.school = form.cleaned_data.get(
                "school",
                "",
            )

            profile.bio = form.cleaned_data.get(
                "bio",
                "",
            )

            avatar = request.FILES.get("avatar")

            if avatar:
                profile.avatar = avatar

            profile.save()

            login(
                request,
                user,
            )

            messages.success(
                request,
                "Student account created successfully!",
            )

            return redirect_after_login(user)

    else:

        form = StudentRegistrationForm()

    return render(
        request,
        "club/studentregister.html",
        {
            "form": form,
        },
    )


# ============================================================
# STUDENT LOGIN
# ============================================================

@ensure_csrf_cookie
def student_login(request):

    if request.user.is_authenticated:
        return redirect_after_login(
            request.user
        )

    if request.method == "POST":

        form = UserLoginForm(
            request,
            user_type="student",
            data=request.POST,
        )

        if form.is_valid():

            user = form.get_user()

            login(
                request,
                user,
            )

            messages.success(
                request,
                f"Welcome back, {user.username}!",
            )

            return redirect_after_login(user)

    else:

        form = UserLoginForm(
            request,
            user_type="student",
        )

    return render(
        request,
        "club/student_login.html",
        {
            "form": form,
        },
    )


# ============================================================
# STUDENT DASHBOARD
# ============================================================

@login_required
def student_dashboard(request):

    if getattr(request.user, "user_type", None) != "student":
        messages.error(
            request,
            "You do not have permission to access the student dashboard.",
        )
        return redirect_after_login(request.user)

    profile = get_user_profile(request.user)

    return render(
        request,
        "club/student_dashboard.html",
        {
            "profile": profile,
            "student": profile,
            "user": request.user,
        },
    )


# ============================================================
# PARENT REGISTRATION
# ============================================================
from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import ParentProfile, User  # Adjust imports if your User model is elsewhere


@ensure_csrf_cookie
def parentregister(request):
    if request.user.is_authenticated:
        return redirect("club:parent_dashboard")

    if request.method == "POST":
        parent_name = request.POST.get("parent_name", "").strip()
        email = request.POST.get("email", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        whatsapp_number = request.POST.get("whatsapp_number", "").strip()
        address = request.POST.get("address", "").strip()
        country = request.POST.get("country", "").strip()
        state = request.POST.get("state", "").strip()
        lga = request.POST.get("lga", "").strip()
        avatar = request.FILES.get("avatar")

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "club/parentregister.html",
                {
                    "error": "That username is already taken. Please pick another.",
                    "form_data": request.POST,
                },
            )

        if User.objects.filter(email=email).exists():
            return render(
                request,
                "club/parentregister.html",
                {
                    "error": "An account with this email address already exists.",
                    "form_data": request.POST,
                },
            )

        try:
            with transaction.atomic():
                # 1. Create User instance
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=parent_name,
                )

                # Set user_type so edit_profile works properly
                if hasattr(user, "user_type"):
                    user.user_type = "parent"
                    user.save(update_fields=["user_type"])

                # 2. Create or fetch ParentProfile and attach uploaded avatar
                profile, _ = ParentProfile.objects.get_or_create(user=user)
                profile.whatsapp_number = whatsapp_number
                profile.address = address
                profile.country = country
                profile.state = state
                profile.lga = lga

                if avatar:
                    profile.avatar = avatar  # Ensure field name in model is 'avatar'

                profile.save()

                # Store username in session for login pre-fill
                request.session["registered_username"] = user.username

                messages.success(
                    request,
                    "Account created successfully! Please log in below.",
                )
                return redirect("club:parent_login")

        except Exception as e:
            print("Registration Error:", str(e))
            return render(
                request,
                "club/parentregister.html",
                {
                    "error": f"An error occurred during registration: {e}",
                    "form_data": request.POST,
                },
            )

    return render(request, "club/parentregister.html")

    
# ============================================================
# PARENT LOGIN
# ============================================================
@ensure_csrf_cookie
def parent_login(request):
    if request.user.is_authenticated:
        return redirect_after_login(request.user)

    if request.method == "POST":
        form = UserLoginForm(
            request,
            user_type="parent",
            data=request.POST,
        )
        if form.is_valid():
            # Retrieve the authenticated user from the form's user_cache or cleaned_data
            user = getattr(form, "user_cache", None) or form.cleaned_data.get(
                "user"
            )

            # Fallback authentication if user isn't attached to form
            if not user:
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password")
                user = authenticate(
                    request, username=username, password=password
                )

            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect_after_login(user)

        filled_username = request.POST.get("username", "").strip()

    else:
        registered_username = request.session.pop("registered_username", "")
        filled_username = registered_username

        form = UserLoginForm(
            request,
            user_type="parent",
            initial={"username": registered_username}
            if registered_username
            else {},
        )

    return render(
        request,
        "club/parent_login.html",
        {
            "form": form,
            "registered_username": filled_username,
        },
    )

# ============================================================
# TEACHER REGISTRATION
# ============================================================

def teacherregister(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST, request.FILES) # Pass request.FILES for image upload
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please log in to continue.")
            return redirect('club:teacher_login') # Redirects to Login page first
    else:
        form = TeacherRegistrationForm()
    
    return render(request, 'club/teacher_register.html', {'form': form})


# ============================================================
# TEACHER LOGIN
# ============================================================

@ensure_csrf_cookie
def teacher_login(request):

    if request.user.is_authenticated:
        return redirect_after_login(
            request.user
        )

    if request.method == "POST":

        form = UserLoginForm(
            request,
            user_type="teacher",
            data=request.POST,
        )

        if form.is_valid():

            user = form.get_user()

            login(
                request,
                user,
            )

            messages.success(
                request,
                f"Welcome back, {user.username}!",
            )

            return redirect_after_login(user)

    else:

        form = UserLoginForm(
            request,
            user_type="teacher",
        )

    return render(
        request,
        "club/teacher_login.html",
        {
            "form": form,
        },
    )


# ============================================================
# SCHOOL REGISTRATION
# ============================================================

@transaction.atomic
def schoolregister(request):

    if request.user.is_authenticated:
        logout(request)

    if request.method == "POST":

        form = SchoolRegistrationForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            school_name = form.cleaned_data[
                "school_name"
            ]

            user = User.objects.create_user(
                username=school_name,
                email=form.cleaned_data.get(
                    "email",
                    "",
                ),
                password=form.cleaned_data["password"],
                user_type="school",
            )

            profile = SchoolProfile.objects.filter(
                user=user
            ).first()

            if profile is None:
                profile = SchoolProfile.objects.create(
                    user=user
                )

            profile.school_name = school_name

            profile.director_name = form.cleaned_data.get(
                "director_name",
                "",
            )

            profile.email = form.cleaned_data.get(
                "email",
                "",
            )

            profile.whatsapp_number = form.cleaned_data.get(
                "whatsapp_number",
                "",
            )

            profile.contact_number = form.cleaned_data.get(
                "contact_number",
                "",
            )

            profile.registration_number = (
                form.cleaned_data.get(
                    "registration_number"
                )
            )

            profile.address = form.cleaned_data.get(
                "address",
                "",
            )

            profile.nearest_bus_stop = form.cleaned_data.get(
                "nearest_bus_stop",
                "",
            )

            profile.lga = form.cleaned_data.get(
                "lga",
                "",
            )

            profile.state = form.cleaned_data.get(
                "state",
                "",
            )

            profile.country = form.cleaned_data.get(
                "country",
                "Nigeria",
            )

            profile.num_students = (
                form.cleaned_data.get(
                    "num_students"
                )
                or 0
            )

            # Supports either a normal field or a
            # multiple-choice field.
            school_type = form.cleaned_data.get(
                "school_type",
                "",
            )

            if isinstance(school_type, (list, tuple)):
                school_type = ", ".join(
                    str(item)
                    for item in school_type
                )

            profile.school_type = school_type

            profile.website = form.cleaned_data.get(
                "website"
            )

            avatar = request.FILES.get("avatar")

            if avatar:
                profile.avatar = avatar

            profile.save()

            login(
                request,
                user,
            )

            messages.success(
                request,
                "School account created successfully!",
            )

            return redirect_after_login(user)

    else:

        form = SchoolRegistrationForm()

    return render(
        request,
        "club/schoolregister.html",
        {
            "form": form,
        },
    )


# ============================================================
# SCHOOL LOGIN
# ============================================================

@ensure_csrf_cookie
def school_login(request):

    if request.user.is_authenticated:
        return redirect_after_login(
            request.user
        )

    if request.method == "POST":

        form = UserLoginForm(
            request,
            user_type="school",
            data=request.POST,
        )

        if form.is_valid():

            user = form.get_user()

            login(
                request,
                user,
            )

            messages.success(
                request,
                f"Welcome back, {user.username}!",
            )

            return redirect_after_login(user)

    else:

        form = UserLoginForm(
            request,
            user_type="school",
        )

    return render(
        request,
        "club/school_login.html",
        {
            "form": form,
        },
    )


# ============================================================
# SCHOOL DASHBOARD
# ============================================================

@login_required
def school_dashboard(request):

    if getattr(request.user, "user_type", None) != "school":
        messages.error(
            request,
            "You do not have permission to access the school dashboard.",
        )
        return redirect_after_login(request.user)

    profile = get_user_profile(request.user)

    return render(
        request,
        "club/school_dashboard.html",
        {
            "profile": profile,
            "school": profile,
            "user": request.user,
        },
    )


# ============================================================
# ADMIN LOGIN
# ============================================================

@ensure_csrf_cookie
def admin_login(request):

    if request.user.is_authenticated:

        if is_admin(request.user):
            return redirect("club:admin_dashboard")

        logout(request)

    if request.method == "POST":

        form = UserLoginForm(
            request,
            user_type="admin",
            data=request.POST,
        )

        if form.is_valid():

            user = form.get_user()

            if not is_admin(user):

                messages.error(
                    request,
                    "This account does not have administrator privileges.",
                )

            else:

                login(
                    request,
                    user,
                )

                messages.success(
                    request,
                    "Administrator login successful.",
                )

                return redirect(
                    "club:admin_dashboard"
                )

    else:

        form = UserLoginForm(
            request,
            user_type="admin",
        )

    return render(
        request,
        "club/admin_login.html",
        {
            "form": form,
        },
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):

    total_users = User.objects.count()

    total_students = User.objects.filter(
        user_type="student"
    ).count()

    total_parents = User.objects.filter(
        user_type="parent"
    ).count()

    total_teachers = User.objects.filter(
        user_type="teacher"
    ).count()

    total_schools = User.objects.filter(
        user_type="school"
    ).count()

    total_admins = User.objects.filter(
        user_type="admin"
    ).count()

    context = {
        "total_users": total_users,
        "total_students": total_students,
        "total_parents": total_parents,
        "total_teachers": total_teachers,
        "total_schools": total_schools,
        "total_admins": total_admins,
    }

    return render(
        request,
        "club/admin_dashboard.html",
        context,
    )


# ============================================================
# MANAGE USERS
# ============================================================

@login_required
@user_passes_test(is_admin)
def manage_users(request):

    users = User.objects.all().order_by(
        "-date_joined"
    )

    return render(
        request,
        "club/manage_users.html",
        {
            "users": users,
        },
    )


# ============================================================
# DELETE USER
# ============================================================

@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):

    user = get_object_or_404(
        User,
        id=user_id,
    )

    # Prevent an administrator from accidentally
    # deleting their own active account.
    if user == request.user:

        messages.error(
            request,
            "You cannot delete your own administrator account.",
        )

        return redirect(
            "club:manage_users"
        )

    if request.method == "POST":

        username = user.username

        user.delete()

        messages.success(
            request,
            f"User '{username}' was deleted successfully.",
        )

    return redirect(
        "club:manage_users"
    )


# ============================================================
# MANAGE POSTS
# ============================================================

@login_required
@user_passes_test(is_admin)
def manage_posts(request):

    """
    This view intentionally avoids assuming the exact post
    model name. It checks common model names used by this
    application.
    """

    post_model = None

    for model_name in (
        "Post",
        "SocialPost",
        "FeedPost",
    ):

        try:

            post_model = getattr(
                __import__(
                    f"{__package__}.models",
                    fromlist=[model_name],
                ),
                model_name,
            )

            break

        except AttributeError:
            continue

    posts = (
        post_model.objects.all()
        if post_model is not None
        else []
    )

    return render(
        request,
        "club/manage_posts.html",
        {
            "posts": posts,
        },
    )


# ============================================================
# MANAGE SCHOOLS
# ============================================================

@login_required
@user_passes_test(is_admin)
def manage_schools(request):

    schools = SchoolProfile.objects.select_related(
        "user"
    ).all().order_by(
        "school_name"
    )

    return render(
        request,
        "club/manage_schools.html",
        {
            "schools": schools,
        },
    )


# ============================================================
# GENERAL LOGOUT
# ============================================================

def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully.",
    )

    return redirect(
        "club:home"
    )


# ============================================================
# SIGNOUT
# ============================================================

def signout(request):

    logout(request)

    messages.success(
        request,
        "You have been signed out successfully.",
    )

    return redirect(
        "club:home"
    )


# ============================================================
# SCHOOL LOGOUT
# ============================================================

def school_logout(request):

    logout(request)

    messages.success(
        request,
        "School account logged out successfully.",
    )

    return redirect(
        "club:home"
    )


# ============================================================
# PROFILE - CURRENT USER
# ============================================================

@login_required
def self_profile_view(request):

    return redirect(
        "club:profile_view",
        username=request.user.username,
    )


# ============================================================
# PROFILE - USER
# ============================================================

@login_required
def profile_view(request, username):

    profile_user = get_object_or_404(
        User,
        username=username,
    )

    profile = get_user_profile(
        profile_user
    )

    # --------------------------------------------------------
    # PROFILE PICTURE UPDATE
    # --------------------------------------------------------

    if request.method == "POST":

        if request.user != profile_user:

            messages.error(
                request,
                "You can only edit your own profile.",
            )

            return redirect(
                "club:profile_view",
                username=username,
            )

        avatar = request.FILES.get(
            "avatar"
        )

        if avatar:

            if profile is not None and hasattr(
                profile,
                "avatar",
            ):

                profile.avatar = avatar
                profile.save()

                messages.success(
                    request,
                    "Profile picture updated successfully!",
                )

            else:

                messages.error(
                    request,
                    "This account does not have an editable profile.",
                )

        return redirect(
            "club:profile_view",
            username=username,
        )

    return render(
        request,
        "club/profile.html",
        {
            "profile_user": profile_user,
            "profile": profile,
        },
    )
# club/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ParentProfileForm
from .models import ParentProfile, SchoolProfile, StudentProfile, TeacherProfile


@login_required
def edit_profile(request):
    user = request.user
    user_type = getattr(user, "user_type", None)

    # 1. Dynamically match user type to profile model and form
    if user_type == "parent":
        profile, _ = ParentProfile.objects.get_or_create(user=user)
        form_class = ParentProfileForm
    elif user_type == "student":
        profile, _ = StudentProfile.objects.get_or_create(user=user)
        form_class = StudentProfileForm
    elif user_type == "teacher":
        profile, _ = TeacherProfile.objects.get_or_create(user=user)
        form_class = TeacherProfileForm
    elif user_type == "school":
        profile, _ = SchoolProfile.objects.get_or_create(user=user)
        form_class = SchoolProfileForm
    else:
        # Fallback if account has no valid user_type set
        messages.error(
            request, "This account does not have an editable profile."
        )
        return redirect("home")

    # 2. Handle form submission
    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("club:edit_profile")
    else:
        form = form_class(instance=profile)

    return render(
        request, "club/edit_profile.html", {"form": form, "profile": profile}
    )