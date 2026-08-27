import json
import time
from functools import wraps
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, get_object_or_404
from .models import Book
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, logout
from django.contrib.auth import login as auth_login  # Resolves conflict between standard login and auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from .forms import ProfileForm  # or StudentProfileForm depending on your setup
from .models import (
    AdminProfile,
    Comment,
    Like,
    Post,
    SchoolProfile,
    Share,
    StudentProfile,
)


def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # ✅ Only allow staff/admin users
            if user.is_staff or user.is_superuser:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "You are not authorized as an admin.")
                return redirect('admin_login')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('admin_login')

    return render(request, 'club/admin_login.html')


def no_permission(request):
    return render(request, 'club/no_permission.html')


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'adminprofile'):
            return redirect('no_permission')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@admin_required
def admin_dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'total_posts': Post.objects.count(),
        'total_comments': Comment.objects.count(),
        'total_schools': SchoolProfile.objects.count(),
    }
    return render(request, 'club/admin_dashboard.html', context)

@login_required
@admin_required
def manage_users(request):
    users = User.objects.all()
    return render(request, 'club/manage_users.html', {'users': users})


@login_required
@admin_required
def manage_posts(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'club/manage_posts.html', {'posts': posts})


@login_required
@admin_required
def manage_schools(request):
    schools = SchoolProfile.objects.all()
    return render(request, 'club/manage_schools.html', {'schools': schools})


@login_required
@admin_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return redirect('manage_posts')


@login_required
@admin_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('manage_users')

@receiver(post_save, sender=User)
def create_admin_profile(sender, instance, created, **kwargs):
    if created and instance.is_staff:
        AdminProfile.objects.create(user=instance, role='moderator')


def _debug_log(hypothesis_id, location, message, data):
    # region agent log
    try:
        with open('debug-cad0c0.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                "sessionId": "cad0c0",
                "runId": "school-image-debug-1",
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data,
                "timestamp": int(time.time() * 1000),
            }) + "\n")
    except Exception:
        pass
    # endregion

