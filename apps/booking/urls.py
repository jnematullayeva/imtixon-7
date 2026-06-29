from django.urls import path

from .views import (
    AppointmentCancelView,
    AppointmentDetailView,
    AppointmentListCreateView,
    CategoryServicesView,
    MasterAvailabilityView,
    MasterDetailView,
    MasterFreeSlotsView,
    MasterListView,
    ServiceCategoryListView,
    ServiceListView,
)

urlpatterns = [
    path('categories/', ServiceCategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/services/', CategoryServicesView.as_view(), name='category-services'),
    path('services/', ServiceListView.as_view(), name='service-list'),
    path('masters/', MasterListView.as_view(), name='master-list'),
    path('masters/<int:pk>/', MasterDetailView.as_view(), name='master-detail'),
    path('masters/<int:pk>/availability/', MasterAvailabilityView.as_view(), name='master-availability'),
    path('masters/<int:pk>/free-slots/', MasterFreeSlotsView.as_view(), name='master-free-slots'),
    path('appointments/', AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('appointments/<int:pk>/cancel/', AppointmentCancelView.as_view(), name='appointment-cancel'),
]
