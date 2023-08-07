from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap

from account.views import (
    registration_view,
    logout_view,
    login_view,
    account_view,
    must_authenticate_view,
    robots_txt,
)

from blog.sitemaps import BlogPostSitemap

sitemaps = {
    "blog": BlogPostSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("account/", account_view, name="account"),
    path("", include("blog.urls", "blog")),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("must_authenticate/", must_authenticate_view, name="must_authenticate"),
    path("register/", registration_view, name="register"),
    # REST-framework
    path("api/blog/", include("blog.api.urls", "blog_api")),
    path("api/account/", include("account.api.urls", "account_api")),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    # path("privacy-policy", privacy_policy_view, name="privacy_policy"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("robots.txt", robots_txt, name="robotstext"),
    # Password reset links (ref: https://github.com/django/django/blob/master/django/contrib/auth/views.py)
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change.html"
        ),
        name="password_change",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
