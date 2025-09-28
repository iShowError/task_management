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
        fields = ['id', 'title', 'description', 'assigned_to', 'assigned_to_username', 'created_by_username', 'status', 'due_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'assigned_to_username', 'created_by_username']
    
    def validate(self, data):
        # Handle updates (PATCH requests)
        if self.instance:
            # Permission check: User can only update tasks they created or are assigned to
            user = self.context['request'].user
            if not (self.instance.created_by == user or self.instance.assigned_to == user):
                raise serializers.ValidationError("You do not have permission to edit this task.")
            
            # Check if user tries to update forbidden fields
            forbidden_fields = {
                'id': 'Task ID is automatically assigned and cannot be changed.',
                'created_by': 'Task creator cannot be changed after creation.',
                'created_at': 'Creation timestamp is automatically set and cannot be modified.',
                'updated_at': 'Update timestamp is automatically managed by the system.',
                'created_by_username': 'This is a read-only field derived from the task creator.',
                'assigned_to_username': 'This is a read-only field derived from the assigned user.'
            }
            
            for field in forbidden_fields:
                if field in self.initial_data:
                    raise serializers.ValidationError({field: forbidden_fields[field]})
            
            # Convert assigned_to username to User object if provided
            if 'assigned_to' in data:
                try:
                    user_obj = User.objects.get(username=data['assigned_to'])
                    data['assigned_to'] = user_obj
                except User.DoesNotExist:
                    raise serializers.ValidationError({"assigned_to": f"User '{data['assigned_to']}' does not exist."})
        
        # Handle creation (POST requests)  
        else:
            # Required fields validation
            if not data.get('title', '').strip():
                raise serializers.ValidationError({"title": "Title is required."})
            
            if not data.get('assigned_to', ''):
                raise serializers.ValidationError({"assigned_to": "Assigned user is required."})
            
            # Convert assigned_to username to User object
            try:
                user_obj = User.objects.get(username=data['assigned_to'])
                data['assigned_to'] = user_obj
            except User.DoesNotExist:
                raise serializers.ValidationError({"assigned_to": f"User '{data['assigned_to']}' does not exist."})
            
            # Check for duplicate title for same user
            if Task.objects.filter(title=data['title'], assigned_to=data['assigned_to']).exists():
                raise serializers.ValidationError({"title": "A task with this title already exists for this user."})
        
        return data

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