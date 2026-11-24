import logging

from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver

from .models import SignIn

log = logging.getLogger("notes.security")


@receiver(user_logged_in)
def record_sign_in(sender, user, **kwargs):
    SignIn.objects.create(user=user)


@receiver(user_login_failed)
def record_failed_sign_in(sender, **kwargs):
    # Keep submitted credentials out of the server log.
    log.warning("Sign-in rejected")
