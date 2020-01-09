from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
path('', views.index, name='index'),
# path('list/', views.TaskListView.as_view(), name='list'),
path('list/', views.tasks_by_tag, name='list'),
path('list/<slug:tag_slug>', views.tasks_by_tag, name='list_by_tag'),
path('create/', views.TaskCreateView.as_view(), name='create'),
path('add-task/', views.add_task, name='api-add-task'),
path('complete/<int:uid>', views.complete_task, name='complete'),
path('delete/<int:uid>', views.delete_task, name='delete'),
path('delete/<int:uid>/<slug:tag_slug>', views.delete_task, name='delete_by_tag'),
path('details/<int:pk>', views.TaskDetailView.as_view(), name='details'),
path('edit/<int:pk>', views.TaskEditView.as_view(), name='edit'),
path('export/', views.TaskExportView.as_view(), name='export'),
path('uncompleted/', views.UncompletedTaskListView.as_view(), name='uncompleted'),
path('grouped/', views.GroupedTaskListView.as_view(), name='grouped'),
]

