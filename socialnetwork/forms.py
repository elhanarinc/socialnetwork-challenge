from django import forms


class SignupForm(forms.Form):
    name = forms.CharField(required=False)
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True)


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True)


class PostForm(forms.Form):
    content = forms.CharField(required=True)


class LikeAndDislikeForm(forms.Form):
    post_id = forms.CharField(required=True)
    max_count = forms.IntegerField(required=False)


class RandomPostForm(forms.Form):
    user_id = forms.CharField(required=True)
