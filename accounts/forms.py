from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'name@example.com',
            'class': 'w-full px-3.5 py-2.5 rounded border border-stone-300 dark:border-stone-700 bg-white dark:bg-stone-900 text-stone-900 dark:text-stone-100 placeholder-stone-400 dark:placeholder-stone-500 focus:outline-none focus:ring-1 focus:ring-stone-900 dark:focus:ring-stone-400 font-sans text-sm transition-colors'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_input_classes = 'w-full px-3.5 py-2.5 rounded border border-stone-300 dark:border-stone-700 bg-white dark:bg-stone-900 text-stone-900 dark:text-stone-100 placeholder-stone-400 dark:placeholder-stone-500 focus:outline-none focus:ring-1 focus:ring-stone-900 dark:focus:ring-stone-400 font-sans text-sm transition-colors'
        
        if 'username' in self.fields:
            self.fields['username'].widget.attrs.update({
                'class': base_input_classes,
                'placeholder': 'reader_name'
            })
            self.fields['username'].help_text = "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        if 'password_1' in self.fields:
            self.fields['password_1'].widget.attrs.update({
                'class': base_input_classes,
                'placeholder': '••••••••'
            })
        elif 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({
                'class': base_input_classes,
                'placeholder': '••••••••'
            })
        if 'password_2' in self.fields:
            self.fields['password_2'].widget.attrs.update({
                'class': base_input_classes,
                'placeholder': '••••••••'
            })
        elif 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({
                'class': base_input_classes,
                'placeholder': '••••••••'
            })


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Your username',
            'class': 'w-full px-3.5 py-2.5 rounded border border-stone-300 dark:border-stone-700 bg-white dark:bg-stone-900 text-stone-900 dark:text-stone-100 placeholder-stone-400 dark:placeholder-stone-500 focus:outline-none focus:ring-1 focus:ring-stone-900 dark:focus:ring-stone-400 font-sans text-sm transition-colors'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'class': 'w-full px-3.5 py-2.5 rounded border border-stone-300 dark:border-stone-700 bg-white dark:bg-stone-900 text-stone-900 dark:text-stone-100 placeholder-stone-400 dark:placeholder-stone-500 focus:outline-none focus:ring-1 focus:ring-stone-900 dark:focus:ring-stone-400 font-sans text-sm transition-colors'
        })
    )
