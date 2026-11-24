from django.conf import settings
from django.db import models


class Note(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField(max_length=6000)
    created = models.DateTimeField(auto_now_add=True)


class SessionEvent(models.Model):
    kind = models.CharField(max_length=10, choices=[("login", "Signed in"), ("logout", "Signed out")], default="login")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
