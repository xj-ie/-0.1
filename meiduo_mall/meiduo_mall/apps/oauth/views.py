from django.shortcuts import render, redirect, reverse
from django.views import View
from django.conf import settings
from QQLoginTool.QQtool import OAuthQQ
from django import http
from oauth.models import OAuthQQUser
from django.contrib.auth import login
import logging, re
from oauth.uilts import Serializer
from users.models import User

logging.getLogger('django')


# Create your views here.
class QQLoginViews(View):
    def get(self, request):


        oauthqq = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI, state="next")

        login_url = oauthqq.get_qq_url()



        return http.JsonResponse({'code': 1, "errmsg": "ok", "login_url": login_url})

class QQ_SESSION_ID(View):
    def get(self, request):

        code = request.GET.get("code")

        if not code:
            return http.HttpResponseForbidden('EREER:501')
        oauthqq = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI, state="next")
        try:
            access_token = oauthqq.get_access_token(code)
            open_id = oauthqq.get_open_id(access_token)
        except Exception as e:
            logging.error(e)
            return http.HttpResponseForbidden('django_qq_exain:flase')
        try:
            oauthqq_user = OAuthQQUser.objects.get(openid=open_id)
        except OAuthQQUser.DoesNotExist:
            s = Serializer()
            context = {"access_token_openid": s.dupmsl(open_id).decode('utf-8')}
            return render(request, 'oauth_callback.html', context=context)
        else:
            login(request, oauthqq_user.users)
            response = render(reverse('Contents:index'))
            response.set_cookie('username', oauthqq_user.user.username, max_age=3000*24*30)
            return response

    def post(self, request):
        data = request.POST
        data = dict(data).values()
        print(data)
        if not all(data):
            return http.HttpResponseForbidden(501)
        if not re.match(r'1[3-9]\d{9}', data[1]):
            return http.HttpResponseForbidden('Phone:ERROR')
        if not re.match(r'[a-zA-Z0-9-_]{8,20}', data[2]):
            return http.HttpResponseForbidden('password:ERROR')

        s = Serializer()
        try:
            s.loadsl(data[-1])
        except Exception:
            return http.HttpResponseForbidden(501)
        # try:
        #     user = User.objects.get(mobile=data[1])
        #
        #
        # except User.DoesNotExist:
        #     OAuthQQUser.objects.create(user=user, openid=data[1])
        #     user =User.objects.create_user(mobile=data[1],username=data[1],password=data[2])
        #     login(user)
        #     return redirect('/')
        # else:
        #     OAuthQQUser.objects.create(user = user,openid=data[1])
        #     login(user.username)
        #     return redirect('/')





        return http.JsonResponse(dict(data))




