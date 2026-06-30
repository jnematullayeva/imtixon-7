from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse

from apps.booking.serializers import AppointmentSerializer

appointment_list_schema = extend_schema_view(
    get=extend_schema(
        summary='Bronlar ro\'yxati',
        description='Mijoz o\'z bronlarini, master o\'ziga biriktirilgan bronlarni ko\'radi.',
        responses={200: AppointmentSerializer(many=True)},
    ),
    post=extend_schema(
        summary='Yangi bron yaratish',
        description='Mijoz master, xizmat, sana va vaqt tanlab bron qiladi.',
        request=AppointmentSerializer,
        responses={201: AppointmentSerializer},
    ),
)

profile_history_schema = extend_schema(
    summary='Profil bron tarixi',
    description='Autentifikatsiyadan o\'tgan foydalanuvchi uchun bron tarixi (mijoz yoki master).',
    responses={200: AppointmentSerializer(many=True)},
)

master_availability_schema = extend_schema(
    summary='Master bo\'sh vaqtlari',
    parameters=[
        OpenApiParameter(name='date', required=True, type=str, description='YYYY-MM-DD'),
        OpenApiParameter(name='service_id', required=True, type=int),
    ],
    responses={200: OpenApiResponse(description='Bo\'sh slotlar ro\'yxati')},
)

master_free_slots_schema = extend_schema(
    summary='Master erkin oynalari',
    parameters=[
        OpenApiParameter(name='date', required=True, type=str, description='YYYY-MM-DD'),
    ],
    responses={200: OpenApiResponse(description='Erkin vaqt oynalari')},
)
