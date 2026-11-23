from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('full_name', 'bio')
        widgets = {
            'full_name': forms.TextInput(
                attrs={'class': 'field', 'placeholder': 'Your full name'}
            ),
            'bio': forms.Textarea(
                attrs={
                    'class': 'field',
                    'rows': 5,
                    'placeholder': 'Tell readers a little about yourself',
                }
            ),
        }
