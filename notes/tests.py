from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, identify_hasher
from django.test import TestCase
from django.urls import reverse

from .models import Note, SessionEvent

User = get_user_model()


class NotebookTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create_user("reader")
        cls.other = User.objects.create_user("other")
        cls.private = Note.objects.create(owner=cls.other, title="Private draft", body="Private body")

    def test_private_notes(self):
        address = reverse("note", args=[self.private.pk])
        self.assertRedirects(self.client.get(address), "/login/?next=" + address)
        self.client.force_login(self.reader)
        self.assertEqual(self.client.get(address).status_code, 404)
        self.assertNotContains(self.client.get("/"), self.private.title)
        self.client.force_login(self.other)
        self.assertContains(self.client.get(address), self.private.body)

    def test_save_and_search(self):
        self.client.force_login(self.reader)
        title = "Today's 100% review"
        response = self.client.post("/", {"title": title, "body": "Read chapter two"}, follow=True)
        self.assertContains(response, "Read chapter two")
        Note.objects.create(owner=self.reader, title="Another review", body="Other text")
        response = self.client.get("/", {"q": "'s 100%"})
        self.assertEqual([n.title for n in response.context["notes"]], [title])
        self.assertFalse(self.client.get("/", {"q": "Private"}).context["notes"].exists())

    def test_password_storage_and_sign_in(self):
        password = "Maple paper notebook 761"
        for name in ["first_student", "second_student"]:
            response = self.client.post("/register/", {
                "username": name, "password1": password, "password2": password,
            })
            self.assertRedirects(response, "/login/")
        first = User.objects.get(username="first_student")
        second = User.objects.get(username="second_student")
        self.assertEqual(identify_hasher(first.password).algorithm, "pbkdf2_sha256")
        self.assertNotIn(password, first.password)
        self.assertNotEqual(first.password, second.password)
        self.assertTrue(check_password(password, first.password))
        self.assertRedirects(self.client.post("/login/", {
            "username": first.username, "password": password,
        }), "/")
        self.assertContains(self.client.get("/account/"), "pbkdf2_sha256")
        self.assertEqual(SessionEvent.objects.filter(user=first, kind="login").count(), 1)
        self.assertRedirects(self.client.post("/logout/"), "/login/")

    def test_common_password_rejected(self):
        response = self.client.post("/register/", {
            "username": "new_student", "password1": "password", "password2": "password",
        })
        self.assertContains(response, "This password is too common")
        self.assertFalse(User.objects.filter(username="new_student").exists())

    def test_sign_in_monitoring(self):
        self.client.force_login(self.other)
        self.client.force_login(self.reader)
        events = self.client.get("/activity/").context["events"]
        self.assertEqual([e.user_id for e in events], [self.reader.pk])
        self.client.logout()
        with self.assertLogs("notes.security", level="WARNING") as captured:
            self.client.post("/login/", {"username": "reader", "password": "test-input"})
        self.assertEqual([record.getMessage() for record in captured.records], ["Sign-in rejected"])

    def test_staff_inventory(self):
        self.client.force_login(self.reader)
        self.assertEqual(self.client.get("/staff/packages/").status_code, 403)
        self.reader.is_staff = True
        self.reader.save()
        self.assertContains(self.client.get("/staff/packages/"), "Django")

    def test_saved_receipt_and_older_note(self):
        self.client.force_login(self.other)
        self.assertContains(self.client.get(reverse("note", args=[self.private.pk])), "predates save receipts")
        response = self.client.post("/", {"title": "Week one", "body": "Read two pages."}, follow=True)
        self.assertContains(response, "matches its receipt")
        address = response.redirect_chain[-1][0]
        with self.settings(NOTE_RECEIPT_KEY="different-test-key"):
            self.assertContains(self.client.get(address), "Verification failed")
        self.assertContains(self.client.get(address), "matches its receipt")

    def test_guide_integrity(self):
        from unittest.mock import patch
        from .reports import CHECKSUMS

        self.client.force_login(self.reader)
        self.assertContains(self.client.get("/guides/"), "Before you start a chapter")
        with patch.dict(CHECKSUMS, {"reading-plan.txt": "unexpected digest"}):
            response = self.client.get("/guides/")
            self.assertContains(response, "differs from the approved release")
            self.assertNotContains(response, "Before you start a chapter")
