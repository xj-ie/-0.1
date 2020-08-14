from django.shortcuts import render, reverse, redirect
from django.views import View
from django import http
import re
from celery_tasks.email.tasks import send_verify_email
# import phone
from goods.models import SKU
from users.models import User, Address
from django.db import DatabaseError
from django.contrib.auth import login, logout
from meiduo_mall.utils.response_code import RETCODE
from django_redis import get_redis_connection
from users.utils import UsernameMobileBackend

from users.utils import generate_verify_email_url, decorate_verify_email_url
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from carts.utils import mcookie_to_redis
from meiduo_mall.utils.views import LoginRequireJSONdMixin
# import json
# Create your views here.
import logging
# from django_redis import get_redis_connection
# from carts.utils import mcookie_to_redis



logging.getLogger('django')
class UserBrowseHistory(LoginRequireJSONdMixin, View):
    def post(self, requst):
        sku_id = json.loads(requst.body.decode('utf-8')).get('sku_id')
        try:
            SKU.objects.get(id=sku_id)
        except Exception as e:
            return http.JsonResponse({'code':1, 'error':'alter'})
        user = requst.user
        redis_connect = get_redis_connection('history')
        pl = redis_connect.pipeline()
        pl.lrem('history_{}'.format(user.id), 0, sku_id)
        pl.lpush('history_{}'.format(user.id), sku_id)
        pl.ltrim('history_{}'.format(user.id), 0, 4)
        pl.execute()
        response = {'code': 0, 'error': 'info'}
        return http.JsonResponse(response)

    def get(self, request):
        user = request.user
        redis_connect = get_redis_connection('history')
        sku_id = redis_connect.lrange('history_{}'.format(user.id), 0, -1)

        sku_history = [SKU.objects.filter(id=sku) for sku in sku_id]
        print(sku_history)
        response = {
            "code":"0",
            "errmsg":"OK",
            "skus":[{
                "id": h[0].id,
                "name":h[0].name,
                "default_image_url":h[0].default_image.url,
                "price":h[0].price,
                } for h in sku_history]
        }

        return http.JsonResponse(response)
        # range


class UpdateTitleAddressView(LoginRequireJSONdMixin, View):
    def put(self,request, address_id):
        data = json.loads(request.body.decode)
        name = data.get("title")
        address = request.Address.get(address_id)
        address.title = name
        address.save()
        return http.JsonResponse({'code': 1, "errmsg": "salf"})


class UpdateDestroyAddressView(LoginRequireJSONdMixin, View):
    # def put(self, request, address_id):
    #     data = json.loads(request.body.decode())
    #
    #     receiver = data.get('receiver')
    #     province_id = data.get('province_id')
    #     city_id = data.get('city_id')
    #     district_id = data.get('district_id')
    #     place = data.get('place')
    #     mobile = data.get('mobile')
    #     tel = data.get('tel')
    #     email = data.get('email')
    #     # if not all([receiver, province_id, city_id, district_id, place, mobile]):
    #     #     return http.HttpResponseForbidden('缺少必传参数')
    #     # if not re.match(r'^1[3-9]\d{9}$', mobile):
    #     #     return http.HttpResponseForbidden('参数mobile有误')
    #     # if tel:
    #     #     if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
    #     #         return http.HttpResponseForbidden('参数tel有误')
    #     # if email:
    #     #     if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
    #     #         return http.HttpResponseForbidden('参数email有误')
    #
    #     user = request.user
    #     address = Address.objects.filter(id=address_id, user_id=user).update(
    #         user_id=user,
    #         title=receiver,
    #         receiver=receiver,
    #         province_id=province_id,
    #         city_id=city_id,
    #         district_id=district_id,
    #         place=place,
    #         mobile=mobile,
    #         tel=tel,
    #         email=email,
    #     )
    #
    #     response = {"code": 0, "errmsg": 'info',
    #                 "address": {"receiver": address.receiver, "province": address.province_id, "city": address.city_id,
    #                             "district": address.district_id, "place": address.place, "mobile": address.mobile,
    #                             "tel": address.tel, "email": address.email}}
    #     return http.JsonResponse(response)
    def put(self, request, address_id):
        # 1, 获取修改的数据
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 2, 判断正则,是否为空等(这里我就不写了)

        # 3, 修改数据库的数据

        try:
            address = Address.objects.get(id=address_id)
            address.user = request.user
            address.title = receiver
            address.receiver = receiver
            address.province_id = province_id
            address.city_id = city_id
            address.district_id = district_id
            address.place = place
            address.mobile = mobile
            address.tel = tel
            address.email = email
            address.save()

        except Exception as e:
            print(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})

    def delete(request,address_id):
        try:
            address =  request.Address.get(id=address_id)
            address.is_deleted = True
            address.save()
        except Exception as e:
            logging.error(e)
            return http.JsonResponse({'code': 0, 'errmsg': '删除地址失败'})
        return http.JsonResponse({'code':1 ,'errmsg': 'safe'})

        # 4, 返回修改后的数据给前端
        address = Address.objects.get(id=address_id)
        address_dict = {
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
        }

        # 响应更新地址结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})
