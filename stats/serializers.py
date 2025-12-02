from rest_framework import serializers
from payments.serializers import PaymentSerializer
from users.serializers import UserSerializer
from translations.serializers import TranslationSerializer
from payments.models import Payment
from translations.models import Translation
from .models import DailyStats

class TranslationSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = Translation
        fields = '__all__'


class DailyStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStats
        fields = '__all__'