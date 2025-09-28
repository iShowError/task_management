from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name'] 
        read_only_fields = ['id', 'username', 'first_name', 'last_name']

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    assigned_to = serializers.CharField(write_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'assigned_to', 'assigned_to_username', 'status', 'due_date', 'created_at', 'updated_at', 'created_by_username']
        read_only_fields = ['created_at', 'updated_at', 'assigned_to_username', 'created_by_username']
    
    def validate(self, data):
        if 'title' not in data or not data['title'].strip():
            raise serializers.ValidationError({"title": "Title is required."})

        if 'assigned_to' not in data or not data['assigned_to'].strip():
            raise serializers.ValidationError({"assigned_to": "Assigned user is required."})
        
        # Check if the assigned user exists.
        try:
            username = data.get('assigned_to')
            assigned_user = User.objects.get(username=username)
            data['assigned_to'] = assigned_user # Replace username with User object
        except User.DoesNotExist:
            raise serializers.ValidationError({"assigned_to": f"User '{username}' does not exist."})
        
        # Check for duplicate tasks (same title assigned to the same user)
        if Task.objects.filter(title=data['title'], assigned_to=data['assigned_to']).exists():
            raise serializers.ValidationError("A task with this title already exists for this user.")
        return data
    
    def create(self, validated_data):
        return super().create(validated_data)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value