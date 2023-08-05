from email.policy import default
from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from django_ckeditor_5.fields import CKEditor5Field
from datetime import datetime


class BlogCategory(MPTTModel):
    name = models.CharField(max_length=32, unique=True)
    description = CKEditor5Field("Text", default="", config_name="extends")
    slug = models.SlugField(unique=True, null=True, blank=True)
    parent = TreeForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    date_published = models.DateTimeField(
        auto_now_add=True, verbose_name="date published"
    )
    date_updated = models.DateTimeField(auto_now=True, verbose_name="date updated")

    class MPTTMeta:
        order_insertion_by = ["name"]

    def get_categories(self):
        if self.parent is None:
            return self.name
        else:
            return self.parent.get_categories() + " -> " + self.name

    def __str__(self):
        return self.get_categories()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(BlogCategory, self).save(*args, **kwargs)


def upload_location(instance, filename, **kwargs):
    file_path = f"blog/{str(instance.title)}-{datetime.now().timestamp()}-{filename}"
    return file_path


class Tag(models.Model):
    name = models.CharField(max_length=300, unique=True)
    description = CKEditor5Field("Text", default="", config_name="extends")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="updated at")

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    category = models.ManyToManyField(BlogCategory)
    title = models.CharField(max_length=300, null=False, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    meta_keywords = models.CharField(max_length=255, null=True, blank=True)
    content = CKEditor5Field("Text", default="", config_name="extends")
    image = models.ImageField(upload_to=upload_location, null=False, blank=True)
    date_published = models.DateTimeField(
        auto_now_add=True, verbose_name="date published"
    )
    date_updated = models.DateTimeField(auto_now=True, verbose_name="date updated")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    slug = models.SlugField(blank=True, unique=True)
    is_approved = models.BooleanField(default=False)
    visited = models.IntegerField(default=0)
    related_posts = models.ManyToManyField("self", blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Comment(MPTTModel):
    post = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name="comments"
    )
    name = models.CharField(max_length=50)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    email = models.EmailField()
    content = models.TextField()
    publish = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ["publish"]

    def __str__(self):
        return self.name


@receiver(post_delete, sender=BlogPost)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)


def pre_save_blog_post_receiever(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)


pre_save.connect(pre_save_blog_post_receiever, sender=BlogPost)
