from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Payment.PaymentStatus.choices, read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'user', 'amount', 'status', 'created_at', 'closed_at']
        read_only_fields = ['id', 'created_at', 'closed_at']

    def create(self, validated_data):
        user = self.context.get('request').user
        validated_data.pop('user', None)
        return Payment.objects.create(user=user, **validated_data)