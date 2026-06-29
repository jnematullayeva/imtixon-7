from django_filters import rest_framework as filters
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsOwnerOrAdmin

from .availability import get_master_availability
from .models import Appointment, MasterDayOff, MasterProfile, Service, ServiceCategory
from .serializers import (
    AdminAppointmentSerializer,
    AppointmentCancelSerializer,
    AppointmentSerializer,
    MasterDayOffSerializer,
    MasterProfileSerializer,
    ServiceCategorySerializer,
    ServiceSerializer,
)


class CanCreateAppointment(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.method == 'POST' and request.user.is_master and not request.user.is_staff:
            return False
        return True


class ServiceCategoryListView(generics.ListAPIView):
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAuthenticated]


class CategoryServicesView(generics.ListAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Service.objects.filter(category_id=self.kwargs['pk'], is_active=True)


class ServiceListView(generics.ListAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category']

    def get_queryset(self):
        return Service.objects.filter(is_active=True)


class MasterFilter(filters.FilterSet):
    service = filters.NumberFilter(field_name='specializations__services')
    category = filters.NumberFilter(field_name='specializations')

    class Meta:
        model = MasterProfile
        fields = ['service', 'category']


class MasterListView(generics.ListAPIView):
    serializer_class = MasterProfileSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = MasterFilter

    def get_queryset(self):
        return MasterProfile.objects.filter(is_available=True).distinct()


class MasterDetailView(generics.RetrieveAPIView):
    queryset = MasterProfile.objects.all()
    serializer_class = MasterProfileSerializer
    permission_classes = [IsAuthenticated]


class MasterAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        date_str = request.query_params.get('date')
        service_id = request.query_params.get('service_id')

        if not date_str or not service_id:
            return Response(
                {'detail': 'date va service_id parametrlari talab qilinadi.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            service = Service.objects.get(pk=service_id, is_active=True)
            master = MasterProfile.objects.get(pk=pk, is_available=True)
        except (ValueError, Service.DoesNotExist, MasterProfile.DoesNotExist):
            return Response({'detail': 'Noto\'g\'ri parametrlar.'}, status=status.HTTP_400_BAD_REQUEST)

        slots = get_master_availability(master, date, service)
        return Response(slots)


class MasterFreeSlotsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response(
                {'detail': 'date parametri talab qilinadi.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from datetime import datetime
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            master = MasterProfile.objects.get(pk=pk)
        except (ValueError, MasterProfile.DoesNotExist):
            return Response({'detail': 'Noto\'g\'ri parametrlar.'}, status=status.HTTP_400_BAD_REQUEST)

        if MasterDayOff.objects.filter(master=master, date=date).exists() or not master.is_available:
            return Response([])

        work_start = datetime.combine(date, master.work_start_time)
        work_end = datetime.combine(date, master.work_end_time)

        blocked = []
        if master.break_start and master.break_end:
            blocked.append((
                datetime.combine(date, master.break_start),
                datetime.combine(date, master.break_end),
            ))

        appointments = Appointment.objects.filter(
            master=master,
            date=date,
            status__in=['pending', 'confirmed'],
        ).order_by('start_time')

        for appt in appointments:
            blocked.append((
                datetime.combine(date, appt.start_time),
                datetime.combine(date, appt.end_time),
            ))

        blocked.sort(key=lambda x: x[0])
        free_windows = []
        current = work_start

        for start, end in blocked:
            if start > current:
                free_windows.append({'start': current.strftime('%H:%M'), 'end': start.strftime('%H:%M')})
            if end > current:
                current = end

        if current < work_end:
            free_windows.append({'start': current.strftime('%H:%M'), 'end': work_end.strftime('%H:%M')})

        return Response(free_windows)


class AppointmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [CanCreateAppointment]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Appointment.objects.all().select_related('master', 'service', 'client')
        if user.is_master and hasattr(user, 'master_profile'):
            return Appointment.objects.filter(master=user.master_profile).select_related('service', 'client')
        return Appointment.objects.filter(client=user).select_related('master', 'service')


class AppointmentDetailView(generics.RetrieveAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Appointment.objects.all()
        if user.is_master and hasattr(user, 'master_profile'):
            return Appointment.objects.filter(master=user.master_profile)
        return Appointment.objects.filter(client=user)


class AppointmentCancelView(generics.UpdateAPIView):
    serializer_class = AppointmentCancelSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Appointment.objects.exclude(status__in=['cancelled', 'completed'])
        return Appointment.objects.filter(client=user).exclude(status__in=['cancelled', 'completed'])

    def patch(self, request, *args, **kwargs):
        appointment = self.get_object()
        serializer = self.get_serializer(appointment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        appointment.status = 'cancelled'
        appointment.cancelled_by = request.user
        appointment.cancellation_reason = serializer.validated_data.get('cancellation_reason', '')
        appointment.save()
        return Response(AppointmentSerializer(appointment).data)


class AdminAppointmentFilter(filters.FilterSet):
    status = filters.CharFilter()
    date = filters.DateFilter(field_name='date')
    master = filters.NumberFilter(field_name='master_id')
    client = filters.NumberFilter(field_name='client_id')

    class Meta:
        model = Appointment
        fields = ['status', 'date', 'master', 'client']


class AdminAppointmentListView(generics.ListAPIView):
    queryset = Appointment.objects.all().select_related('client', 'master', 'service')
    serializer_class = AdminAppointmentSerializer
    permission_classes = [IsAdminUser]
    filterset_class = AdminAppointmentFilter


class AdminAppointmentDetailView(generics.RetrieveUpdateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AdminAppointmentSerializer
    permission_classes = [IsAdminUser]


class AdminMasterCreateView(generics.CreateAPIView):
    queryset = MasterProfile.objects.all()
    serializer_class = MasterProfileSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        master = serializer.save()
        user = master.user
        user.is_master = True
        user.save(update_fields=['is_master'])


class AdminMasterUpdateView(generics.RetrieveUpdateAPIView):
    queryset = MasterProfile.objects.all()
    serializer_class = MasterProfileSerializer
    permission_classes = [IsAdminUser]


class AdminMasterDayOffView(generics.CreateAPIView):
    serializer_class = MasterDayOffSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        master = MasterProfile.objects.get(pk=self.kwargs['pk'])
        serializer.save(master=master)
