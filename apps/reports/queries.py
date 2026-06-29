from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.booking.models import Appointment
from apps.orders.models import Order, OrderItem
from apps.shop.models import Product

User = get_user_model()


def parse_date_range(request):
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    start = None
    end = None
    if date_from:
        try:
            start = datetime.strptime(date_from, '%Y-%m-%d').date()
        except ValueError as exc:
            raise ValidationError({'date_from': 'Noto\'g\'ri sana formati. YYYY-MM-DD ishlating.'}) from exc
    if date_to:
        try:
            end = datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError as exc:
            raise ValidationError({'date_to': 'Noto\'g\'ri sana formati. YYYY-MM-DD ishlating.'}) from exc
    if start and end and start > end:
        raise ValidationError({'date_to': 'Tugash sanasi boshlanish sanasidan oldin bo\'lishi mumkin emas.'})
    return start, end


def filter_appointments_by_date(qs, date_from, date_to):
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    return qs


def filter_orders_by_date(qs, date_from, date_to):
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)
    return qs


def booking_summary(date_from, date_to):
    qs = filter_appointments_by_date(Appointment.objects.all(), date_from, date_to)
    return {
        'total': qs.count(),
        'confirmed': qs.filter(status='confirmed').count(),
        'cancelled': qs.filter(status='cancelled').count(),
        'completed': qs.filter(status='completed').count(),
        'no_show': qs.filter(status='no_show').count(),
    }


def bookings_by_master(date_from, date_to, master_id=None):
    qs = filter_appointments_by_date(
        Appointment.objects.filter(status__in=['confirmed', 'completed']),
        date_from, date_to,
    )
    if master_id:
        qs = qs.filter(master_id=master_id)
    data = qs.values('master_id', 'master__user__first_name', 'master__user__last_name').annotate(
        count=Count('id'),
        revenue=Sum('service__price'),
    )
    return list(data)


def bookings_by_service(date_from, date_to, category_id=None):
    qs = filter_appointments_by_date(
        Appointment.objects.filter(status__in=['confirmed', 'completed']),
        date_from, date_to,
    )
    if category_id:
        qs = qs.filter(service__category_id=category_id)
    data = qs.values('service_id', 'service__name').annotate(count=Count('id')).order_by('-count')
    return list(data)


def bookings_by_date(date_from, date_to):
    qs = filter_appointments_by_date(Appointment.objects.all(), date_from, date_to)
    data = qs.annotate(day=TruncDate('date')).values('day').annotate(count=Count('id')).order_by('day')
    return [{'date': item['day'].isoformat(), 'count': item['count']} for item in data]


def no_show_clients(date_from, date_to):
    qs = filter_appointments_by_date(
        Appointment.objects.filter(status='no_show'),
        date_from, date_to,
    )
    return list(qs.values(
        'client_id', 'client__first_name', 'client__last_name',
        'client__phone', 'date', 'service__name',
    ))


def top_clients(date_from, date_to, limit=10):
    qs = filter_appointments_by_date(
        Appointment.objects.filter(status__in=['confirmed', 'completed']),
        date_from, date_to,
    )
    data = qs.values('client_id', 'client__first_name', 'client__last_name').annotate(
        appointment_count=Count('id'),
    ).order_by('-appointment_count')[:limit]
    return list(data)


def new_clients(date_from, date_to):
    qs = User.objects.filter(is_staff=False, is_master=False)
    if date_from:
        qs = qs.filter(date_joined__date__gte=date_from)
    if date_to:
        qs = qs.filter(date_joined__date__lte=date_to)
    return list(qs.values('id', 'username', 'first_name', 'last_name', 'phone', 'date_joined'))


def orders_summary(date_from, date_to):
    qs = filter_orders_by_date(
        Order.objects.filter(status__in=['confirmed', 'processing', 'completed']),
        date_from, date_to,
    )
    total_orders = qs.count()
    total_revenue = qs.aggregate(total=Sum('total_price'))['total'] or Decimal('0')
    avg_check = total_revenue / total_orders if total_orders else Decimal('0')
    return {
        'total_orders': total_orders,
        'total_revenue': float(total_revenue),
        'average_check': float(avg_check),
    }


def orders_by_status(date_from, date_to):
    qs = filter_orders_by_date(Order.objects.all(), date_from, date_to)
    data = qs.values('status').annotate(count=Count('id'), revenue=Sum('total_price'))
    return list(data)


