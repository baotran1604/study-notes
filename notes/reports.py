from hashlib import sha256
from importlib import metadata
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render


@login_required
def inventory(request):
    if not request.user.is_staff:
        raise PermissionDenied

    packages = [metadata.distribution("Django")]
    # Fix 1: use the installed environment, including indirect dependencies.
    # packages = list(metadata.distributions())

    rows = sorted((p.metadata["Name"], p.version) for p in packages)
    return render(request, "notes/inventory.html", {"rows": rows})


GUIDE_FOLDER = Path(__file__).with_name("guides")
# Release checksums are recorded when the guide is approved for publication.
CHECKSUMS = {
    "reading-plan.txt": "708e948e1fbddaaf1cb4e58e84ca7bf802bb396e0d64bff6167a0bc097f218a6",
    # Fix 3: include the approved weekly review in the release manifest.
    # "weekly-review.txt": "35ea340886df0f35eb17cf5e9fabc1925cedb3188aa0113db8f85af605ceb3db",
}


@login_required
def guides(request):
    guides = []
    for path in sorted(GUIDE_FOLDER.glob("*.txt")):
        data = path.read_bytes()
        expected = CHECKSUMS.get(path.name)
        body = ""
        if expected is None:
            status = "Unavailable. The release has no checksum for this guide."
        elif sha256(data).hexdigest() != expected:
            status = "Unavailable. The file differs from the approved release."
        else:
            status = "Release checksum verified."
            body = data.decode("utf-8")
        guides.append({"name": path.stem.replace("-", " ").title(), "status": status, "body": body})
    return render(request, "notes/guides.html", {"guides": guides})
