from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return self.title

class PrivateNote(models.Model):
    user =  models.OneToOneField(User, on_delete=models.CASCADE)
    note =  models.TextField()

    def __str__(self):
        return f"Private message for {self.user.username}"