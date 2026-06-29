from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models


class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Wishlist: {self.user.username}'


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE, related_name='wishlist_items')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('wishlist', 'product')]

    def __str__(self):
        return f'{self.wishlist.user.username} - {self.product.name}'
