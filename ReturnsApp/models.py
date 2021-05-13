from django.db import models


class Product(models.Model):
    product_id = models.IntegerField()
    quantity = models.IntegerField()


class Return(models.Model):
    date = models.DateField()
    products = models.ForeignKey(Product, on_delete=models.CASCADE, default=None, null=True)
    sum = models.DecimalField(max_digits=10, decimal_places=2)
    basket_id = models.IntegerField(default=None)

    def __str__(self):
        return f'Return {self.date}'