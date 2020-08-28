from django.db import models


class DefaultManager(models.Manager):
    pass


class UserManager(DefaultManager):
    def get_by_natural_key(self, email_id):
        return super(UserManager, self).get(email=email_id)
