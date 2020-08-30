from django.db import models


class DefaultManager(models.Manager):
    pass


class UserManager(DefaultManager):
    def get_by_natural_key(self, email_id):
        return super(UserManager, self).get(email=email_id)


class InvoiceItemManager(DefaultManager):
    def create_items(self, invoice, invoice_items):
        self.clean_items(invoice)
        for item in invoice_items:
            self.create(invoice=invoice, **item)

    def clean_items(self, invoice):
        self.filter(invoice=invoice).delete()
