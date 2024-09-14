from django import forms
from django.contrib.auth.models import User
from .models import Feedback


class MyLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2


class BookSearchForm(forms.Form):
    title = forms.CharField(required=False, label='Title', max_length=100)
    author = forms.CharField(required=False, label='Author', max_length=100)
    genre = forms.CharField(required=False, label='Genre', max_length=50)


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 14, 'placeholder': 'Enter your feedback'}),
        }
        labels = {
            'feedback': 'Your Feedback',
        }
