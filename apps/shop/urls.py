from django.urls import path

from .views import (
    FeaturedProductListView,
    ProductCategoryListView,
    ProductDetailView,
    ProductListView,
)

urlpatterns = [
    path('categories/', ProductCategoryListView.as_view(), name='shop-category-list'),
    path('products/', ProductListView.as_view(), name='shop-product-list'),
    path('products/featured/', FeaturedProductListView.as_view(), name='shop-featured-products'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='shop-product-detail'),
]
