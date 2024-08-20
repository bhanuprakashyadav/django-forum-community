
"""
Form Fields: You explicitly define the fields (title and description in this case) that you want to appear on the form. Each field is represented by an instance of a field class (forms.CharField, forms.Textarea, etc.) from Django's form library.
"""
from django import forms
from .models import PostField, ReplyField

class PostForm(forms.ModelForm):
    class Meta:
        model = PostField
        fields = ['post_title', 'description']  # Note: it's 'post_title', not 'title'

class ReplyForm(forms.ModelForm):
    class Meta:
        model = ReplyField
        fields = ['reply_text']