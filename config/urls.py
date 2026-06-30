from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui-alt'),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/booking/', include('apps.booking.urls')),
    path('api/shop/', include('apps.shop.urls')),
    path('api/wishlist/', include('apps.wishlist.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/admin/', include('apps.accounts.admin_urls')),
    path('api/admin/', include('apps.booking.admin_urls')),
    path('api/admin/', include('apps.shop.admin_urls')),
    path('api/admin/', include('apps.orders.admin_urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='profile'),
    path('booking/', TemplateView.as_view(template_name='booking.html'), name='booking'),
    path('shop/', TemplateView.as_view(template_name='shop.html'), name='shop'),
    path('product/<int:pk>/', TemplateView.as_view(template_name='product.html'), name='product'),
    path('wishlist/', TemplateView.as_view(template_name='wishlist.html'), name='wishlist'),
    path('orders/', TemplateView.as_view(template_name='orders.html'), name='orders'),
    path('admin1/', TemplateView.as_view(template_name='admin/dashboard.html'), name='admin-dashboard'),
    path('admin1/appointments/', TemplateView.as_view(template_name='admin/appointments.html'), name='admin-appointments'),
    path('admin1/products/', TemplateView.as_view(template_name='admin/products.html'), name='admin-products'),
    path('admin1/orders/', TemplateView.as_view(template_name='admin/orders.html'), name='admin-orders'),
    path('admin1/reports/', TemplateView.as_view(template_name='admin/reports.html'), name='admin-reports'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
