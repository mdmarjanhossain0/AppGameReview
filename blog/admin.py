from django.contrib import admin

from blog.models import BlogPost, BlogCategory, Tag, Comment

admin.site.register(BlogPost)
admin.site.register(BlogCategory)
admin.site.register(Tag)

admin.site.register(Comment)
