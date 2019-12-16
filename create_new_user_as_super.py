from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserCreateForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
            super(UserCreationForm, self).__init__(*args, **kwargs)
            self.fields['password1'].required = False
            self.fields['password2'].required = False
            # If one field gets autocompleted but not the other, our 'neither
            # password or both password' validation will be triggered.
            self.fields['password1'].widget.attrs['autocomplete'] = 'off'
            self.fields['password2'].widget.attrs['autocomplete'] = 'off'

    def save(self,commit=True):
        user = super(UserCreateForm,self).save(commit=False)
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        if commit:
            user.save()
        return user


class UserAdmin(UserAdmin):
    add_form = UserCreateForm

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','email' ),
        }),
    )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
