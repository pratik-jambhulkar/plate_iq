import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from invoice.managers import DefaultManager, UserManager
from invoice.utils import generate_invoice_number


class CommonField(models.Model):
    # Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = DefaultManager()

    class Meta:
        abstract = True


class User(AbstractBaseUser, PermissionsMixin, CommonField):
    # Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    # ParentModelFields
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

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


class Company(CommonField):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField()
    email = models.EmailField()

    class Meta:
        db_table = 'companies'


class Invoice(CommonField):
    invoice_number = models.CharField(max_length=8, primary_key=True, editable=False, default=generate_invoice_number)
    terms = models.TextField(null=True, blank=True)

    deu_date = models.DateTimeField()

    digitized = models.BooleanField(default=False)
    digitized_by = models.ForeignKey('User', on_delete=models.CASCADE, null=True, related_name='digitized_invoice')
    purchaser = models.ForeignKey('Company', on_delete=models.CASCADE, null=True, related_name='purchaser')
    vendor = models.ForeignKey('Company', on_delete=models.CASCADE, null=True, related_name='vendor')
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, null=True, related_name='created_invoice')

    @property
    def total(self):
        total = 0
        for item in self.invoice_items.all():
            total += item.amount
        return total

    class Meta:
        db_table = 'invoices'


class InvoiceItem(CommonField):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    quantity = models.IntegerField(default=1)
    price = models.FloatField()
    amount = models.FloatField()

    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, null=True, related_name='invoice_items')

    class Meta:
        db_table = 'invoice_items'