class DefaultAddressView(View):
    def put(self, request, address_id):
        try:
            address = request.Address.get(id=address_id)
            user = request.user.default_address = address
            user.save()
        except Exception as e:
            logging.error(e)
            return http.JsonResponse({'code':0, "errmsg": 'error'})

        return http.JsonResponse({'code':1, "errmsg": 'safe'})

class OrdersViews(View):
    def get(self, request):
        user_login = request.user
        addresses = Address.objects.filter(user_id=user_login, is_deleted=False)
        address_dict_list = [{
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


class Create_Addresses(LoginRequireJSONdMixin, View):
    def post(self, request):
        user = request.user

        # if Address.objects.filter(user_id=user).count():
        #     return http.HttpResponseForbidden('个数超了')
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        # if not re.match(r'^1[3-9]\d{9}$', mobile):
        #     return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')
        # 接收参数
        try:
            address = Address.objects.create(user=user,
                                             title=receiver,
                                             receiver=receiver,
                                             province_id=province_id,
                                             city_id=city_id,
                                             district_id=district_id,
                                             place=place,
                                             mobile=mobile,
                                             tel=tel,
                                             email=email)
            if not user.default_address:
                user.default_address = address
                user.save()
        except Exception as e:
            logging.error(e)
            return http.JsonResponse({'code': 0, 'errmsg': '新增地址失败'})
        address_dict = {
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
        }

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


class Emali_Verifications(View):
    def get(self, request):
        token = request.GET.get()
        if not token:
            return http.HttpResponseForbidden('501')
        user = decorate_verify_email_url(token)
        if not user:
            return http.HttpResponseForbidden('404')
        user.email_activate = True
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
        context = {"name": request.user.username,
                   "phone": request.user.mobile,
                   "email": request.user.email,
                   "email_activate": request.user.email_active}

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
        userba = UsernameMobileBackend()
        user = userba.authenticate(request=request, username=usernmae, password=password)

        if user is None:
            return render(request, 'login.html', {'account_errmsg': 'KEAL'})

        nexts = request.GET.get("next")
        if nexts:
            response = redirect(nexts)
        else:
            response = redirect(reverse("contents:index"))
        response.set_cookie("username", user.username, max_age=3600 * 12 * 24)
        login(request, user)
        if remembered == "on":
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)

        response = mcookie_to_redis(request=request, user=user, response=response)

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
            return render(request, "reister.html", {"error_message_msg": "不能为空"})
        conn_ext = get_redis_connection("identified")
        ssm_code = conn_ext.get("+86%s" % is_unll[4])
        if is_unll[-2] != ssm_code:
            return render(request, "reister.html", {"error_message_msg": "验证码有𢇞"})


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
