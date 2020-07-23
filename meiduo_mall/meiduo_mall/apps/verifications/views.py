from django.shortcuts import render
from django import http
from django.views import View
# Create your views here.
from verifications.libs.captcha.captcha import captcha
from django_redis import get_redis_connection

class IdentifiedIame(View):

    def get(self, request, image):
        text, img = captcha.generate_captcha()
        redis_db = get_redis_connection("identified")
        redis_db.setex("img_%s" % image, 200, text)
        return http.HttpResponse(img, content_type="image/jpg")


