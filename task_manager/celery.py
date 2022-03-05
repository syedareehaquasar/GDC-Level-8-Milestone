import os
from django.conf import settings
from celery import Celery
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_manager.settings')

app = Celery('task_manager')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

from datetime import timedelta

from celery.decorators import periodic_task
from django.core.mail import send_mail


@periodic_task(run_every=timedelta(seconds=5))
def send_report(user):
    from tasks.models import Report, Task

    def user_tasks(user):
        print("In user_task")
        tasks = Task.objects.filter(user=user, completed=False, deleted=False).order_by("status")
        return {
            "name": user.username.capitalize(),
            "status": dict(tasks)
        }
    
    tasks = user_tasks(user)
    if not tasks:
        report = "\n No tasks scheduled! \n"
    else:
        report = f"Hey {user}! \n Here is your task report for today: \n"
        report += json.dumps(tasks)
    
    send_mail("Daily Tasks Status Report [Task Manager]", report, "tasks@gdc.com", ["syedareehaquasar@gmail.com"])