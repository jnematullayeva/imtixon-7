from rest_framework import serializers

from apps.shop.serializers import ProductSerializer

from .models import Wishlist, WishlistItem


class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    out_of_stock = serializers.SerializerMethodField()

    class Meta:
        model = WishlistItem
        fields = ['id', 'product', 'added_at', 'out_of_stock']

    def get_out_of_stock(self, obj):
        return obj.product.stock_quantity == 0


class WishlistSerializer(serializers.ModelSerializer):
    items = WishlistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'created_at', 'items']
        read_only_fields = ['user', 'created_at']


class WishlistAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
