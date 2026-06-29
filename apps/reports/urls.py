from django.urls import path

from .views import (
    BookingsByDateReportView,
    BookingsByMasterReportView,
    BookingsByServiceReportView,
    BookingSummaryReportView,
    DashboardReportView,
    LowStockReportView,
    MasterDashboardReportView,
    NewClientsReportView,
    NoShowReportView,
    OrdersByStatusReportView,
    OrdersSummaryReportView,
    ProductStockReportView,
    RevenueReportView,
    TopClientsReportView,
    TopSellingProductsReportView,
)

urlpatterns = [
    path('bookings/summary/', BookingSummaryReportView.as_view(), name='report-booking-summary'),
    path('bookings/by-master/', BookingsByMasterReportView.as_view(), name='report-bookings-by-master'),
    path('bookings/by-service/', BookingsByServiceReportView.as_view(), name='report-bookings-by-service'),
    path('bookings/by-date/', BookingsByDateReportView.as_view(), name='report-bookings-by-date'),
    path('bookings/no-show/', NoShowReportView.as_view(), name='report-no-show'),
    path('clients/top/', TopClientsReportView.as_view(), name='report-top-clients'),
    path('clients/new/', NewClientsReportView.as_view(), name='report-new-clients'),
    path('orders/summary/', OrdersSummaryReportView.as_view(), name='report-orders-summary'),
    path('orders/by-status/', OrdersByStatusReportView.as_view(), name='report-orders-by-status'),
    path('products/top-selling/', TopSellingProductsReportView.as_view(), name='report-top-selling'),
    path('products/low-stock/', LowStockReportView.as_view(), name='report-low-stock'),
    path('products/stock/', ProductStockReportView.as_view(), name='report-product-stock'),
    path('revenue/', RevenueReportView.as_view(), name='report-revenue'),
    path('dashboard/master/', MasterDashboardReportView.as_view(), name='report-dashboard-master'),
    path('dashboard/', DashboardReportView.as_view(), name='report-dashboard'),
]
