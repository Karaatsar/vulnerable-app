from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("posts/new/", views.create_post, name="create_post"),
    path("posts/<int:post_id>/delete/", views.delete_post, name="delete_post"),
    path("private_note/", views.private_note, name="private_note"),
]
