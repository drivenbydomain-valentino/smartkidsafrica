from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views



from . import views

urlpatterns = [
    # urls.py

    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('manage_posts/', views.manage_posts, name='manage_posts'),
    path('manage_schools/', views.manage_schools, name='manage_schools'),

    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    # AUTH
    path('studentregister/', views.studentregister, name='studentregister'),
    path('student_login/', views.student_login, name='student_login'),
    path('school_login/', views.school_login, name='school_login'),
    path("student_dashboard/", views.student_dashboard, name="student_dashboard"),
    path('schoolregister/', views.schoolregister, name='schoolregister'),
    path('signout/', views.signout, name='signout'),
    path('student_logout/', views.signout, name='student_logout'),
    path("school_dashboard/", views.school_dashboard, name="school_dashboard"),
    path("logout/", views.school_logout, name="school_logout"),

    # CORE PAGES
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='club/login.html'), name='login'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # CONTENT
    path('newpost/', views.newpost, name='newpost'),
    path('mypost/', views.mypost, name='mypost'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.view_profile, name='view_profile'),

    # EDUCATIONAL SECTIONS
    path('books/', views.books, name='books'),
    path('books/<str:slug>/', views.book_detail, name='book_detail'),
    # path('books/<int:pk>/', views.book_detail, name='book_detail'),  # <--- Add this pattern
    # path('add_to_cart/<int:id>/', views.add_to_cart, name='add_to_cart'),

    path('careers/', views.careers, name='careers'),
    path('financeliteracy/savings/', views.savings, name='savings'),
    path('financeliteracy/investment/', views.investment, name='investment'),
    path('financeliteracy/', views.financeliteracy, name='financeliteracy'),
    path('careers/digitalentrepreneurship/', views.digitalentrepreneurship, name='digitalentrepreneurship'),
    path('characterbuilding/', views.characterbuilding, name='characterbuilding'),

    # POSTS
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/view/', views.increment_views, name='increment_views'),

    # INTERACTIONS
    path("like/<int:post_id>/", views.like_post, name="like_post"),
    path("comment/<int:post_id>/", views.add_comment, name="add_comment"),
    path("share/<int:post_id>/", views.share_post, name="share_post"),

    # COMMENTS
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    # SEARCH
    path('search/', views.search_users, name='search_users'),

    # CHAT
    # path('chat/', views.chat_home, name='chat_home'),
    # path('chat/start/<str:username>/', views.start_chat, name='start_chat'),
    # path('chat/<int:convo_id>/messages/', views.get_messages, name='get_messages'),
    # path('chat/<int:convo_id>/send/', views.send_message, name='send_message'),

    # path('cart/', views.cart_detail, name='cart_detail'),
    # path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    # path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    # path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('cart/', views.cart_detail, name='cart'),
    path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
]

# MEDIA FILES (development only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)