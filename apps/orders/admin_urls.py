from django.urls import path

from .views import AdminOrderDetailView, AdminOrderListView, AdminOrderStatusView

urlpatterns = [
    path('orders/', AdminOrderListView.as_view(), name='admin-order-list'),
    path('orders/<int:pk>/', AdminOrderDetailView.as_view(), name='admin-order-detail'),
    path('orders/<int:pk>/status/', AdminOrderStatusView.as_view(), name='admin-order-status'),
]
