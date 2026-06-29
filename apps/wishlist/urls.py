from django.urls import path

from .views import (
    WishlistAddView,
    WishlistClearView,
    WishlistMoveToCartView,
    WishlistRemoveView,
    WishlistView,
)

urlpatterns = [
    path('', WishlistView.as_view(), name='wishlist'),
    path('add/', WishlistAddView.as_view(), name='wishlist-add'),
    path('remove/<int:product_id>/', WishlistRemoveView.as_view(), name='wishlist-remove'),
    path('move-to-cart/<int:product_id>/', WishlistMoveToCartView.as_view(), name='wishlist-move-to-cart'),
    path('clear/', WishlistClearView.as_view(), name='wishlist-clear'),
]
