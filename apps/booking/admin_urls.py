from django.urls import path

from .views import (
    AdminAppointmentDetailView,
    AdminAppointmentListView,
    AdminMasterCreateView,
    AdminMasterDayOffView,
    AdminMasterUpdateView,
)

urlpatterns = [
    path('appointments/', AdminAppointmentListView.as_view(), name='admin-appointment-list'),
    path('appointments/<int:pk>/', AdminAppointmentDetailView.as_view(), name='admin-appointment-detail'),
    path('masters/', AdminMasterCreateView.as_view(), name='admin-master-create'),
    path('masters/<int:pk>/', AdminMasterUpdateView.as_view(), name='admin-master-update'),
    path('masters/<int:pk>/dayoff/', AdminMasterDayOffView.as_view(), name='admin-master-dayoff'),
]
