from django_filters import rest_framework as filters
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser

from .models import Product, ProductCategory, ProductImage
from .serializers import (
    AdminProductSerializer,
    ProductCategorySerializer,
    ProductImageSerializer,
    ProductImageUploadSerializer,
    ProductSerializer,
)


class ProductFilter(filters.FilterSet):
    category = filters.NumberFilter(field_name='category_id')
    price_min = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = filters.NumberFilter(field_name='price', lookup_expr='lte')
    is_featured = filters.BooleanFilter()

    class Meta:
        model = Product
        fields = ['category', 'price_min', 'price_max', 'is_featured']


class ProductQuerysetMixin:
    def get_queryset(self):
        return Product.objects.filter(is_active=True).prefetch_related('images', 'category')


class ProductCategoryListView(generics.ListAPIView):
    queryset = ProductCategory.objects.filter(is_active=True)
    serializer_class = ProductCategorySerializer
    permission_classes = [AllowAny]


class ProductListView(ProductQuerysetMixin, generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'brand']


class ProductDetailView(ProductQuerysetMixin, generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class FeaturedProductListView(ProductQuerysetMixin, generics.ListAPIView):
    def get_queryset(self):
        return super().get_queryset().filter(is_featured=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class AdminProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.prefetch_related('images')
    serializer_class = AdminProductSerializer
    permission_classes = [IsAdminUser]


class AdminProductUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.prefetch_related('images')
    serializer_class = AdminProductSerializer
    permission_classes = [IsAdminUser]


class AdminProductImageCreateView(generics.CreateAPIView):
    serializer_class = ProductImageUploadSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        product = Product.objects.get(pk=self.kwargs['pk'])
        is_primary = serializer.validated_data.get('is_primary', False)
        if is_primary:
            ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)
        elif not ProductImage.objects.filter(product=product).exists():
            serializer.save(product=product, is_primary=True)
            return
        serializer.save(product=product)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class AdminProductImageDeleteView(generics.DestroyAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminUser]


class AdminProductCategoryUpdateView(generics.ListCreateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAdminUser]
