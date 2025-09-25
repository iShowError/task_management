from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'status', 'due_date', 'created_at', 'updated_at')
    list_filter = ('status', 'due_date', 'assigned_to')
    search_fields = ('title', 'description', 'assigned_to__username')