def studentregister(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return render(request, "club/studentregister.html", {"error": "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            return render(request, "club/studentregister.html", {"error": "Username already exists"})

        user = User.objects.create_user(username=username, password=password1)
        user.save()

        # 👇 ADD THIS REDIRECT AFTER SUCCESS
        return redirect("student_login")

    return render(request, "club/studentregister.html")


@login_required(login_url="student_login")
def student_dashboard(request):
    user = request.user
    
    # 1. Fetch the student profile safely
    try:
        profile = StudentProfile.objects.get(user=user)
        school = profile.school 
    except StudentProfile.DoesNotExist:
        # Fallback safeguard: create a blank profile if it got missed during signup
        profile = StudentProfile.objects.create(user=user, user_type='student')
        school = ""

    # 2. Grab their classmates (matching by school name string)
    if school:
        classmates = StudentProfile.objects.filter(school=school).exclude(user=user)
    else:
        classmates = StudentProfile.objects.none()

    # 3. Match the context variables EXACTLY to your HTML tags!
    context = {
        "profile_user": user,       # This fixes {{ profile_user.username }}
        "profile": profile,         # Gives easy access to profile data
        "school": school,           # Pass the school name string
        "classmates": classmates,   # Pass the classmates list
        "posts": [],                # Fixes the {% for post in posts %} loop so it doesn't break
    }
    return render(request, "club/student_dashboard.html", context)

# ✅ Delete Post
@login_required
def delete_post(request, post_id):
    if request.method != "POST":
        return HttpResponseForbidden("Invalid request")

    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return HttpResponseForbidden("You cannot delete this post")

    post.delete()
    return redirect('mypost')

def add_comment(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        text = data.get("text")

        comment = Comment.objects.create(
            user=request.user,
            post_id=post_id,
            text=text
        )

        return JsonResponse({
            "user": request.user.username,
            "text": comment.text
        })

def search_users(request):
    query = request.GET.get('q')
    users = []

    if query:
        users = User.objects.filter(username__icontains=query)

    return render(request, 'club/search_results.html', {
        'query': query,
        'users': users
    })

def view_profile(request, username):
    user_obj = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user_obj).order_by('-created_at')

    return render(request, 'club/profile.html', {
        'profile_user': user_obj,
        'posts': posts
    })

@login_required
def share_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    Share.objects.create(
        post=post,
        user=request.user
    )
    return JsonResponse({
        "message": "Post shared successfully"
    })
    if request.method != "POST":
        return HttpResponseForbidden()

def get_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comment_set.all().order_by("-created_at")

    data = [
        {"user": c.user.username, "text": c.text}
        for c in comments
    ]

    return JsonResponse(data, safe=False)


def increment_views(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.views += 1
    post.save()

    return JsonResponse({"views": post.views})

# ✅ Delete Comment
@login_required
def delete_comment(request, comment_id):
    if request.method != "POST":
        return HttpResponseForbidden("Invalid request")

    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.author:
        return HttpResponseForbidden("You cannot delete this comment")

    comment.delete()

    return redirect('mypost')  # ✅ FIXED

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse

from .models import Post, Share


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse

@login_required
def share_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    post_url = request.build_absolute_uri(
        reverse('post_detail', args=[post.id])
    )

    return JsonResponse({
        "success": True,
        "url": post_url,
        "title": post.title,
        "content": post.content[:200],
    })

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from .models import Post, Share

@require_GET
def get_post_share_url(request, post_id):
    """
    Returns the absolute canonical URL of a post so social platforms can fetch metadata.
    """
    post = get_object_or_404(Post, id=post_id)
    # Generate full absolute URL (e.g. https://yourdomain.com/post/12/)
    # Replace 'post_detail' with your actual post detail view name if different
    relative_url = f"/post/{post.id}/" 
    absolute_url = request.build_absolute_uri(relative_url)
    
    return JsonResponse({'url': absolute_url})


@require_POST
def record_post_share(request, post_id):
    """
    Records the share activity in the database.
    """
    post = get_object_or_404(Post, id=post_id)
    platform = request.POST.get('platform', 'copy')
    
    user = request.user if request.user.is_authenticated else None

    if user:
        # Prevent exact duplicate constraint violations if unique_share_combination applies
        share, created = Share.objects.get_or_create(
            user=user,
            post=post,
            platform=platform,
            share_type='external',
            defaults={'shared_with': None}
        )
        return JsonResponse({'success': True, 'shares': post.total_shares()})
    
    return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=401)


@login_required
def record_share(request, post_id):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required"},
            status=405
        )

    post = get_object_or_404(Post, id=post_id)

    platform = request.POST.get("platform")

    allowed_platforms = [
        "facebook",
        "x",
        "linkedin",
        "whatsapp",
        "copy",
    ]

    if platform not in allowed_platforms:
        return JsonResponse(
            {"error": "Invalid sharing platform"},
            status=400
        )

    Share.objects.get_or_create(
        user=request.user,
        post=post,
        platform=platform,
        share_type="external",
        shared_with=None,
    )

    post_url = request.build_absolute_uri(
        reverse('post_detail', args=[post.id])
    )

    return JsonResponse({
        "success": True,
        "url": post_url,
        "platform": platform,
    })

@login_required
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)
    user = request.user

    like_obj, created = Like.objects.get_or_create(user=user, post=post)

    if not created:
        like_obj.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        "liked": liked,
        "likes": post.likes.count()
    })

@csrf_protect
def student_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, "club/student_login.html", {
                "error": "All fields are required"
            })

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            return render(request, "club/student_login.html", {
                "error": "Invalid username or password"
            })

    return render(request, "club/student_login.html")

def home(request):
    posts = Post.objects.all().order_by('-created_at')

    for post in posts[:15]:
        school_profile = SchoolProfile.objects.filter(user=post.author).first()

        profile = getattr(post.author, "profile", None)

        _debug_log("SI2", "home", "avatar check", {
            "post_id": post.id,
            "author": post.author.username,
            "is_school_author": bool(school_profile),
            "school_avatar": bool(getattr(school_profile, "avatar", None)) if school_profile else False,
            "profile_avatar": bool(getattr(profile, "avatar", None)) if profile else False,
        })

    return render(request, 'club/home.html', {'posts': posts})



@login_required(login_url='login')
def newpost(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        Post.objects.create(
            title=title,
            content=content,
            image=image,
            video=video,
            author=request.user
        )
        return redirect('home')

    return render(request, 'club/newpost.html')

@login_required(login_url='login')
def mypost(request):
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'club/mypost.html', {'posts': posts})

