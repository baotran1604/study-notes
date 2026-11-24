import json

from django.conf import settings
from django.utils.crypto import salted_hmac
from django.db import models


class Note(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField(max_length=6000)
    created = models.DateTimeField(auto_now_add=True)

    receipt = models.CharField(max_length=64, blank=True, default="")

    def make_receipt(self):
        fields = [self.pk, self.owner_id, self.title, self.body]
        payload = json.dumps(fields, ensure_ascii=False)
        return salted_hmac("study-notes.receipt.v1", payload, secret=settings.NOTE_RECEIPT_KEY,
                           algorithm="sha256").hexdigest()


class SessionEvent(models.Model):
    kind = models.CharField(max_length=10, choices=[("login", "Signed in"), ("logout", "Signed out")], default="login")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
