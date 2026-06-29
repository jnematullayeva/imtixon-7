from django_filters import rest_framework as filters
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsOwnerOrAdmin

from .models import Order
from .serializers import OrderCreateSerializer, OrderSerializer, OrderStatusUpdateSerializer
from .services import create_order_from_items, update_order_status


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().prefetch_related('items')
        return Order.objects.filter(client=user).prefetch_related('items')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = create_order_from_items(
                client=request.user,
                items=serializer.validated_data['items'],
                delivery_address=serializer.validated_data.get('delivery_address', ''),
                notes=serializer.validated_data.get('notes', ''),
            )
        except ValidationError as e:
            raise e
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().prefetch_related('items')
        return Order.objects.filter(client=user).prefetch_related('items')


class OrderCancelView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'detail': 'Buyurtma topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_staff and order.client != request.user:
            return Response({'detail': 'Ruxsat yo\'q.'}, status=status.HTTP_403_FORBIDDEN)

        if order.status != 'pending':
            return Response({'detail': 'Faqat pending buyurtmani bekor qilish mumkin.'}, status=status.HTTP_400_BAD_REQUEST)

        update_order_status(order, 'cancelled', is_admin=request.user.is_staff, is_client=order.client == request.user)
        return Response(OrderSerializer(order).data)


class AdminOrderFilter(filters.FilterSet):
    status = filters.CharFilter()
    client = filters.NumberFilter(field_name='client_id')
    date_from = filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    date_to = filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

    class Meta:
        model = Order
        fields = ['status', 'client', 'date_from', 'date_to']


class AdminOrderListView(generics.ListAPIView):
    queryset = Order.objects.all().prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    filterset_class = AdminOrderFilter


class AdminOrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all().prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]


class AdminOrderStatusView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'detail': 'Buyurtma topilmadi.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_order_status(order, serializer.validated_data['status'], is_admin=True)
        return Response(OrderSerializer(order).data)
