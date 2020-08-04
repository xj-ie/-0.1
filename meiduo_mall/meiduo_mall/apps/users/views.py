from django.shortcuts import render, reverse, redirect
from django.views import View
from django import http
import re
from celery_tasks.email.tasks import send_verify_email
# import phone
from users.models import User, Address
from django.db import DatabaseError
from django.contrib.auth import login, logout
from meiduo_mall.utils.response_code import RETCODE
from django_redis import get_redis_connection
from users.utils import UsernameMobileBackend

from users.utils import generate_verify_email_url, decorate_verify_email_url
import json
from django.contrib.auth.mixins import LoginRequiredMixin

from meiduo_mall.utils.views import LoginRequireJSONdMixin
# import json
# Create your views here.
import logging

logging.getLogger('django')

class OrdersViews(View):
    def get(self, request):
        user_login = request.user
        addresses = Address.objects.filter(user_id=user_login, is_deleted=False)
        address_dict_list =[{
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            } for address in addresses]
        context = {
            'default_address_id': user_login.default_address or '0',
            'addresses': address_dict_list,
        }


        return render(request, "user_center_site.html", context)

class AddressCreateView(LoginRequireJSONdMixin, View):
    def post(self, request):
        pass


class Emali_Verifications(View):
    def get(self, request):
        token = request.GET.get()
        if not token:
            return http.HttpResponseForbidden('501')
        user = decorate_verify_email_url(token)
        if not user:
            return http.HttpResponseForbidden('404')
        user.email_activate=True
        user.save()
        return render(reverse("users:email"))

class EmailView(LoginRequireJSONdMixin, View):
    def put(self, request):
        json_str = json.loads(request.body.decode('utf-8'))
        email = json_str.get("email")
        # if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.a-z]{2,5}){1.2}$', email):
        #     logging.error("X:email:eroor")
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email有误')

        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logging.error(e)
            return http.JsonResponse({"code": 1, "errmsg": 'db:save_ERROR'})
        user = request.user
        # data = {"user": user.username, 'email': user.email}
        # s = SECRET_key(SECRET_TXT())
        # data = s.dumpsl(data)
        # verify_url="http://www.meiduo.site:8000/email/verification/?token=" + str(data)
        # 邮件的激活网址
        verify_url = generate_verify_email_url(request.user)

        send_verify_email.delay(email, verify_url)
        return http.JsonResponse({"code": 0, "errmsg": 'safe'})

class UserInfoView(LoginRequiredMixin, View):

    def get(self, request):


        context = {"name" : request.user.username,
                   "phone" : request.user.mobile,
                   "email" : request.user.email,
                   "email_activate" : request.user.email_active}




        return render(request, "user_center_info.html", context=context)


class LogOut(View):
    def get(self, request):
        logout(request)
        response = redirect(reverse("Contents:index"))
        response.delete_cookie("username")

        return response


class LoginView(View):
    def get(self, request):
        return render(request, "login.html")
    def post(self, request):
        data_i = request.POST
        usernmae = data_i.get("username")
        password = data_i.get("password")
        remembered = data_i.get("remembered")


        if not re.match(r"[a-zA-Z0-9]{5,20}", usernmae):
            return http.HttpResponseForbidden("501")
        if not re.match(r"[a-zA-Z0-9-_]{8,16}", password):
            return http.HttpResponseForbidden("501")

        if not all([usernmae, password]):
            return http.HttpResponseForbidden("501")
        userba =UsernameMobileBackend()
        user = userba.authenticate(request=request, username=usernmae, password=password)

        if user is None:
            return render(request,'login.html',{'account_errmsg':'123'})

        nexts = request.GET.get("next")
        if nexts:
            response = redirect(nexts)
        else:
            response = redirect(reverse("Contents:index"))
        response.set_cookie("username", user.username, max_age=3600*12*24)
        login(request, user)
        if remembered == "on":
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)

        return response

class UserCountView(View):

    def get(self, request, usrname):
        conut = User.objects.filter(username=usrname).count()

        reault = {"code": RETCODE.OK, "errmag": "OK", "conut": conut}

        return http.JsonResponse(reault)
class PhoneCountView(View):

    def get(self, request, phone):
        conut = User.objects.filter(mobile=phone).count()

        reault = {"code": RETCODE.OK, "errmag": "OK", "conut": conut}

        return http.JsonResponse(reault)



class RegisterView(View):
    """register user"""

    def get(self, request):

        """commit reister view"""

        return render(request, "register.html")

    def post(self, request):

        """excute reister realize"""
        response = request.POST
        response = dict(response)
        is_unll = [i[0] for i in response.values()]
        print(is_unll)
        if not all(is_unll):
            return http.HttpResponseForbidden("error_file: commit data message  500")

        if not re.match(r"^[a-zA-Z0-9_-]{5,20}", is_unll[1]):
            return http.HttpResponseForbidden('error_file: username type info NOT 404')
        if not re.match(r"[0-9A-Za-z]{8,20}", is_unll[2]):
            return http.HttpResponseForbidden("error_file: pass type info not 404")
        if is_unll[2] != is_unll[3]:
            return http.HttpResponseForbidden("error_file:commit password info not 404")
        if not re.match(r"^1[3-9]\d{9}$", is_unll[4]):
            return http.HttpResponseForbidden("error_phone:commit phone info not 404")
        if is_unll[-1] != "on":
            return http.HttpResponseForbidden('506')
        if is_unll[-2] is None:
            return render(request, "reister.html", {"error_message_msg":"不能为空"})
        conn_ext = get_redis_connection("identified")
        ssm_code = conn_ext.get("+86%s"%is_unll[4])
        if is_unll[-2] != ssm_code:
            return render(request, "reister.html", {"error_message_msg":"验证码有𢇞"})


        else:
            try:
                users = User.objects.create_user(username=is_unll[1], password=is_unll[2], mobile=is_unll[4])
            except Exception as err:
                print(err)
                return render(request, "register.html", {"register_error": "register:404"})
            # return render(request, "register.html")
            # return http.HttpResponseForbidden(f"{phone.Phone().find(is_unll[4])}")
            login(request, users)
            return redirect(reverse("Contents:index"))