from django.core.management import BaseCommand
from tasks.models import TodoItem

class Command(BaseCommand):
    help = u"adds tasks with descriptions from the list"

    def add_arguments(self, parser):
        parser.add_argument('--file', dest='input_file', type=str)

    def handle(self, *args, **kwargs):
        with open(kwargs['input_file']) as f:
            for desc in f:
                t = TodoItem(description=desc)
                t.save()