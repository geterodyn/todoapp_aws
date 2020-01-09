from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.conf import settings
from taggit.models import Tag

from tasks.models import TodoItem
from tasks.forms import AddTaskForm, TodoItemForm, TasksExportForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView

# Create your views here.
@login_required
def index(request):
	counts = Tag.objects.annotate(
		total_tasks=Count('todoitem')
	).order_by('-total_tasks')

	counts = {
		c.name: c.total_tasks
		for c in counts
	}
	# counts = {
	# 	t.name: t.taggit_taggeditem_items.count()
	# 	for t in Tag.objects.all()
	# 	}
	return render(request, 'tasks/index.html', {'counts': counts})

def task_count(request):
	total = TodoItem.objects.filter(owner=request.user).count()
	completed = TodoItem.objects.filter(is_completed=True).count()
	return render(request, 'base.html', {'total': total, 'completed': completed})

def complete_task(request, uid):
	t = TodoItem.objects.get(id=uid)
	t.is_completed = True
	t.save()
	return HttpResponse('OK')

def add_task(request):
	if request.method == 'POST':
		desc = request.POST['description']
		t = TodoItem(description=desc)
		t.save()
		messages.success(request,'Задача добавлена')
	return redirect(reverse('tasks:list'))

def delete_task(request, uid, tag_slug=None):
	t = TodoItem.objects.get(id=uid)
	t.delete()
	messages.success(request, 'Задача удалена')
	return redirect(reverse('tasks:list_by_tag',args=[tag_slug])) if tag_slug else redirect(reverse('tasks:list'))

# def task_create(request):
# 	if request.method == 'POST':
# 		form = TodoItemForm(request.POST)
# 		if form.is_valid():
# 			form.save()
# 			return redirect('/tasks/list')
# 	else:
# 		form = AddTaskForm()
# 	return render(request, 'tasks/create.html', {'form': form}) # ключ словаря - то, что мы используем в шаблоне в {{}},
# 													# значение словаря - то, что мы определяем в данном обработчике

def filter_tags(tags_by_task):
	return list(set(sum(tags_by_task, [])))

# def filter_tasks(tasks, tag):
# 	return [entry['task_id'] for entry in tasks if str(tag) in entry['tags']]

def tasks_by_tag(request, tag_slug=None):
	u = request.user
	tasks = TodoItem.objects.filter(owner=u).all()

	tag = None
	if tag_slug:
		tag = get_object_or_404(Tag, slug=tag_slug)
		tasks = tasks.filter(tags__in=[tag])

	all_tags = filter_tags([list(t.tags.all()) for t in tasks])

	return render(request, 'tasks/list_by_tag.html', {'tag': tag, 'tasks': tasks, 'all_tags': all_tags})
	

class TaskListView(LoginRequiredMixin, ListView):
	# queryset = TodoItem.objects.all()
	model = TodoItem
	context_object_name = 'tasks'
	template_name = 'tasks/list.html'

	def get_queryset(self):
		u = self.request.user
		return u.tasks.all()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		user_tasks = self.get_queryset()
		tags = []
		for t in user_tasks:
			tags.append(list(t.tags.all()))

		context['tags'] = filter_tags(tags)
		return context
		
class UncompletedTaskListView(LoginRequiredMixin, ListView):
	model = TodoItemForm
	context_object_name = 'tasks'
	template_name = 'tasks/list.html'

	def get_queryset(self):
		u = self.request.user
		return u.tasks.filter(is_completed=False)

class GroupedTaskListView(LoginRequiredMixin, ListView):
	model = TodoItem
	context_object_name = 'tasks'
	template_name = 'tasks/grouped_list.html'

	def get_queryset(self):
		u = self.request.user
		return u.tasks.all()	

class TaskCreateView(View):
	def post(self, request, *args, **kwargs):
		form = TodoItemForm(request.POST)
		if form.is_valid():
			new_task = form.save(commit=False)
			new_task.owner = request.user
			new_task.save()
			form.save_m2m()
			messages.success(request, 'Задача создана')
			return redirect(reverse('tasks:list'))

		return render(request, 'tasks/create.html', {'form': form})
	
	def get(self, request, *args, **kwargs):
		form = TodoItemForm()
		return render(request, 'tasks/create.html', {'form': form})

class TaskDetailView(DetailView):
	model = TodoItem
	template_name = 'tasks/details.html'

class TaskEditView(LoginRequiredMixin, View):
	def post(self, request, pk, *args, **kwargs):
		t = TodoItem.objects.get(id=pk)
		form = TodoItemForm(request.POST, instance=t)
		if form.is_valid():
			new_task = form.save(commit=False)
			new_task.owner = request.user
			new_task.save()
			messages.success(request, 'Задача изменена')
			return redirect(reverse('tasks:list'))
		return render(request, 'tasks/edit.html', {'form': form, 'task': t})

	def get(self, request, pk, *args, **kwargs):
		t = TodoItem.objects.get(id=pk)
		form = TodoItemForm(instance=t)
		return render(request, 'tasks/edit.html', {'form': form, 'task': t})

class TaskExportView(LoginRequiredMixin, View):
	
	def generate_body(self, user, priorities):
		q = Q()
		if priorities['prio_high']:
			q = q | Q(priority=TodoItem.PRIORITY_HIGH)
		if priorities['prio_med']:
			q = q | Q(priority=TodoItem.PRIORITY_MEDIUM)
		if priorities['prio_low']:
			q = q | Q(priority=TodoItem.PRIORITY_LOW)

		tasks = TodoItem.objects.filter(owner=user).filter(q).all()
		
		if not priorities['group']:
			body = 'Ваши задачи и приоритеты:\n'
			for t in tasks:
				tags = ', '.join([tag.name for tag in t.tags.all()])
				if t.is_completed:
					body += f"[x] {t.description} (тэги: {tags}) ({t.get_priority_display()})\n"
				else:
					body += f"[ ] {t.description} (тэги: {tags}) ({t.get_priority_display()})\n"
		else:
			body = 'Ваши задачи, сгруппированные по приоритетам:\n'
			prio = [TodoItem().PRIORITY_CHOICES[i][1] for i in range(3)]

			for i in range(len(prio)):
				body += '\n' + prio[i] + '\n'
				for t in tasks:
					tags = ', '.join([tag.name for tag in t.tags.all()])
					if t.get_priority_display() == prio[i]:
						if t.is_completed:
							body += f"[x] {t.description} (тэги: {tags})\n"
						else:
							body += f"[ ] {t.description} (тэги: {tags})\n"			
		return body

	def post(self, request, *args, **kwargs):
		form = TasksExportForm(request.POST)
		if form.is_valid():
			email = request.user.email
			body = self.generate_body(request.user, form.cleaned_data)
			send_mail('Мои задачи', body, settings.EMAIL_HOST_USER, [email])
			messages.success(request, 'Задачи были отправлены на почту %s' % email)
		else:
			messages.error(request, 'Что-то пошло не так, попробуйте ещё раз')
		return redirect(reverse('tasks:list'))

	def get(self, request, *args, **kwargs):
		form = TasksExportForm()
		return render(request, 'tasks/export.html', {'form': form})
