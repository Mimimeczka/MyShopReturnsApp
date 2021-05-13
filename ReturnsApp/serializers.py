from .models import Return
from rest_framework import serializers


class ReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Return
        fields = ['date', 'products', 'sum', 'basket_id']