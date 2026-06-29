from datetime import datetime, timedelta

from apps.booking.models import Appointment, MasterDayOff


def get_master_availability(master, date, service):
    if MasterDayOff.objects.filter(master=master, date=date).exists():
        return []

    if not master.is_available:
        return []

    duration = service.duration_minutes
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
    )
    for appt in appointments:
        blocked.append((
            datetime.combine(date, appt.start_time),
            datetime.combine(date, appt.end_time),
        ))

    blocked.sort(key=lambda x: x[0])

    free_windows = []
    current = work_start

    for block_start, block_end in blocked:
        if block_start > current:
            free_windows.append((current, block_start))
        if block_end > current:
            current = block_end

    if current < work_end:
        free_windows.append((current, work_end))

    slots = []
    slot_duration = timedelta(minutes=duration)

    for window_start, window_end in free_windows:
        slot_start = window_start
        while slot_start + slot_duration <= window_end:
            slot_end = slot_start + slot_duration
            slots.append({
                'start': slot_start.strftime('%H:%M'),
                'end': slot_end.strftime('%H:%M'),
            })
            slot_start += slot_duration

    return slots
