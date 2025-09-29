from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Task
from .serializers import TaskSerializer, UserRegistrationSerializer, UserListSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ReadOnlyModelViewSet
from django.db import models
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

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

class UserLogoutView(APIView):
    #endpoint for user logout
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get the user's token and delete it
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            # Handle case where token doesn't exist (already deleted)
            return Response({'message': 'You are already logged out'}, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle any other unexpected errors
            return Response(
                {'error': 'An error occurred during logout. Please try again.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
        user = self.request.user
        if not instance.created_by:
            raise PermissionDenied("This task has no creator and cannot be deleted.")
        elif instance.created_by == user:
            instance.delete()
        else:
            raise PermissionDenied("Only the task creator can delete this task.")
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Task deleted successfully'}, status=status.HTTP_200_OK)