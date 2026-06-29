from apps.booking.models import Appointment


def check_appointment_conflict(master, date, start_time, end_time, exclude_id=None):
    qs = Appointment.objects.filter(
        master=master,
        date=date,
        status__in=['pending', 'confirmed'],
        start_time__lt=end_time,
        end_time__gt=start_time,
    )
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    return qs.exists()
