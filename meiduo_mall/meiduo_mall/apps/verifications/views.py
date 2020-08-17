from django.shortcuts import render
from django import http
from django.views import View
# Create your views here.
from goods.models import SKU
from verifications.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from meiduo_mall.utils import constants
import random
from meiduo_mall.utils import checkt_phone
from celery_tasks.sms.tasks import send_sms_code

class SMSCondeView(View):
    def get(self, request, phone):#phone:18478
        conn = get_redis_connection("identified")
        index = conn.get("index%s"%(phone))
        # "index%s" % (phone)
        img_code = request.GET.get("img_code")
        uuid = request.GET.get("uuid")
        if not all([uuid, img_code]):
            return http.HttpResponseForbidden("gi ce yl pw ")


        image_conde = conn.get(f"img_{uuid}")
        conn.delete(f"img_{uuid}")
        if image_conde is None:
            return http.JsonResponse({"code": 1, "errmsg": "img_code:NONE"})
        if image_conde.upper() != img_code.encode("utf-8").upper():
            return http.JsonResponse({"code": 1, "errmsg": "img_conde:ERROR"})

        txt_code = "%06d"%(random.randint(0, 999999))
        phone = "+86"+phone
        if not index is None:
            return http.JsonResponse({"code": 2, "errmsg": "img_conde:注册过于频繁"})
        # yield http.JsonResponse({"code": 0, "errmsg": "info"})

        conn_redis = get_redis_connection("identified").pipeline()
        # send_sms_code.delay(txt_code, phone)
        checkt_phone.CCP().get_conde(txt_code, phone)
        conn_redis.setex(phone, 400, txt_code)
        conn_redis.setex("index%s"%(phone), 400, 1)
        conn_redis.execute()
        return http.JsonResponse({"code": 0, "errmsg": "info"})



class IdentifiedIame(View):

    def get(self, request, image):
        text, img = captcha.generate_captcha()
        redis_db = get_redis_connection("identified")
        redis_db.setex("img_%s" % image, 400, text)
        return http.HttpResponse(img, content_type="image/jpg")


class Test_View(View):
    def get(self,request):
        skus = SKU.objects.all()
        dist_dect = [sku.__dict__ for sku in skus]
        # context = {'contex':dist_dect}
        return http.JsonResponse(dist_dect, safe=False)