User = get_user_model()


# views.py
@login_required
def profile_view(request):
    # Retrieve the student profile (or school profile)
    profile = request.user.profile  # or request.user.studentprofile
    
    if request.method == 'POST':
        # MUST include request.FILES along with request.POST
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'club/profile.html', {
        'profile_user': request.user,
        'form': form,
    })

def signout(request):
    logout(request)
    return redirect('home')

def about(request):
    return render(request, 'club/about.html')

def contact(request):
    return render(request, 'club/contact.html')

def savings(request):
    return render(request, 'club/savings.html')

def investment(request):
    return render(request, 'club/investment.html')

def careers(request):
    return render(request, 'club/careers.html')

def entrepreneurship(request):
    return render(request, 'club/entrepreneurship.html')

def careers(request):
    return render(request, 'club/careers.html')

def books(request):
    books = Book.objects.all()
    return render(request, 'club/books.html', {'books': books})

# views.py
from django.shortcuts import render, get_object_or_404
from .models import Book  # Adjust to your model name

# Hardcoded dictionary matching your 8 static fallback books
STATIC_BOOKS = {
    1: {"title": "Strokes", "author": "Murphy A. Rich", "description": "A foundational workbook to strokes skills building.", "cover": "image/book_covers/strokes.jpeg"},
    2: {"title": "Patterns", "author": "Murphy A. Rich", "description": "A foundational workbook to patterns skills building.", "cover": "image/book_covers/patterns.jpeg"},
    3: {"title": "123 to 10 Vol. 1", "author": "Murphy A. Rich", "description": "A foundational workbook to number skills building.", "cover": "image/book_covers/123_10_vol1.jpeg"},
    4: {"title": "123 to 20 Vol. 2", "author": "Murphy A. Rich", "description": "A foundational workbook to number skills building.", "cover": "image/book_covers/123_20_vol2.jpeg"},
    5: {"title": "abc to m Vol. 1", "author": "Murphy A. Rich", "description": "A foundational workbook to letter skills building.", "cover": "image/book_covers/abc_m_vol1.jpeg"},
    6: {"title": "abc to z Vol. 2", "author": "Murphy A. Rich", "description": "A foundational workbook to letter skills building.", "cover": "image/book_covers/abc_z_vol2.jpeg"},
    7: {"title": "Capital ABC to Z", "author": "Murphy A. Rich", "description": "A foundational workbook to letter skills building.", "cover": "image/book_covers/CAPITAL_ABC_Z.jpeg"},
    8: {"title": "Drawing & Colouring", "author": "Murphy A. Rich", "description": "A foundational workbook to art skills building.", "cover": "image/book_covers/drawing_colouring.jpeg"},
}

# def book_detail(request, pk):
#     try:
#         # Try fetching from database first
#         book = Book.objects.get(pk=pk)
#     except (Book.DoesNotExist, ValueError):
#         # Fallback to static dummy data if not in DB
#         book = STATIC_BOOKS.get(pk)
        
#         if not book:
#             # If it's not in DB AND not in static list, return 404
#             from django.http import Http404
#             raise Http404("Book not found")

#     return render(request, 'club/book_detail.html', {'book': book})

# views.py
# def book_detail(request, pk):
#     try:
#         book = Book.objects.get(pk=pk)
#     except (Book.DoesNotExist, ValueError):
#         book = STATIC_BOOKS.get(int(pk))
#         if not book:
#             raise Http404("Book not found")

#     context = {
#         'book': book,
#         'pk': pk,  # <-- Pass 'pk' explicitly to context!
#     }
#     return render(request, 'club/book_detail.html', context)

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Book, Marketer

# def book_detail(request, slug):
#     book = get_object_or_404(Book, slug=slug)
    
#     # Fetch active marketers assigned to this book
#     marketers = book.marketers.filter(is_active=True)
    
#     # Handle search/filter by region or marketer name
#     query = request.GET.get('q', '').strip()
#     if query:
#         marketers = marketers.filter(
#             Q(name__icontains=query) |
#             Q(region__icontains=query) |
#             Q(business_name__icontains=query)
#         )
    
#     # Handle auto-selection via URL referral code (e.g. ?ref=MARKETER123)
#     ref_code = request.GET.get('ref', '').strip()
#     selected_marketer = None
#     if ref_code:
#         selected_marketer = marketers.filter(referral_code__iexact=ref_code).first()

