from rest_framework import serializers

from payments.models import Payment
from payments.serializers import PaymentSerializer
from users.serializers import UserSerializer
from .models import Translation
from django.utils.translation import gettext_lazy as _


class TranslationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Translation
        fields = [
            'id',
            'user',
            'payment',
            'source_text',
            'translated_text',
            'source_lang',
            'target_lang',
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'payment', 'translated_text', 'created_at']

    def validate(self, attrs):
        source_text = attrs.get('source_text')
        source_lang = attrs.get('source_lang')
        target_lang = attrs.get('target_lang')

        if len(source_text) > 50000:
            raise serializers.ValidationError(
                {"source_text": _("Source text must be shorter than 50000 characters")}
            )
        if source_lang == target_lang:
            raise serializers.ValidationError(
                {"target_lang": _("Target language must be different than source language")}
            )
        return attrs

    def create(self, validated_data):
        payment_id = self.context.get("payment_id")
        if not payment_id:
            raise serializers.ValidationError({"payment": _("Payment is required")})

        payment = Payment.objects.get(id=payment_id)
        user = payment.user

        return Translation.objects.create(
            user=user,
            payment=payment,
            **validated_data
        )
