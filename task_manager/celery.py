import time
import os

from django.core.mail import send_mail
from datetime import timedelta

from django.conf import settings
from celery import Celery
from celery.decorators import periodic_task

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

@periodic_task(run_every=timedelta(seconds=10))
def send_email_reminder():
    from django.contrib.auth.models import User
    from tasks.models import Task

    print("Starting to process Emails")
    for user in User.objects.all():
        pending_tasks = Task.objects.filter(user=user, completed=False, deleted=False)
        email_content = f"You have {pending_tasks.count()} Pending Tasks"
        send_mail("Pending Tasks from Tasks Manager", email_content, "tasks@task_manager.org", ["syedareehaquasar@gmail.com"])
        print(f"Completed Processing User {user.id}")

@app.task
def test_background_jobs():
    print("This is from bg")
    for i in range(10):
        time.sleep(1)
        print(i)