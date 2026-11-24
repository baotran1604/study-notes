from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from notes import reports, views

urlpatterns = [
    path("", views.notebook, name="notebook"),
    path("notes/<int:pk>/", views.note, name="note"),
    path("register/", views.register, name="register"),
    path("login/", LoginView.as_view(template_name="notes/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("staff/packages/", reports.inventory, name="inventory"),
    path("guides/", reports.guides, name="guides"),
    path("account/", views.account, name="account"),
    path("activity/", views.activity, name="activity"),
]
