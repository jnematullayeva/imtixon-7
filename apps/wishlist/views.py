from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.services import create_order_from_items
from apps.shop.models import Product

from .models import Wishlist, WishlistItem
from .serializers import WishlistAddSerializer, WishlistSerializer


class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        return Response(WishlistSerializer(wishlist).data)


class WishlistAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WishlistAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data['product_id']

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Mahsulot topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
        return Response(WishlistSerializer(wishlist).data, status=status.HTTP_201_CREATED)


class WishlistRemoveView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        WishlistItem.objects.filter(wishlist=wishlist, product_id=product_id).delete()
        return Response(WishlistSerializer(wishlist).data)


class WishlistMoveToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        try:
            item = WishlistItem.objects.get(wishlist=wishlist, product_id=product_id)
        except WishlistItem.DoesNotExist:
            return Response({'detail': 'Mahsulot wishlistda topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        product = item.product
        if not product.is_active:
            return Response({'detail': 'Mahsulot faol emas.'}, status=status.HTTP_400_BAD_REQUEST)
        if product.stock_quantity == 0:
            return Response({'detail': 'Stokda yo\'q.'}, status=status.HTTP_400_BAD_REQUEST)

        order = create_order_from_items(
            client=request.user,
            items=[{'product_id': product.id, 'quantity': 1}],
        )
        item.delete()
        from apps.orders.serializers import OrderSerializer
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class WishlistClearView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        wishlist.items.all().delete()
        return Response(WishlistSerializer(wishlist).data)
