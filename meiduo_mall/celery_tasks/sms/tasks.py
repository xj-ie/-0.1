from celery_tasks.sms.checkt_phone import CCP
from celery_tasks import main

@main.celery_app.task(name="send_sms_code")
def send_sms_code(txt_code, phone):
    CCP().get_conde(txt_code, phone)