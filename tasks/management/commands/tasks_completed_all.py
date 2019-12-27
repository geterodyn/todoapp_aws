from django.core.management import BaseCommand
# from datetime import datetime, timezone
from tasks.models import TodoItem
# from django.contrib.auth.models import User

class Command(BaseCommand):
    help = u"Display number of completed tasks"

    # def add_arguments(self, parser):
    #     parser.add_argument('--warning-days', dest='warn_days', type=int, default=5)

    def handle(self, *args, **kwargs):
        print(len(TodoItem.objects.filter(is_completed=True)))