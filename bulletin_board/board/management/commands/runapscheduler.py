from datetime import timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.safestring import mark_safe
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from board.models import Event, Players


def send_fresh_events():
    today = timezone.now()
    last_week = today - timedelta(days=7)
    events = Event.objects.filter(time_create__gte=last_week,is_published=True)
    players = Players.objects.all()
    for player in players:
        filters_events = [e for e in events if player.guild in e.category.all() and player != e.player]
        if len(filters_events) > 0:
            html = render_to_string(template_name='send_fresh_events.html',
                                    context={'events': filters_events, 'player' : player})

            start = f'{"Уважаемый" if player.sex == "Male" else "Уважаемая"} {player.name}!\n'
            body = ''
            for event in filters_events:
                body += f'{event.title}\n' \
                        f'Категории: {list(event.category.all())}' \
                        f'Событие создал: {event.player}' \
                        f'Дата публикации: {event.time_create}' \
                        f'Участие могут принять только {[c.name for c in event.category.all()]}\n' \
                        f'Рекомендуемый уровень: {event.requirement_level}\n' \
                        f'{mark_safe(event.text)}\n' \
                        f'Награды за турнир:\n' \
                        f'{mark_safe(event.awards)}'
            text = start + body + '\n\nС уважением,\nКоманда Bulletin Board'
            msg = EmailMultiAlternatives(
                subject='Свежие объявления!',
                body=text,
                from_email=None,
                to=[player.user.email]
            )
            msg.attach_alternative(html, "text/html")
            msg.send()
    print(f'[{timezone.now()}] job send_fresh_events is done')


def delete_non_confirm_users():
    today = timezone.now()
    last_10_minutes = today - timedelta(minutes=10)
    users = get_user_model().objects.filter(confirm__registration_time__lte=last_10_minutes)
    if len(users) > 0:
        users.delete()

    print(f'[{timezone.now()}] job delete_non_confirm_users is done')

@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
    print(f'[{timezone.now()}] job delete_old_job_executions is done')


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            send_fresh_events,
            trigger=CronTrigger(day_of_week='mon',hour='12',minute='00',second="00"),
            id="send_fresh_events",
            max_instances=1,
            replace_existing=True,
        )
        print("Added job 'send_fresh_events'.")


        scheduler.add_job(
            delete_non_confirm_users,
            trigger=CronTrigger(minute='*/10'),
            id = 'delete_non_confirm_users',
            max_instances=1,
            replace_existing=True,
        )

        print("Added job 'delete_non_confirm_users'.")


        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        print("Added weekly job: 'delete_old_job_executions'.")

        try:
            print("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            print("Stopping scheduler...")
            scheduler.shutdown()
            print("Scheduler shut down successfully!")