#     context = {
#         'book': book,
#         'marketers': marketers,
#         'query': query,
#         'ref_code': ref_code,
#         'selected_marketer': selected_marketer,
#     }
#     return render(request, 'club/book_detail.html', context)

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Book

def book_detail(request, slug):
    # If 'slug' is actually a number (e.g. /books/3/), look up by ID
    if slug.isdigit():
        book = get_object_or_404(Book, pk=int(slug))
    else:
        book = get_object_or_404(Book, slug=slug)
    
    # Active marketers assigned to this book
    marketers = book.marketers.filter(is_active=True)
    
    # Search/filter by region or name
    query = request.GET.get('q', '').strip()
    if query:
        marketers = marketers.filter(
            Q(name__icontains=query) |
            Q(region__icontains=query) |
            Q(business_name__icontains=query)
        )
    
    # Referral code lookup (?ref=CODE)
    ref_code = request.GET.get('ref', '').strip()
    selected_marketer = None
    if ref_code:
        selected_marketer = marketers.filter(referral_code__iexact=ref_code).first()

    context = {
        'book': book,
        'marketers': marketers,
        'query': query,
        'ref_code': ref_code,
        'selected_marketer': selected_marketer,
    }
    return render(request, 'store/book_detail.html', context)

def financeliteracy(request):
    return render(request, 'club/financeliteracy.html')


def digitalentrepreneurship(request):
    return render(request, 'club/digitalentrepreneurship.html')


def characterbuilding(request):
    return render(request, 'club/characterbuilding.html')

from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect

from .models import SchoolProfile


