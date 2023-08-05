from django.urls import path, re_path
from blog.views import home_view, details_view

app_name = "blog"

urlpatterns = [
    path("", home_view, name="home"),
    path("blog/<slug>", details_view, name="details"),
]