def top_selling_products(date_from, date_to, limit=10):
    qs = OrderItem.objects.filter(order__status__in=['confirmed', 'processing', 'completed'])
    if date_from:
        qs = qs.filter(order__created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(order__created_at__date__lte=date_to)
    data = qs.values('product_name').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('subtotal'),
    ).order_by('-total_quantity')[:limit]
    return list(data)


def low_stock_products(threshold=5):
    qs = Product.objects.filter(is_active=True, stock_quantity__lte=threshold)
    return list(qs.values('id', 'name', 'stock_quantity', 'sku', 'price'))


def product_stock_report(category_id=None):
    qs = Product.objects.filter(is_active=True)
    if category_id:
        qs = qs.filter(category_id=category_id)
    return list(qs.values('id', 'name', 'stock_quantity', 'unit', 'category__name'))


def revenue_report(date_from, date_to, group_by='total'):
    booking_qs = filter_appointments_by_date(
        Appointment.objects.filter(status__in=['confirmed', 'completed']),
        date_from, date_to,
    )
    booking_revenue = booking_qs.aggregate(total=Sum('service__price'))['total'] or Decimal('0')

    order_qs = filter_orders_by_date(
        Order.objects.filter(status__in=['confirmed', 'processing', 'completed']),
        date_from, date_to,
    )
    shop_revenue = order_qs.aggregate(total=Sum('total_price'))['total'] or Decimal('0')

    result = {
        'booking_revenue': float(booking_revenue),
        'shop_revenue': float(shop_revenue),
        'total_revenue': float(booking_revenue + shop_revenue),
        'group_by': group_by,
    }
    return result


def master_dashboard_summary(master):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    today_appointments = Appointment.objects.filter(master=master, date=today)
    month_appointments = Appointment.objects.filter(master=master, date__gte=month_start, date__lte=today)

    booking_revenue = month_appointments.filter(
        status__in=['confirmed', 'completed']
    ).aggregate(total=Sum('service__price'))['total'] or Decimal('0')

    upcoming = Appointment.objects.filter(
        master=master,
        date__gte=today,
        status__in=['pending', 'confirmed'],
    ).select_related('client', 'service').order_by('date', 'start_time')[:10]

    upcoming_data = [{
        'id': a.id,
        'client': a.client.get_full_name(),
        'service': a.service.name,
        'date': a.date.isoformat(),
        'start_time': a.start_time.strftime('%H:%M'),
        'status': a.status,
    } for a in upcoming]

    return {
        'master': master.user.get_full_name(),
        'today': {
            'appointments': today_appointments.count(),
            'confirmed': today_appointments.filter(status='confirmed').count(),
            'pending': today_appointments.filter(status='pending').count(),
            'cancelled': today_appointments.filter(status='cancelled').count(),
            'completed': today_appointments.filter(status='completed').count(),
        },
        'this_month': {
            'total_appointments': month_appointments.count(),
            'booking_revenue': float(booking_revenue),
        },
        'upcoming_appointments': upcoming_data,
    }


def dashboard_summary():
    today = timezone.now().date()
    month_start = today.replace(day=1)

    today_appointments = Appointment.objects.filter(date=today)
    month_appointments = Appointment.objects.filter(date__gte=month_start, date__lte=today)
    month_orders = Order.objects.filter(created_at__date__gte=month_start, created_at__date__lte=today)

    booking_revenue = month_appointments.filter(
        status__in=['confirmed', 'completed']
    ).aggregate(total=Sum('service__price'))['total'] or Decimal('0')

    shop_revenue = month_orders.filter(
        status__in=['confirmed', 'processing', 'completed']
    ).aggregate(total=Sum('total_price'))['total'] or Decimal('0')

    upcoming = Appointment.objects.filter(
        date__gte=today,
        status__in=['pending', 'confirmed'],
    ).select_related('client', 'master', 'service').order_by('date', 'start_time')[:10]

    upcoming_data = [{
        'id': a.id,
        'client': a.client.get_full_name(),
        'master': a.master.user.get_full_name(),
        'service': a.service.name,
        'date': a.date.isoformat(),
        'start_time': a.start_time.strftime('%H:%M'),
        'status': a.status,
    } for a in upcoming]

    return {
        'today': {
            'appointments': today_appointments.count(),
            'confirmed': today_appointments.filter(status='confirmed').count(),
            'pending': today_appointments.filter(status='pending').count(),
            'cancelled': today_appointments.filter(status='cancelled').count(),
        },
        'this_month': {
            'total_appointments': month_appointments.count(),
            'total_orders': month_orders.count(),
            'booking_revenue': float(booking_revenue),
            'shop_revenue': float(shop_revenue),
        },
        'low_stock_products': low_stock_products(),
        'upcoming_appointments': upcoming_data,
    }
