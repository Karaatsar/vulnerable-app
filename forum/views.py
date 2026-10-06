
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .models import Post


def home(request):
    posts = Post.objects.all().order_by("-created_at")

    return render(
        request,
        "forum/home.html",
        {"posts": posts},
    )


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(
                request,
                "forum/register.html",
                {"error": "Username already exists."},
            )

        user = User.objects.create_user(
            username=username,
            password=password,
        )

        login(request, user)

        return redirect("home")

    return render(request, "forum/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)
            return redirect("home")

        return render(
            request,
            "forum/login.html",
            {"error": "Invalid username or password."},
        )

    return render(request, "forum/login.html")


def logout_view(request):
    logout(request)

    return redirect("home")


def create_post(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        Post.objects.create(
            author=request.user,
            title=title,
            content=content,
        )

        return redirect("home")

    return render(request, "forum/create_post.html")


def delete_post(request, post_id):
    if not request.user.is_authenticated:
        return redirect("login")

    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        # tässä kohtaa on haavoittuvuus, jossa ei tarkisteta
        # onko kirjautunut käyttäjä postauksen tekijä
        # post.delete()
        #vain kirjoittanut käyttäjä voi poistaa oman postauksen
        if post.author!=request.user:
            return redirect("home")
        post.delete()

        return redirect("home")

    return render(
        request,
        "forum/delete_post.html",
        {"post": post},
    )