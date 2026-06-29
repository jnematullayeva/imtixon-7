from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

User = get_user_model()


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class MasterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='master_profile')
    bio = models.TextField(blank=True)
    specializations = models.ManyToManyField(ServiceCategory, blank=True, related_name='masters')
    experience_years = models.PositiveIntegerField(default=0)
    photo = models.ImageField(upload_to='masters/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    work_start_time = models.TimeField(default='09:00')
    work_end_time = models.TimeField(default='19:00')
    break_start = models.TimeField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.user.username})'


class MasterDayOff(models.Model):
    master = models.ForeignKey(MasterProfile, on_delete=models.CASCADE, related_name='days_off')
    date = models.DateField()
    reason = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = [('master', 'date')]

    def __str__(self):
        return f'{self.master} - {self.date}'


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    master = models.ForeignKey(MasterProfile, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_appointments'
    )
    cancellation_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f'{self.client} - {self.service} ({self.date} {self.start_time})'

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError('Tugash vaqti boshlanish vaqtidan keyin bo\'lishi kerak.')

        from apps.booking.validators import check_appointment_conflict

        if check_appointment_conflict(
            master=self.master,
            date=self.date,
            start_time=self.start_time,
            end_time=self.end_time,
            exclude_id=self.pk,
        ):
            raise ValidationError('Bu vaqt band. Double-booking mumkin emas.')

    def save(self, *args, **kwargs):
        if not self.end_time and self.service_id and self.start_time:
            start_dt = datetime.combine(self.date, self.start_time)
            end_dt = start_dt + timedelta(minutes=self.service.duration_minutes)
            self.end_time = end_dt.time()
        self.full_clean()
        super().save(*args, **kwargs)