@csrf_protect
def schoolregister(request):
    if request.method == "POST":
        # Get form data
        school_name = request.POST.get("school_name", "").strip()
        password = request.POST.get("password", "")
        director_name = request.POST.get("director_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        avatar = request.FILES.get("avatar")
        whatsapp_number = request.POST.get("whatsapp_number", "").strip()
        address = request.POST.get("address", "").strip()
        nearest_bus_stop = request.POST.get("nearest_bus_stop", "").strip()
        lga = request.POST.get("lga", "").strip()
        state = request.POST.get("state", "").strip()
        country = request.POST.get("country", "").strip()
        num_students = request.POST.get("num_students", "").strip()

        # Get selected school types
        school_types = request.POST.getlist("school_type")
        school_type_str = ", ".join(school_types)

        # ---------------------------------------------------------
        # Validation
        # ---------------------------------------------------------

        if not school_name:
            return render(
                request,
                "club/schoolregister.html",
                {
                    "error": "School name is required.",
                    "form_data": request.POST,
                },
            )

        if not email:
            return render(
                request,
                "club/schoolregister.html",
                {
                    "error": "Email address is required.",
                    "form_data": request.POST,
                },
            )

        if not password:
            return render(
                request,
                "club/schoolregister.html",
                {
                    "error": "Password is required.",
                    "form_data": request.POST,
                },
            )

        if len(password) < 8:
            return render(
                request,
                "club/schoolregister.html",
                {
                    "error": "Password must be at least 8 characters long.",
                    "form_data": request.POST,
                },
            )

        if not country:
            return render(
                request,
                "club/schoolregister.html",
                {
                    "error": "Country is required.",
                    "form_data": request.POST,
                },
            )

        if not num_students:
            return render(
                request,
                "club/schoolregister.html",
                {
                    "error": "Number of students is required.",
                    "form_data": request.POST,
                },
            )

        # Validate number of students
        try:
            num_students = int(num_students)

            if num_students < 0:
                raise ValueError

        except (ValueError, TypeError):
            return render(
                request,
                "club/schoolregister.html",
                {
                    "error": "Please enter a valid number of students.",
                    "form_data": request.POST,
                },
            )

        # School type validation
        if not school_types:
            return render(
                request,
                "club/schoolregister.html",
                {
                    "error": "Please select at least one school type.",
                    "form_data": request.POST,
                },
            )

        # ---------------------------------------------------------
        # Check existing school
        # ---------------------------------------------------------

        if User.objects.filter(username__iexact=school_name).exists():
            return render(
                request,
                "club/schoolregister.html",
                {
                    "error": "A school with this name already exists.",
                    "form_data": request.POST,
                },
            )

        # ---------------------------------------------------------
        # Check existing email
        # ---------------------------------------------------------

        if User.objects.filter(email__iexact=email).exists():
            return render(
                request,
                "club/schoolregister.html",
                {
                    "error": "An account with this email address already exists.",
                    "form_data": request.POST,
                },
            )

        # ---------------------------------------------------------
        # Create User + SchoolProfile
        # ---------------------------------------------------------

        try:
            with transaction.atomic():

                # Create Django user
                user = User.objects.create_user(
                    username=school_name,
                    email=email,
                    password=password,
                )

                # Create school profile
                SchoolProfile.objects.create(
                    user=user,
                    school_name=school_name,
                    director_name=director_name,
                    email=email,
                    avatar=avatar,
                    whatsapp_number=whatsapp_number,
                    address=address,
                    nearest_bus_stop=nearest_bus_stop,
                    lga=lga,
                    state=state,
                    country=country,
                    num_students=num_students,
                    school_type=school_type_str,
                )

        except Exception as e:
            return render(
                request,
                "club/schoolregister.html",
                {
                    "error": f"Unable to create school account: {str(e)}",
                    "form_data": request.POST,
                },
            )

        # Registration successful
        return redirect("school_login")

    return render(request, "club/schoolregister.html")


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect


@csrf_protect
def school_login(request):
    if request.method == "POST":
        school_name = request.POST.get("school_name", "").strip()
        password = request.POST.get("password", "")

        # Validate required fields
        if not school_name or not password:
            return render(
                request,
                "club/school_login.html",
                {
                    "error": "School name and password are required.",
                    "school_name": school_name,
                },
            )

        # Authenticate user
        user = authenticate(
            request,
            username=school_name,
            password=password,
        )

        if user is not None:
            # Make sure the account is active
            if not user.is_active:
                return render(
                    request,
                    "club/school_login.html",
                    {
                        "error": "This account is inactive. Please contact the administrator.",
                        "school_name": school_name,
                    },
                )

            login(request, user)

            # Redirect after successful login
            return redirect("home")

        # Authentication failed
        return render(
            request,
            "club/school_login.html",
            {
                "error": "Invalid school name or password.",
                "school_name": school_name,
            },
        )

    return render(request, "club/school_login.html")

def school_dashboard(request):
    if not request.user.is_authenticated:
        return redirect("school_login")

    try:
        profile = request.user.school_profile
    except SchoolProfile.DoesNotExist:
        return redirect("schoolregister")

    return render(request, "club/school_dashboard.html", {
        "profile": profile
    })


def school_logout(request):
    logout(request)
    return redirect("home")

def student_logout(request):
    logout(request)
    return redirect("home")

def admin_logout(request):
    logout(request)
    return redirect("home")

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import Http404
from .models import Book, CartItem


@login_required
def cart_detail(request):
    """Displays all cart items and calculates the total price for the logged-in user."""
    cart_items = CartItem.objects.filter(user=request.user).select_related('book')
    
    # Calculate total safely using a fallback property or callable on CartItem
    cart_total = sum(
        item.get_total_price() if callable(getattr(item, 'get_total_price', None)) else (item.book.price * item.quantity)
        for item in cart_items
    )
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'club/cart.html', context)


# views.py
@login_required
@require_POST
def add_to_cart(request, book_id):
    # Try fetching the book from DB; if it doesn't exist, create it on the fly or fetch/get_or_create
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        # Check if it's one of your static books
        static_data = STATIC_BOOKS.get(int(book_id))
        if static_data:
            # Create the book in DB so CartItem can reference it via Foreign Key
            book = Book.objects.create(
                id=book_id,
                title=static_data.get('title', f'Book #{book_id}'),
                author=static_data.get('author', 'Unknown'),
                description=static_data.get('description', ''),
                price=static_data.get('price', 10.00)
            )
        else:
            raise Http404("Book not found")

    # Safely extract quantity
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1

    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        book=book,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return redirect('cart')

@login_required
@require_POST
def update_cart(request, item_id):
    """Updates item quantity in the cart or removes it if quantity is 0 or less."""
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
        
    return redirect('cart')


@login_required
def remove_from_cart(request, item_id):
    """Removes an item from the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')