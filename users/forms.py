from django import forms
from django.contrib.auth.forms import PasswordResetForm,SetPasswordForm
from django.contrib.auth.models import User

# class CustomPasswordResetForm(PasswordResetForm):
#     def get_users(self, email):
#         return User.objects.filter(email__iexact=email, is_active=True)

class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'w-full border px-3 py-2 rounded focus:outline-none focus:ring-2 focus:ring-[#5A827E]',
            'placeholder': 'Enter new password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'w-full border px-3 py-2 rounded focus:outline-none focus:ring-2 focus:ring-[#5A827E]',
            'placeholder': 'Confirm new password'
        })

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'w-full border border-gray-300 p-2 rounded text-sm focus:outline-none focus:ring-2 focus:ring-[#5A827E] focus:border-[#5A827E]',
            'placeholder': 'Enter your email address',
        })
    )
