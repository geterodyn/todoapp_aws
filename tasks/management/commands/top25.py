from django.core.management import BaseCommand
# from datetime import datetime, timezone
from tasks.models import TodoItem
from django.contrib.auth.models import User

from collections import Counter

class Command(BaseCommand):
    help = u"Display list of top 25 users with highest number of tasks"

    def add_arguments(self, parser):
        parser.add_argument('--top', dest='top', type=int, default=25)

    def handle(self, *args, **kwargs):
        total_user_list=[]
        unc_dict = {}
        less20 = 0
        for u in User.objects.all():
            unc_dict[u] = len(TodoItem.objects.filter(owner=u).filter(is_completed=False))
            for t in u.tasks.all():
                total_user_list.append(u)
        c = Counter(total_user_list)
        print(f"Топ {kwargs['top']} пользователей по количеству задач:")

        for user, count in c.most_common(kwargs['top']):
            print(f'{user}: {count} задач, из них {len(TodoItem.objects.filter(owner=user).filter(is_completed=True))} выполнены')

        # Количество пользователей, у которых менее 20 невыполненных задач
        for num in unc_dict.values():
            if num < 20:
                less20 += 1
        print(less20)

        # Имя пользователя, стоящего на втором месте по количеству невыполненных задач
        for k,v in unc_dict.items():
            if v == sorted(list(unc_dict.values()))[-2]:
                print(k)

