from django.core.serializers import serialize
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from translations.models import Translation
from translations.serializers import TranslationSerializer


# Create your views here.
class TranslationViewSet(viewsets.ModelViewSet):
    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['source_lang','target_lang','created_at']
    ordering_fields = ['created_at','source_lang','target_lang']
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Translation.objects.all()
        return Translation.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        payment_id = request.data.get('payment_id')
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request, 'payment_id': payment_id}
        )
        serializer.is_valid(raise_exception=True)
        translation = serializer.save()
        return Response(serializer.data, status=201)

    def update(self,request,*args,**kwargs):
        return Response(
            {"Error":_("Translation cnnot be updated")},
            status=status.HTTP_403_FORBIDDEN,
        )

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response(
                {"Error":_("Only admins can delete translations")},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_translations(self, request):
        queryset = self.filter_queryset(self.get_queryset().filter(user=request.user))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)