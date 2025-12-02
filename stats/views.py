from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext_lazy as _
from django_pandas.io import read_frame
from translations.models import Translation
from payments.models import Payment  # Імпортуємо лише Payment
from users.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .serializers import TranslationSerializer, DailyStatsSerializer
from .models import DailyStats
from django.utils import timezone

class StatsViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['date', 'source_lang', 'target_lang', 'created_at']
    ordering_fields = ['date', 'created_at', 'source_lang', 'target_lang']

    def get_queryset(self):
        if not self.request.user.is_admin:
            return DailyStats.objects.none()
        return DailyStats.objects.all()

    def list(self, request, *args, **kwargs):
        print(f"User: {request.user.username}, Is Admin: {request.user.is_admin}")
        if not request.user.is_admin:
            return Response({"error": _("Only admins can access stats"), "user": request.user.username}, status=status.HTTP403_FORBIDDEN)

        try:
            translations = Translation.objects.all()
            payments = Payment.objects.filter(status=Payment.PaymentStatus.SUCCESS)
            users = User.objects.all()

            translations_df = read_frame(translations, fieldnames=['id', 'user', 'created_at', 'source_lang', 'target_lang'])
            payments_df = read_frame(payments, fieldnames=['id', 'user', 'amount', 'created_at', 'status'])
            users_df = read_frame(users, fieldnames=['id', 'username', 'created_at'])

            print("Translations DF:", translations_df)
            print("Payments DF:", payments_df)
            print("Users DF:", users_df)

            total_translations = len(translations_df)
            total_revenue = payments_df['amount'].sum() if not payments_df.empty else 0
            average_check = total_revenue / len(payments_df) if len(payments_df) > 0 else 0
            total_users = len(users_df)
            users_with_translations = len(translations_df['user'].dropna().unique())

            today = timezone.now().date()
            stats, created = DailyStats.objects.get_or_create(date=today)
            stats.total_translations = total_translations
            stats.total_revenue = total_revenue
            stats.average_check = average_check
            stats.total_users = total_users
            stats.users_with_translations = users_with_translations
            stats.save()

            filterset = {
                'user': request.query_params.get('user'),
                'source_lang': request.query_params.get('source_lang'),
                'target_lang': request.query_params.get('target_lang'),
                'created_at__gte': request.query_params.get('date_from'),
                'created_at__lte': request.query_params.get('date_to'),
            }

            user_id = request.query_params.get('user')
            if user_id and user_id.isdigit():
                filterset['user'] = int(user_id)

            filterset = {k: v for k, v in filterset.items() if v is not None}

            filtered_translations = Translation.objects.filter(**filterset).select_related('payment','user')
            ordering = request.query_params.get('ordering', '-created_at')
            ordered_translations = filtered_translations.order_by(ordering)

            translations_serializer = TranslationSerializer(ordered_translations, many=True)

            return Response({
                "daily_stats": DailyStatsSerializer(stats).data,
                "translations": translations_serializer.data,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        return Response({"error": _("Stats cannot be created manually")}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        return Response({"error": _("Stats cannot be updated manually")}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        return Response({"error": _("Stats cannot be deleted manually")}, status=status.HTTP_403_FORBIDDEN)