from django.core.management import BaseCommand
from datetime import datetime, timezone
from tasks.models import TodoItem

class Command(BaseCommand):
    help = u"Display not yet completed tasks' dates"

    def add_arguments(self, parser):
        parser.add_argument('--warning-days', dest='warn_days', type=int, default=5)

    def handle(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        for t in TodoItem.objects.filter(is_completed=False):
            if (now - t.created).days >= kwargs['warn_days']:
                print('Старая задача:', t, t.created)