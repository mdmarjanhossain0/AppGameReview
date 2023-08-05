from rest_framework import serializers
from blog.models import BlogPost

import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from rest_framework_recursive.fields import RecursiveField

IMAGE_SIZE_MAX_BYTES = 1024 * 1024 * 2  # 2MB
MIN_TITLE_LENGTH = 5
MIN_content_LENGTH = 50

from blog.utils import is_image_aspect_ratio_valid, is_image_size_valid
from blog.api.utils import *


class BlogPostSerializer(serializers.ModelSerializer):
    # username = serializers.SerializerMethodField('get_username_from_author')
    # image 	 = serializers.SerializerMethodField('validate_image_url')

    class Meta:
        model = BlogPost
        # fields = ['pk', 'title', 'slug', 'content', 'image', 'date_updated', 'username']
        fields = "__all__"

        depth = 1

    def get_username_from_author(self, blog_post):
        username = blog_post.author.username
        return username

    def validate_image_url(self, blog_post):
        image = blog_post.image
        new_url = image.url
        if "?" in new_url:
            new_url = image.url[: image.url.rfind("?")]
        return new_url


class BlogPostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = [
            "category",
            "title",
            "content",
            "image",
            "author",
            "related_posts",
            "tags",
        ]

    def to_internal_value(self, data):
        response = {}
        e = False

        # print(self.context.get("title", None))

        # print(self.validated_data["title"])

        category = data.get("category", None)
        if category and blog_category_validation(data["category"]):
            response["category_status"] = ""
        else:
            e = True
            if category:
                response["category_status"] = CATEGORY_ERROR
            else:
                response["category_status"] = "Required Field"

        related_posts = data.get("related_posts", None)
        if not related_posts or blog_related_post_validation(related_posts):
            response["related_posts_status"] = ""
        else:
            e = True
            response["related_posts_status"] = RELATED_POST_ERROR

        tags = data.get("tags", None)
        if not tags or blog_tag_validation(tags):
            response["tags_status"] = ""
        else:
            e = True
            response["tags_status"] = TAG_ERROR

        title = data.get("title", None)
        if title:
            if (data.get("old_title", None) == title) or blog_title_validation(title):
                response["title_status"] = ""
            else:
                e = True
                response["title_status"] = TITLE_ERROR
        else:
            e = True
            response["title_status"] = "Required Field"
        content = data.get("content", None)
        if content:
            response["content_status"] = ""
        else:
            e = True
            response["content_status"] = "Required Field"

        if e:
            raise serializers.ValidationError(response)
        print(response)
        return super(BlogPostUpdateSerializer, self).to_internal_value(data)

    def update(self, instance, validated_data):
        print(instance)
        instance.title = validated_data.get("title", instance.title)
        instance.content = validated_data.get("content", instance.content)
        instance.image = validated_data.get("image", instance.image)

        instance.category.clear()
        for item in validated_data.get("category", instance.category.all()):
            instance.category.add(item.pk)

        instance.related_posts.clear()
        for item in validated_data.get("related_posts", instance.related_posts.all()):
            instance.related_posts.add(item.pk)

        instance.tags.clear()
        for item in validated_data.get("tags", instance.tags.all()):
            instance.tags.add(item.pk)
        # instance.related_posts = validated_data.get("related_posts", instance.related_posts)
        # instance.tags = validated_data.get("tags", instance.tags)
        return instance

    # def validate(self, blog_post):
    # 	try:
    # 		title = blog_post['title']
    # 		if len(title) < MIN_TITLE_LENGTH:
    # 			raise serializers.ValidationError({"response": "Enter a title longer than " + str(MIN_TITLE_LENGTH) + " characters."})

    # 		content = blog_post['content']
    # 		if len(content) < MIN_content_LENGTH:
    # 			raise serializers.ValidationError({"response": "Enter a content longer than " + str(MIN_content_LENGTH) + " characters."})

    # 		image = blog_post['image']
    # 		url = os.path.join(settings.TEMP , str(image))
    # 		storage = FileSystemStorage(location=url)

    # 		with storage.open('', 'wb+') as destination:
    # 			for chunk in image.chunks():
    # 				destination.write(chunk)
    # 			destination.close()

    # 		# Check image size
    # 		if not is_image_size_valid(url, IMAGE_SIZE_MAX_BYTES):
    # 			os.remove(url)
    # 			raise serializers.ValidationError({"response": "That image is too large. Images must be less than 2 MB. Try a different image."})

    # 		# Check image aspect ratio
    # 		if not is_image_aspect_ratio_valid(url):
    # 			os.remove(url)
    # 			raise serializers.ValidationError({"response": "Image height must not exceed image width. Try a different image."})

    # 		os.remove(url)
    # 	except KeyError:
    # 		pass
    # 	return blog_post


class BlogPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = [
            "category",
            "title",
            "content",
            "image",
            "author",
            "related_posts",
            "tags",
        ]

    def to_internal_value(self, data):
        response = {}
        e = False

        category = data.get("category", None)
        if category and blog_category_validation(data["category"]):
            response["category_status"] = ""
        else:
            e = True
            if category:
                response["category_status"] = CATEGORY_ERROR
            else:
                response["category_status"] = "Required Field"

        related_posts = data.get("related_posts", None)
        if not related_posts or blog_related_post_validation(related_posts):
            response["related_posts_status"] = ""
        else:
            e = True
            response["related_posts_status"] = RELATED_POST_ERROR

        tags = data.get("tags", None)
        if not tags or blog_tag_validation(tags):
            response["tags_status"] = ""
        else:
            e = True
            response["tags_status"] = TAG_ERROR

        title = data.get("title", None)
        if title and blog_title_validation(title):
            response["title_status"] = ""
        else:
            e = True
            if title:
                response["title_status"] = TITLE_ERROR
            else:
                response["title_status"] = "Required Field"
        content = data.get("content", None)
        if content:
            response["content_status"] = ""
        else:
            e = True
            response["content_status"] = "Required Field"

        if e:
            raise serializers.ValidationError(response)
        print(response)
        return super(BlogPostCreateSerializer, self).to_internal_value(data)

    # def save(self):

    # 	try:
    # 		image = self.validated_data['image']
    # 		title = self.validated_data['title']
    # 		if len(title) < MIN_TITLE_LENGTH:
    # 			raise serializers.ValidationError({"response": "Enter a title longer than " + str(MIN_TITLE_LENGTH) + " characters."})

    # 		content = self.validated_data['content']
    # 		if len(content) < MIN_content_LENGTH:
    # 			raise serializers.ValidationError({"response": "Enter a content longer than " + str(MIN_content_LENGTH) + " characters."})

    # 		blog_post = BlogPost(
    # 							author=self.validated_data['author'],
    # 							title=title,
    # 							content=content,
    # 							image=image,
    # 							)

    # 		url = os.path.join(settings.TEMP , str(image))
    # 		storage = FileSystemStorage(location=url)

    # 		with storage.open('', 'wb+') as destination:
    # 			for chunk in image.chunks():
    # 				destination.write(chunk)
    # 			destination.close()

    # 		# Check image size
    # 		if not is_image_size_valid(url, IMAGE_SIZE_MAX_BYTES):
    # 			os.remove(url)
    # 			raise serializers.ValidationError({"response": "That image is too large. Images must be less than 2 MB. Try a different image."})

    # 		# Check image aspect ratio
    # 		if not is_image_aspect_ratio_valid(url):
    # 			os.remove(url)
    # 			raise serializers.ValidationError({"response": "Image height must not exceed image width. Try a different image."})

    # 		os.remove(url)
    # 		blog_post.save()
    # 		return blog_post
    # 	except KeyError:
    # 		raise serializers.ValidationError({"response": "You must have a title, some content, and an image."})


class CategorySerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True)

    class Meta:
        model = BlogCategory
        fields = ["id", "name", "description", "slug", "children"]
