from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.crypto import constant_time_compare
from django.contrib.auth.hashers import identify_hasher
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import NoteForm, RegistrationForm
from .models import Note, SessionEvent


@require_http_methods(["GET", "POST"])
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegistrationForm()

    return render(request, "notes/register.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def notebook(request):
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            # Fill in the owner before writing the note to the database.
            note = form.save(commit=False)
            note.owner = request.user
            with transaction.atomic():
                note.save()
                note.receipt = note.make_receipt()
                note.save(update_fields=["receipt"])
            return redirect("note", pk=note.pk)
    else:
        form = NoteForm()

    query = request.GET.get("q", "")
    notes = Note.objects.filter(owner=request.user).order_by("-created", "-pk")
    if query:
        # The ORM binds the title search as a query parameter.
        notes = notes.filter(title__icontains=query)
    return render(request, "notes/notebook.html", {"form": form, "notes": notes, "q": query})


@login_required
def note(request, pk):
    entry = get_object_or_404(Note, pk=pk, owner=request.user)
    if not entry.receipt:
        status = "This note predates save receipts."
    elif constant_time_compare(entry.make_receipt(), entry.receipt):
        status = "Verified. The saved note matches its receipt."
    else:
        status = "Verification failed. The saved note could not be authenticated."
    return render(request, "notes/note.html", {"note": entry, "status": status})


@login_required
def account(request):
    hasher = identify_hasher(request.user.password)
    return render(request, "notes/account.html", {"algorithm": hasher.algorithm})


@login_required
def activity(request):
    events = SessionEvent.objects.filter(user=request.user).order_by("-created", "-pk")[:20]
    return render(request, "notes/activity.html", {"events": events})
