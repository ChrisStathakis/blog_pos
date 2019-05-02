from django.db import models


class ProductManager(models.Manager):

    def active(self):
        return self.filter(active=True)

    def have_qty(self):
        return self.active().filter(qty__gte=1)