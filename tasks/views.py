from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Task
from .serializers import TaskSerializer, UserRegistrationSerializer, UserListSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.db import models

class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserListSerializer 
    permission_classes = [IsAuthenticated]

class UserRegistrationView(generics.CreateAPIView):
    #API endpoint for user registration
    serializer_class = UserRegistrationSerializer
    permission_classes = [] 

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({'message': 'User successfully registered'}, status=status.HTTP_201_CREATED)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(models.Q(assigned_to=user) | models.Q(created_by=user)).distinct()
        
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        task = serializer.instance
        user = self.request.user
        if task.created_by == user or task.assigned_to == user:
            serializer.save()
        else:
            raise PermissionDenied("You do not have permission to edit this task.")

    def perform_destroy(self, instance):
        if instance.created_by == self.request.user:
            instance.delete()
        else:
            raise PermissionDenied("You do not have permission to delete this task.")