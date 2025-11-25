# shop/serializers.py
from rest_framework import serializers
from .models import Product

class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=0)

class CreateOrderSerializer(serializers.Serializer):
    items = serializers.ListSerializer(child=CartItemSerializer())

    def validate(self, data):
        items = data['items']
        if not any(it['quantity'] > 0 for it in items):
            raise serializers.ValidationError("You must order at least one item.")
        # validate product existence
        product_ids = [it['product_id'] for it in items if it['quantity'] > 0]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}
        for pid in product_ids:
            if pid not in products:
                raise serializers.ValidationError(f'Product {pid} not found.')
        return data
