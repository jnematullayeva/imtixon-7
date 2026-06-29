from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import queries


class BookingSummaryReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        date_from, date_to = queries.parse_date_range(request)
        return Response(queries.booking_summary(date_from, date_to))


class BookingsByMasterReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        date_from, date_to = queries.parse_date_range(request)
        master_id = request.query_params.get('master_id')
        return Response(queries.bookings_by_master(date_from, date_to, master_id))


class BookingsByServiceReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        date_from, date_to = queries.parse_date_range(request)
        category_id = request.query_params.get('category_id')
        return Response(queries.bookings_by_service(date_from, date_to, category_id))


class BookingsByDateReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        date_from, date_to = queries.parse_date_range(request)
        return Response(queries.bookings_by_date(date_from, date_to))


class NoShowReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        date_from, date_to = queries.parse_date_range(request)
        return Response(queries.no_show_clients(date_from, date_to))


class TopClientsReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        date_from, date_to = queries.parse_date_range(request)
        limit = int(request.query_params.get('limit', 10))
        return Response(queries.top_clients(date_from, date_to, limit))


class NewClientsReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        date_from, date_to = queries.parse_date_range(request)
        return Response(queries.new_clients(date_from, date_to))


class OrdersSummaryReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        date_from, date_to = queries.parse_date_range(request)
        return Response(queries.orders_summary(date_from, date_to))


class OrdersByStatusReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        date_from, date_to = queries.parse_date_range(request)
        return Response(queries.orders_by_status(date_from, date_to))


class TopSellingProductsReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        date_from, date_to = queries.parse_date_range(request)
        limit = int(request.query_params.get('limit', 10))
        return Response(queries.top_selling_products(date_from, date_to, limit))


class LowStockReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        threshold = int(request.query_params.get('threshold', 5))
        return Response(queries.low_stock_products(threshold))


class ProductStockReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        category_id = request.query_params.get('category_id')
        return Response(queries.product_stock_report(category_id))


class RevenueReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        date_from, date_to = queries.parse_date_range(request)
        group_by = request.query_params.get('group_by', 'total')
        return Response(queries.revenue_report(date_from, date_to, group_by))


class MasterDashboardReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not getattr(user, 'is_master', False) or not hasattr(user, 'master_profile'):
            raise PermissionDenied('Master access required.')
        return Response(queries.master_dashboard_summary(user.master_profile))


class DashboardReportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(queries.dashboard_summary())
