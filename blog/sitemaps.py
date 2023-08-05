from django.contrib.sitemaps import Sitemap

from .models import BlogPost


class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9
    protocol = "https"

    def items(self):
        return BlogPost.objects.filter(is_approved=True)

    # will return the last time an article was updated
    def lastmod(self, obj):
        return obj.date_updated

    # returns the URL of the article object
    def location(self, obj):
        return f"/blog/{obj.slug}"
