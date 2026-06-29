from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_save, sender=User)
def create_wishlist_for_user(sender, instance, created, **kwargs):
    if created:
        from apps.wishlist.models import Wishlist
        Wishlist.objects.get_or_create(user=instance)
