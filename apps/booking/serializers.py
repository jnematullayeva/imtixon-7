from datetime import datetime, timedelta

from rest_framework import serializers

from apps.booking.models import (
    Appointment,
    MasterDayOff,
    MasterProfile,
    Service,
    ServiceCategory,
)
from apps.booking.validators import check_appointment_conflict


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description', 'icon', 'is_active', 'order']


class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'category', 'category_name', 'name', 'description',
            'duration_minutes', 'price', 'is_active',
        ]


class MasterProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    specializations = ServiceCategorySerializer(many=True, read_only=True)
    specialization_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ServiceCategory.objects.all(), source='specializations', write_only=True, required=False
    )

    class Meta:
        model = MasterProfile
        fields = [
            'id', 'user', 'user_name', 'username', 'bio', 'specializations',
            'specialization_ids', 'experience_years', 'photo', 'is_available',
            'work_start_time', 'work_end_time', 'break_start', 'break_end',
        ]


class MasterDayOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterDayOff
        fields = ['id', 'master', 'date', 'reason']


class AppointmentSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    client_username = serializers.CharField(source='client.username', read_only=True)
    master_name = serializers.SerializerMethodField()
    master_username = serializers.CharField(source='master.user.username', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_price = serializers.DecimalField(source='service.price', max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'client', 'client_name', 'client_username', 'master', 'master_name',
            'master_username', 'service', 'service_name', 'service_price', 'date', 'start_time',
            'end_time', 'status', 'notes', 'created_at', 'updated_at',
            'cancelled_by', 'cancellation_reason',
        ]
        read_only_fields = [
            'client', 'end_time', 'status', 'created_at', 'updated_at',
            'cancelled_by', 'cancellation_reason',
        ]

    def get_client_name(self, obj):
        client = obj.client
        full_name = client.get_full_name()
        return full_name if full_name.strip() else client.username

    def get_master_name(self, obj):
        master = obj.master.user
        full_name = master.get_full_name()
        return full_name if full_name.strip() else master.username

    def validate(self, attrs):
        master = attrs.get('master') or getattr(self.instance, 'master', None)
        service = attrs.get('service') or getattr(self.instance, 'service', None)
        date = attrs.get('date') or getattr(self.instance, 'date', None)
        start_time = attrs.get('start_time') or getattr(self.instance, 'start_time', None)

        if master and service and date and start_time:
            start_dt = datetime.combine(date, start_time)
            end_dt = start_dt + timedelta(minutes=service.duration_minutes)
            end_time = end_dt.time()
            attrs['end_time'] = end_time

            if check_appointment_conflict(
                master=master,
                date=date,
                start_time=start_time,
                end_time=end_time,
                exclude_id=self.instance.pk if self.instance else None,
            ):
                raise serializers.ValidationError('Bu vaqt band. Double-booking mumkin emas.')

        return attrs

    def create(self, validated_data):
        validated_data['client'] = self.context['request'].user
        return super().create(validated_data)


class AppointmentCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['cancellation_reason']


class AdminAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            'id', 'client', 'master', 'service', 'date', 'start_time',
            'end_time', 'status', 'notes', 'created_at', 'updated_at',
            'cancelled_by', 'cancellation_reason',
        ]
