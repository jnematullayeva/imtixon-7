from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.shop.models import Product

from .models import Order, OrderItem


def generate_order_number():
    year = timezone.now().year
    prefix = f'ORD-{year}'
    last_order = Order.objects.filter(order_number__startswith=prefix).order_by('-order_number').first()
    if last_order:
        last_num = int(last_order.order_number.split(prefix)[1])
        new_num = last_num + 1
    else:
        new_num = 1
    return f'{prefix}{new_num:04d}'


ALLOWED_STATUS_TRANSITIONS = {
    'pending': ['confirmed', 'cancelled'],
    'confirmed': ['processing', 'cancelled'],
    'processing': ['completed', 'cancelled'],
    'completed': [],
    'cancelled': [],
}


def validate_status_transition(current_status, new_status):
    allowed = ALLOWED_STATUS_TRANSITIONS.get(current_status, [])
    if new_status not in allowed:
        raise DRFValidationError(f'"{current_status}" dan "{new_status}" ga o\'tish mumkin emas.')


@transaction.atomic
def create_order_from_items(client, items, delivery_address='', notes=''):
    if not items:
        raise DRFValidationError('Buyurtma elementlari bo\'sh bo\'lmasligi kerak.')

    order = Order.objects.create(
        order_number=generate_order_number(),
        client=client,
        delivery_address=delivery_address,
        notes=notes,
    )

    total_price = Decimal('0.00')

    for item_data in items:
        product_id = item_data['product_id']
        quantity = item_data.get('quantity', 1)

        try:
            product = Product.objects.select_for_update().get(pk=product_id)
        except Product.DoesNotExist:
            raise DRFValidationError(f'Mahsulot topilmadi: {product_id}')

        if not product.is_active:
            raise DRFValidationError(f'Mahsulot faol emas: {product.name}')

        if product.stock_quantity < quantity:
            raise DRFValidationError(f'Yetarli stok yo\'q: {product.name}')

        subtotal = product.price * quantity
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_price=product.price,
            quantity=quantity,
            subtotal=subtotal,
        )

        product.stock_quantity -= quantity
        product.save(update_fields=['stock_quantity'])
        total_price += subtotal

    order.total_price = total_price
    order.save(update_fields=['total_price'])
    return order


def update_order_status(order, new_status, is_admin=False, is_client=False):
    if order.status in ['completed', 'cancelled']:
        raise DRFValidationError('Yakunlangan yoki bekor qilingan buyurtmani o\'zgartirib bo\'lmaydi.')

    if new_status == 'cancelled' and order.status == 'pending':
        if not (is_admin or is_client):
            raise DRFValidationError('Bekor qilish uchun ruxsat yo\'q.')
    elif not is_admin:
        raise DRFValidationError('Faqat admin statusni o\'zgartira oladi.')

    validate_status_transition(order.status, new_status)
    order.status = new_status

    if new_status == 'confirmed':
        order.confirmed_at = timezone.now()
    elif new_status == 'completed':
        order.completed_at = timezone.now()

    order.save()
    return order
