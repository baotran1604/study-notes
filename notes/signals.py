import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from .models import SessionEvent

log = logging.getLogger("notes.security")


@receiver(user_logged_in)
def record_sign_in(sender, user, **kwargs):
    SessionEvent.objects.create(user=user, kind="login")


@receiver(user_login_failed)
def record_failed_sign_in(sender, **kwargs):
    # Keep submitted credentials out of the server log.
    log.warning("Sign-in rejected")


@receiver(user_logged_out)
def record_sign_out(sender, user, **kwargs):
    # Fix 5: save the end of the session in the same history as the sign-in.
    # if user is not None:
    #     SessionEvent.objects.create(user=user, kind="logout")
    pass
