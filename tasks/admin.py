from django.contrib import admin
from tasks.models import TodoItem
# Register your models here.

@admin.register(TodoItem)
class TodoItemAdmin(admin.ModelAdmin):
	list_display = ('description', 'is_completed', 'created')