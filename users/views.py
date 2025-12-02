from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from users.models import User
from users.serializers import UserSerializer
from rest_framework.authtoken.models import Token


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication,SessionAuthentication]

    def get_permissions(self):
        if self.action in ['create', 'login']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user':serializer.data,
            'token': token.key,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request,user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username':user.username,
                'email':user.email,
                'is_admin':user.is_admin
            }, status=status.HTTP_200_OK)
        return Response({"Error":"Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        request.user.auth_token.delete()
        logout(request)
        response = Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_200_OK
        )
        response.delete_cookie('auth')
        response.delete_cookie('csrftoken')
        response.delete_cookie('sessionid')

        response["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        if request.user.is_admin or request.user.id == int(kwargs.get('pk')):
            return super().update(request, *args, **kwargs)
        return Response({"Error":"Permission Denied"}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if request.user.is_admin:
            return super().destroy(request, *args, **kwargs)
        return Response({"Error":"Permission Denied"}, status=status.HTTP_403_FORBIDDEN)