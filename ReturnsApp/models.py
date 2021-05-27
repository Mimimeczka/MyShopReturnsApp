from django.db import models


class Return(models.Model):
    date = models.DateField()
    sum = models.DecimalField(max_digits=10, decimal_places=2)
    basket_id = models.IntegerField(default=None)
    summarized = models.BooleanField(default=False)

    def __str__(self):
        return f'Return {self.pk}'


class Product(models.Model):
    product_id = models.IntegerField()
    quantity = models.IntegerField()
    my_return = models.ForeignKey(Return, on_delete=models.CASCADE, default=None, null=True, related_name='products')