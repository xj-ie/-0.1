import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")

celery_app = Celery("meiduo")

celery_app.config_from_object("celery_tasks.conf")

celery_app.autodiscover_tasks(["celery_tasks.sms", "celery_tasks.email"])