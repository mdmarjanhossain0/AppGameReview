from django import forms

from blog.models import BlogPost

from .models import Comment
from mptt.forms import TreeNodeChoiceField


class CreateBlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ["title", "content", "image"]


class UpdateBlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ["title", "content", "image"]

    def save(self, commit=True):
        blog_post = self.instance
        blog_post.title = self.cleaned_data["title"]
        blog_post.content = self.cleaned_data["content"]

        if self.cleaned_data["image"]:
            blog_post.image = self.cleaned_data["image"]

        if commit:
            blog_post.save()
        return blog_post


class NewCommentForm(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=Comment.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["parent"].widget.attrs.update({"class": "d-none"})
        self.fields["parent"].label = ""
        self.fields["parent"].required = False

    class Meta:
        model = Comment
        fields = ("name", "parent", "email", "content")

        widgets = {
            "name": forms.TextInput(attrs={"class": "col-sm-12"}),
            "email": forms.TextInput(attrs={"class": "col-sm-12"}),
            "content": forms.Textarea(attrs={"class": "form-control"}),
        }

    def save(self, *args, **kwargs):
        Comment.objects.rebuild()
        return super(NewCommentForm, self).save(*args, **kwargs)
