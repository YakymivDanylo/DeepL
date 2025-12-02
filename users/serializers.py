from rest_framework import serializers
from .models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    is_admin = serializers.BooleanField(default=False,required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2','is_admin')
        extra_kwargs = {'password': {'write_only': True},
                        'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": 'Passwords must match'})

        password = attrs['password']
        if len(password) < 6:
            raise serializers.ValidationError({"password": 'Password must be at least 6 characters long'})
        if not any(char.isdigit() for char in password ):
            raise serializers.ValidationError({"password": 'Password must contain at least one number'})
        if not any(char.isupper() for char in password):
            raise serializers.ValidationError({"password": 'Password must contain at least one uppercase letter'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        is_admin = validated_data.pop('is_admin', False)

        request_user = self.context.get('request').user
        if request_user.is_authenticated and not request_user.is_admin and is_admin:
            raise serializers.ValidationError({"is_admin": 'Only admins can create admin users'})

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_admin=is_admin
        )
        return user

    def update(self, instance, validated_data):
        if 'is_admin' in validated_data and not self.context.get('request').user.is_admin:
            raise serializers.ValidationError({"is_admin": 'Only admins can update admin users'})
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance, validated_data)
