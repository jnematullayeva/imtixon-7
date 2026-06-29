from rest_framework import serializers

from .models import Product, ProductCategory, ProductImage


def build_image_url(request, image_field):
    if not image_field:
        return None
    url = image_field.url
    if request:
        return request.build_absolute_uri(url)
    return url


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'alt_text', 'is_primary', 'order']
        read_only_fields = ['id', 'product']

    def get_image(self, obj):
        return build_image_url(self.context.get('request'), obj.image)


class ProductCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug', 'description', 'image', 'is_active', 'order']

    def get_image(self, obj):
        return build_image_url(self.context.get('request'), obj.image)


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'name', 'slug', 'description',
            'brand', 'price', 'stock_quantity', 'unit', 'sku', 'is_active',
            'is_featured', 'created_at', 'images', 'primary_image', 'in_stock',
        ]

    def get_primary_image(self, obj):
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        if img and img.image:
            return build_image_url(self.context.get('request'), img.image)
        return None

    def get_in_stock(self, obj):
        return obj.stock_quantity > 0


class AdminProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'name', 'slug', 'description', 'brand', 'price',
            'stock_quantity', 'unit', 'sku', 'is_active', 'is_featured', 'created_at', 'images',
        ]


class ProductImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']
        read_only_fields = ['id']
