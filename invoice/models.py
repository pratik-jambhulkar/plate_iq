import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class User(AbstractBaseUser, PermissionsMixin):
    # Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    # ParentModelFields
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Methods
    def __str__(self):
        return self.email

    def get_short_name(self):
        pass

    def get_full_name(self):
        pass

    @property
    def is_staff(self):
        return self.is_superuser

    # Meta
    class Meta:
        db_table = 'users'
