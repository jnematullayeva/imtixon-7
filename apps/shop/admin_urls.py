from django.urls import path

from .views import (
    AdminProductCategoryUpdateView,
    AdminProductCreateView,
    AdminProductImageCreateView,
    AdminProductImageDeleteView,
    AdminProductUpdateView,
)

urlpatterns = [
    path('shop/products/', AdminProductCreateView.as_view(), name='admin-product-create'),
    path('shop/products/<int:pk>/', AdminProductUpdateView.as_view(), name='admin-product-update'),
    path('shop/products/<int:pk>/images/', AdminProductImageCreateView.as_view(), name='admin-product-image-create'),
    path('shop/products/images/<int:pk>/', AdminProductImageDeleteView.as_view(), name='admin-product-image-delete'),
    path('shop/categories/', AdminProductCategoryUpdateView.as_view(), name='admin-shop-categories'),
]
