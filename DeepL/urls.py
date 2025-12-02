from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from payments.views import PaymentViewSet, wfp_callback
from stats.views import StatsViewSet
from translations.views import TranslationViewSet
from users.views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'translations', TranslationViewSet, basename='translations')
router.register(r'payments', PaymentViewSet, basename='payments')
router.register(r'stats', StatsViewSet, basename='stats')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/wfp_callback/', wfp_callback, name='wfp_callback'),
    path('admin/', admin.site.urls),
    path('api/auth/', obtain_auth_token, name='api-token-auth'),
]
