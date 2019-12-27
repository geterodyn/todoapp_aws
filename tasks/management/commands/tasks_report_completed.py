from django.core.management import BaseCommand
from datetime import datetime, timezone
from tasks.models import TodoItem

class Command(BaseCommand):
    help = u"all tasks completed in the last `days` days (default=3 days)"

    def add_arguments(self, parser):
        parser.add_argument('--days', dest='days', type=int, default=3)

    def handle(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        for t in TodoItem.objects.filter(is_completed=True):
            if (now - t.updated).days <= kwargs['days']:
                print(f"Завершенные задачи за {kwargs['days']} дней: {t}, {t.updated}")