from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Pin, Board, Comment


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class PinForm(forms.ModelForm):
    class Meta:
        model = Pin
        fields = ['title', 'description', 'image', 'link', 'category', 'board']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['board'].queryset = Board.objects.filter(owner=user)
        self.fields['board'].required = False


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['name']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={'placeholder': 'Add a comment...'})
        }
