from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.db.models import Q
from django.http import HttpResponse
from blog.forms import CreateBlogPostForm, UpdateBlogPostForm, NewCommentForm
from blog.models import BlogPost, Comment
from account.models import Account
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from operator import attrgetter


BLOG_POSTS_PER_PAGE = 10


def details_view(request, slug):
    data = {}

    print(slug)
    details = get_object_or_404(BlogPost, slug=slug)
    details.visited = details.visited + 1
    details.save()
    related_posts = details.related_posts.all()
    categories = details.category.all()
    suggetions = (
        BlogPost.objects.filter(category__in=categories)
        .exclude(pk=details.pk)
        .distinct()
    )
    previous_post = BlogPost.objects.filter(pk__lt=details.pk).order_by("-pk").first()
    next_post = BlogPost.objects.filter(pk__gt=details.pk).order_by("pk").first()
    data["item"] = details
    data["related_posts"] = related_posts
    data["categories"] = categories
    data["suggetions"] = suggetions[:3]
    data["previous_post"] = previous_post
    data["next_post"] = next_post
    allcomments = details.comments.filter(status=True)
    page = request.GET.get("page", 1)

    paginator = Paginator(allcomments, 10)
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)

    user_comment = None

    if request.method == "POST":
        comment_form = NewCommentForm(request.POST)
        if comment_form.is_valid():
            user_comment = comment_form.save(commit=False)
            user_comment.post = details
            user_comment.save()
            return HttpResponseRedirect("/blog/" + details.slug)
    else:
        comment_form = NewCommentForm()

    {
        "post": details,
        "comments": user_comment,
        "comments": comments,
        "comment_form": comment_form,
        "allcomments": allcomments,
    }
    data["post"] = details
    data["comments"] = user_comment
    data["comments"] = comments
    data["comment_form"] = comment_form
    data["allcomments"] = allcomments

    print("falkdfjsdkl")
    return render(request, "blog/details.html", data)


def get_blog_queryset(query=None):
    queryset = []
    queries = query.split(" ")  # python install 2019 = [python, install, 2019]
    for q in queries:
        posts = BlogPost.objects.filter(
            Q(title__icontains=q) | Q(content__icontains=q), is_approved=True
        ).distinct()

        for post in posts:
            queryset.append(post)

    return list(set(queryset))


def home_view(request):
    context = {}
    query = request.GET.get("query", "")
    blog_posts = sorted(
        get_blog_queryset(query), key=attrgetter("date_published"), reverse=True
    )
    # Pagination
    page = request.GET.get("page", 1)
    blog_posts_paginator = Paginator(blog_posts, BLOG_POSTS_PER_PAGE)

    print(blog_posts)

    try:
        blog_posts = blog_posts_paginator.page(page)
    except PageNotAnInteger:
        blog_posts = blog_posts_paginator.page(BLOG_POSTS_PER_PAGE)
    except EmptyPage:
        blog_posts = blog_posts_paginator.page(blog_posts_paginator.num_pages)

    popular_posts = BlogPost.objects.all().order_by("-visited")[:5]
    context["blog_posts"] = blog_posts
    context["popular_posts"] = popular_posts
    return render(request, "blog/home.html", context=context)


def contact_us_view(request):
    return render(request, "contact_us.html", {})


def privacy_policy_view(request):
    return render(request, "privacy_policy.html", {})
