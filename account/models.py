import uuid

from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from config.utils.models import Entity


class CustomUserManager(UserManager):
    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})

    def create_user(self, first_name, last_name,address1 ,phone_number, password=None):
        if not phone_number:
            raise ValueError('user must have phone_number')

        user = self.model(
            phone_number=self.normalize_email(phone_number),
        )
        user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.address1 = address1
        user.save()
        return user

        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password):
        if not phone_number:
            raise ValueError('user must have phone_number')

        user = self.model(
            phone_number=self.normalize_email(phone_number),
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
from django.core.validators import RegexValidator
phone_validator = RegexValidator(r"^(((?:\+|00)964)|(0)*)7\d{9}$", "The phone number provided is invalid")
class User(AbstractUser, Entity):

    username = models.NOT_PROVIDED
    email = models.EmailField(_('email address'), null=True, blank=True)
    phone_number = models.CharField(unique=True,max_length=15,validators=[phone_validator])
    address1 = models.CharField(max_length=255, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return True
