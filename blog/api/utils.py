from blog.models import (
	BlogPost,
	BlogCategory,
	Tag
)

from rest_framework.response import Response

from django.utils.text import slugify

ERROR = "Error"

SUCCESS = "Success"


def check_author(function):

	def inner(request, slug):
		try:
			blog_post = BlogPost.objects.get(slug=slug)
		except:
			return Response(data={
				"response" : ERROR,
				"error_message" : "Not found"
			},status=404)
		if request.user == blog_post.author:
			return function(request, blog_post)
		else:
			return Response(data={
				"response" : ERROR,
				"error_message" : "Access denied"
			}, status=400)
	return inner

CATEGORY_ERROR = "Category doesn't exists"
def blog_category_validation(category):
	data = BlogCategory.objects.filter(pk__in=category)
	if len(data) == len(category):
		return True
	else:
		return False

RELATED_POST_ERROR = "Related Post doesn't exists"
def blog_related_post_validation(related_post):
	data = BlogPost.objects.filter(pk__in=related_post)
	if len(data) == len(related_post):
		return True
	else:
		return False



TAG_ERROR = "Tag doesn't exists"
def blog_tag_validation(tag):
	data = Tag.objects.filter(pk__in=tag)
	if len(data) == len(tag):
		return True
	else:
		return False

TITLE_ERROR = "Title already exists"
def blog_title_validation(title):
	if BlogPost.objects.filter(slug=slugify(title)).exists():
		return False
	else:
		return True