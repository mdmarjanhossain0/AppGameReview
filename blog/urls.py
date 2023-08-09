from django.urls import path, re_path
from blog.views import home_view, details_view, privacy_policy_view, contact_us_view

app_name = "blog"

urlpatterns = [
    path("", home_view, name="home"),
    path("article/<slug>", details_view, name="details"),
    path("privacy-policy", privacy_policy_view, name="privacy_policy"),
    path("contact-us", contact_us_view, name="contact_us"),
]
