from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import identify_hasher
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import NoteForm
from .models import Note, SignIn


@require_http_methods(["GET", "POST"])
def register(request):
    form = UserCreationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        # The form applies the configured password validators and hashes on save.
        form.save()
        return redirect("login")
    return render(request, "notes/register.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def notebook(request):
    form = NoteForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        note = form.save(commit=False)
        note.owner = request.user
        note.save()
        return redirect("note", pk=note.pk)
    query = request.GET.get("q", "")
    notes = Note.objects.filter(owner=request.user).order_by("-created", "-pk")
    if query:
        # The ORM binds the title search as a query parameter.
        notes = notes.filter(title__icontains=query)
    return render(request, "notes/notebook.html", {"form": form, "notes": notes, "q": query})


@login_required
def note(request, pk):
    entry = get_object_or_404(Note, pk=pk, owner=request.user)
    return render(request, "notes/note.html", {"note": entry})


@login_required
def account(request):
    hasher = identify_hasher(request.user.password)
    return render(request, "notes/account.html", {"algorithm": hasher.algorithm})


@login_required
def activity(request):
    events = SignIn.objects.filter(user=request.user).order_by("-created", "-pk")[:20]
    return render(request, "notes/activity.html", {"events": events})
