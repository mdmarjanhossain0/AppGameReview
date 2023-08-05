from rest_framework import status
from rest_framework.response import Response

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter

from django.utils.text import slugify
import ast

from account.models import Account
from blog.models import BlogPost
from blog.api.serializers import *
from blog.api.utils import *
from account.api.utils import just_for_teacher

SUCCESS = "success"
ERROR = "error"
DELETE_SUCCESS = "deleted"
UPDATE_SUCCESS = "updated"
CREATE_SUCCESS = "created"


# Response: https://gist.github.com/mitchtabian/93f287bd1370e7a1ad3c9588b0b22e3d
# Url: https://<your-domain>/api/blog/<slug>/
# Headers: Authorization: Token <token>
@api_view(
    [
        "GET",
    ]
)
@permission_classes((IsAuthenticated,))
@check_author
def api_detail_blog_view(request, slug):
    if request.method == "GET":
        serializer = BlogPostSerializer(slug)
        return Response(serializer.data)


# Response: https://gist.github.com/mitchtabian/32507e93c530aa5949bc08d795ba66df
# Url: https://<your-domain>/api/blog/<slug>/update
# Headers: Authorization: Token <token>
@api_view(
    [
        "PUT",
    ]
)
@permission_classes((IsAuthenticated,))
@check_author
def api_update_blog_view(
    request, slug
):  # for check decoretor slug convert to blog_post object
    if request.method == "PUT":
        data = request.data.copy().dict()
        category = ast.literal_eval(data.get("category", "[]"))
        data["category"] = category
        tags = ast.literal_eval(data.get("tags", "[]"))
        data["tags"] = tags
        related_posts = ast.literal_eval(data.get("related_posts", "[]"))
        data["related_posts"] = related_posts
        data["old_title"] = data.get("title", None)
        data["author"] = request.user.pk
        serializer = BlogPostUpdateSerializer(slug, data=data, partial=True)
        data = {}
        if serializer.is_valid():
            blog_post = serializer.save()
            data = BlogPostSerializer(blog_post).data
            data["response"] = SUCCESS
            data["error_message"] = ""
            return Response(data=data)

            return Response(data=data)
        else:
            response = {}
            response["response"] = ERROR
            response["error_message"] = serializer.errors
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


@api_view(
    [
        "GET",
    ]
)
@permission_classes((IsAuthenticated,))
def api_is_author_of_blogpost(request, slug):
    try:
        blog_post = BlogPost.objects.get(slug=slug)
    except BlogPost.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    data = {}
    user = request.user
    if blog_post.author != user:
        data["response"] = "You don't have permission to edit that."
        return Response(data=data)
    data["response"] = "You have permission to edit that."
    return Response(data=data)


# Response: https://gist.github.com/mitchtabian/a97be3f8b71c75d588e23b414898ae5c
# Url: https://<your-domain>/api/blog/<slug>/delete
# Headers: Authorization: Token <token>
@api_view(
    [
        "DELETE",
    ]
)
@permission_classes((IsAuthenticated,))
@check_author
def api_delete_blog_view(request, slug):
    if request.method == "DELETE":
        operation = slug.delete()
        data = {}
        if operation:
            data["response"] = DELETE_SUCCESS
        return Response(data=data)


# Response: https://gist.github.com/mitchtabian/78d7dcbeab4135c055ff6422238a31f9
# Url: https://<your-domain>/api/blog/create
# Headers: Authorization: Token <token>
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@just_for_teacher
def api_create_blog_view(request):
    if request.method == "POST":
        data = request.data.copy().dict()

        category = ast.literal_eval(data.get("category", "[]"))
        data["category"] = category
        tags = ast.literal_eval(data.get("tags", "[]"))
        data["tags"] = tags
        related_posts = ast.literal_eval(data.get("related_posts", "[]"))
        data["related_posts"] = related_posts
        data["author"] = request.user.pk
        serializer = BlogPostCreateSerializer(data=data)

        if serializer.is_valid():
            blog_post = serializer.save()
            data = BlogPostSerializer(blog_post).data
            data["response"] = SUCCESS
            data["error_message"] = ""
            return Response(data=data)
        else:
            response = {}
            response["response"] = ERROR
            response["error_message"] = serializer.errors
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


# Response: https://gist.github.com/mitchtabian/ae03573737067c9269701ea662460205
# Url:
# 		1) list: https://<your-domain>/api/blog/list
# 		2) pagination: http://<your-domain>/api/blog/list?page=2
# 		3) search: http://<your-domain>/api/blog/list?search=mitch
# 		4) ordering: http://<your-domain>/api/blog/list?ordering=-date_updated
# 		4) search + pagination + ordering: <your-domain>/api/blog/list?search=mitch&page=2&ordering=-date_updated
# Headers: Authorization: Token <token>
class ApiBlogListView(ListAPIView):
    serializer_class = BlogPostSerializer
    authentication_classes = (
        TokenAuthentication,
        SessionAuthentication,
    )
    permission_classes = ()
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ("title", "content", "author__username")

    def get_queryset(self):
        return BlogPost.objects.filter(author=self.request.user).order_by("-pk")


class CategoryApiListView(ListAPIView):
    queryset = BlogCategory.objects.root_nodes()
    serializer_class = CategorySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = ()
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
