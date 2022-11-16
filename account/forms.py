from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, ReadOnlyPasswordHashField
from django import forms
from django.urls import reverse_lazy

from account.models import User

FORM_CONTROL = 'form-control '

class RegistrationForm(UserCreationForm):
    """
      Form for Registering new users
    """
    phone_number = forms.CharField(max_length=60, help_text='Required. Add a valid phone_number ')

    class Meta:
        model = User
        fields = ('phone_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        """
          specifying styles to fields
        """
        super(RegistrationForm, self).__init__(*args, **kwargs)
        for field in (
                self.fields['phone_number'], self.fields['password1'], self.fields['password2']):
            field.widget.attrs.update({'class': FORM_CONTROL})


class AccountAuthenticationForm(forms.ModelForm):
    """
      Form for Logging in  users
    """
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone_number', 'password')
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': FORM_CONTROL}),
            'password': forms.TextInput(attrs={'class': FORM_CONTROL}),
        }

    def __init__(self, *args, **kwargs):
        """
          specifying styles to fields
        """
        super(AccountAuthenticationForm, self).__init__(*args, **kwargs)
        for field in (self.fields['phone_number'], self.fields['password']):
            field.widget.attrs.update({'class': FORM_CONTROL})

    def clean(self):
        if self.is_valid():
            phone_number = self.cleaned_data.get('phone_number')
            password = self.cleaned_data.get('password')
            if not authenticate(email=phone_number, password=password):
                raise forms.ValidationError('Invalid Login')


class AccountUpdateForm(forms.ModelForm):
    """
      Updating User Info
    """

    class Meta:
        model = User
        fields = ('phone_number',)
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': FORM_CONTROL}),
            'password': forms.TextInput(attrs={'class': FORM_CONTROL}),
        }

    def __init__(self, *args, **kwargs):
        """
          specifying styles to fields
        """
        super(AccountUpdateForm, self).__init__(*args, **kwargs)
        for field in (self.fields['phone_number'],):
            field.widget.attrs.update({'class': FORM_CONTROL})

    def clean_email(self):
        if self.is_valid():
            phone_number = self.cleaned_data['phone_number']
            try:
                User.objects.exclude(pk=self.instance.pk).get(email=phone_number)
            except User.DoesNotExist:
                return phone_number
            raise forms.ValidationError("phone_number '%s' already in use." % phone_number)


class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone_number',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].help_text = (
                                                "Raw passwords are not stored, so there is no way to see "
                                                "this user's password, but you can <a href=\"%s\"> "
                                                "<strong>Change the Password</strong> using this form</a>."
                                            ) % reverse_lazy('admin:auth_user_password_change', args=[self.instance.id])

    class Meta:
        model = User
        fields = ('phone_number', 'password')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]
