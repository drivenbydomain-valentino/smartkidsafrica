from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from . import views


app_name = "club"


urlpatterns = [

    # ========================================================
    # HOME / CORE PAGES
    # ========================================================

    path("", views.home, name="home"),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="club/login.html"
        ),
        name="login",
    ),

    path(
        "about/",
        views.about,
        name="about",
    ),

    path(
        "contact/",
        views.contact_view,
        name="contact",
    ),


    # ========================================================
    # ADMIN
    # ========================================================

    path(
        "admin_login/",
        views.admin_login,
        name="admin_login",
    ),

    path(
        "admin_dashboard/",
        views.admin_dashboard,
        name="admin_dashboard",
    ),

    path(
        "manage_users/",
        views.manage_users,
        name="manage_users",
    ),

    path(
        "manage_posts/",
        views.manage_posts,
        name="manage_posts",
    ),

    path(
        "manage_schools/",
        views.manage_schools,
        name="manage_schools",
    ),

    path(
        "delete_user/<int:user_id>/",
        views.delete_user,
        name="delete_user",
    ),


    # ========================================================
    # STUDENT
    # ========================================================

    path(
        "studentregister/",
        views.studentregister,
        name="studentregister",
    ),

    path(
        "student_login/",
        views.student_login,
        name="student_login",
    ),

    path(
        "student_dashboard/",
        views.student_dashboard,
        name="student_dashboard",
    ),


    # ========================================================
    # PARENT
    # ========================================================

    path(
        "parentregister/",
        views.parentregister,
        name="parentregister",
    ),

    path(
        "parent_login/",
        views.parent_login,
        name="parent_login",
    ),


    # ========================================================
    # TEACHER
    # ========================================================

    path(
        "teacherregister/",
        views.teacherregister,
        name="teacherregister",
    ),

    path(
        "teacher_login/",
        views.teacher_login,
        name="teacher_login",
    ),


    # ========================================================
    # SCHOOL
    # ========================================================

    path(
        "schoolregister/",
        views.schoolregister,
        name="schoolregister",
    ),

    path(
        "school_login/",
        views.school_login,
        name="school_login",
    ),

    path(
        "school_dashboard/",
        views.school_dashboard,
        name="school_dashboard",
    ),


    # ========================================================
    # LOGOUT
    # ========================================================

    path(
        "signout/",
        views.signout,
        name="signout",
    ),

    # Kept for existing templates/links that may still use
    # student_logout
    path(
        "student_logout/",
        views.signout,
        name="student_logout",
    ),

    # Existing school logout
    path(
        "school_logout/",
        views.school_logout,
        name="school_logout",
    ),

    # General logout
    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),


    # ========================================================
    # PROFILE
    # ========================================================

    # Currently logged-in user's profile
    path(
        "profile/",
        views.self_profile_view,
        name="self_profile",
    ),

    # Alternative name kept for existing templates
    path(
        "my-profile/",
        views.self_profile_view,
        name="my_profile",
    ),

    # Specific user's profile
    path(
        "profile/<str:username>/",
        views.profile_view,
        name="profile_view",
    ),


    # ========================================================
    # POSTS / CONTENT
    # ========================================================

    path(
        "newpost/",
        views.newpost,
        name="newpost",
    ),

    path(
        "mypost/",
        views.mypost,
        name="mypost",
    ),

    path(
        "post/<int:post_id>/",
        views.post_detail,
        name="post_detail",
    ),
    path(
        'post/<int:pk>/', 
        views.post_detail, 
        name='post_detail'
    ),

    path(
        "post/<int:post_id>/edit/",
        views.edit_post,
        name="edit_post",
    ),

    path(
        "post/<int:post_id>/delete/",
        views.delete_post,
        name="delete_post",
    ),

    path(
        "post/<int:post_id>/view/",
        views.increment_views,
        name="increment_views",
    ),

    # Existing admin-style delete route kept so older
    # templates/links do not break.
    path(
        "delete_post/<int:post_id>/",
        views.delete_post,
        name="delete_post_legacy",
    ),


    # ========================================================
    # INTERACTIONS
    # ========================================================

    path(
        "like/<int:post_id>/",
        views.like_post,
        name="like_post",
    ),

    path(
        "comment/<int:post_id>/",
        views.add_comment,
        name="add_comment",
    ),

    path(
        "comment/<int:comment_id>/delete/",
        views.delete_comment,
        name="delete_comment",
    ),


    # ========================================================
    # SHARING
    # ========================================================

    # Original share functionality
    path(
        "share/<int:post_id>/",
        views.share_post,
        name="share_post",
    ),

    # Original record-share functionality
    path(
        "record-share/<int:post_id>/",
        views.record_share,
        name="record_share",
    ),

    # Additional share URL functionality retained under
    # separate names to avoid duplicate URL names/routes.
    path(
        "share-url/<int:post_id>/",
        views.get_post_share_url,
        name="get_post_share_url",
    ),

    path(
        "record-post-share/<int:post_id>/",
        views.record_post_share,
        name="record_post_share",
    ),


    # ========================================================
    # SEARCH
    # ========================================================

    path(
        "search/",
        views.search_users,
        name="search_users",
    ),


    # ========================================================
    # EDUCATIONAL SECTIONS
    # ========================================================

    # Book detail using integer ID
    path(
        "books/<int:pk>/",
        views.book_detail,
        name="book_detail",
    ),

    # Book detail using slug
    path(
        "books/<slug:slug>/",
        views.book_detail,
        name="book_detail_slug",
    ),

    path(
        "careers/",
        views.careers,
        name="careers",
    ),

    path(
        "financeliteracy/",
        views.financeliteracy,
        name="financeliteracy",
    ),

    path(
        "financeliteracy/savings/",
        views.savings,
        name="savings",
    ),

    path(
        "financeliteracy/investment/",
        views.investment,
        name="investment",
    ),

    path(
        "stencilbooks/",
        views.stencilbooks,
        name="stencilbooks",
    ),

    path(
        "digitalentrepreneurship/",
        views.digitalentrepreneurship,
        name="digitalentrepreneurship",
    ),

    path(
        "characterbuilding/",
        views.characterbuilding,
        name="characterbuilding",
    ),


    # ========================================================
    # CART / BOOK STORE
    # ========================================================

    path(
        "cart/",
        views.cart_detail,
        name="cart",
    ),

    path(
        "cart/add/<int:book_id>/",
        views.add_to_cart,
        name="add_to_cart",
    ),

    path(
        "cart/update/<int:item_id>/",
        views.update_cart,
        name="update_cart",
    ),

    path(
        "cart/remove/<int:item_id>/",
        views.remove_from_cart,
        name="remove_from_cart",
    ),
    


    # ========================================================
    # MARKETERS / PARTNERS
    # ========================================================

    path(
        "marketers/",
        views.marketer_list,
        name="marketer_list",
    ),

    path(
        "become-a-marketer/",
        views.partner_application,
        name="partner_application",
    ),


    # ========================================================
    # API
    # ========================================================

    path(
        "api/tutor-chat/",
        views.tutor_chat_api,
        name="tutor_chat_api",
    ),
]


# ============================================================
# MEDIA FILES
# DEVELOPMENT ONLY
# ============================================================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
