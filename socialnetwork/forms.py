from django import forms


class SignupForm(forms.Form):
    name = forms.CharField(required=False)
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True)
