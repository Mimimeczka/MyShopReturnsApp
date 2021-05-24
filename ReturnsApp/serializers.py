from .models import Return, Product
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_id', 'quantity', 'id']


class ReturnSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = Return
        fields = ['date', 'id', 'sum', 'products', 'basket_id', 'summarized']

