
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .models import Post, PrivateNote

from cryptography.fernet import Fernet
from django.conf import settings


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
        # tässä kohtaa on haavoittuvuus (flaw1, broken access control), jossa ei tarkisteta
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
#uusi ominaisuuden lisääminen yksityisviestien tallentamiseen
def private_note(request):
    if not request.user.is_authenticated:
        return redirect("login")

    note, created = PrivateNote.objects.get_or_create(
        user=request.user, 
        defaults={"note": ""}
        )
    
    cipher = Fernet(settings.PRIVATE_NOTE_KEY.encode())

    if request.method == "POST":
        new_note = request.POST.get("note")
        #tässä kohtaa haavoittuvuus (flaw2, broken cryptography), jossa
        #yksityisviesti plaintekstinä tallennetaan tietokantaan, vaikka se pitäisi salata
        #note.note = new_note
        # note.save()
        # KORJATAAN: salataan yksityisviesti ennen tallentamista
        note.note = cipher.encrypt(new_note.encode()).decode()
        note.save()
        return redirect("private_note")
    if note.note:
        # KORJATAAN: puretaan salaus ennen näyttämistä
        decrypted_note = cipher.decrypt(note.note.encode()).decode()
    else:
        decrypted_note = ""
    
    return render(
        request,
        "forum/private_note.html",
        {"note": decrypted_note},
    )

def search_posts(request):
    query = request.GET.get("q", "")
    # tässä kohtaa on haavoittuvuus (flaw3, SQL injection),
    # käyttäjän syöttämä hakuparametri liitetään suoraan SQL-lauseeseen ilman asianmukaista parametrisoitua kyselyä
    # posts =[]
    # if query:
    # with connection.cursor() as cursor:   
            # sql= f"""
            #     SELECT id, author_id, title, content, created_at
            #     FROM forum_post
            #     WHERE title LIKE %{query}% OR content LIKE %{query}%
            # """
            # cursor.execute(sql)
            # rows = cursor.fetchall()
            # KORJATAAN: django ORM:n avulla parametrisoidulla kyselyllä, jotta SQL-injektio estetään
    if query:
        posts = Post.objects.filter(
            title__icontains=query
            ) | Post.objects.filter(
                content__icontains=query
            )
    else:
        posts = Post.objects.none()

    return render(
        request, 
        "forum/search.html",
        {"posts": posts, "query": query}
    )