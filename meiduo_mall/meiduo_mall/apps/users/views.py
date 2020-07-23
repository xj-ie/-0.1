from django.shortcuts import render, reverse, redirect
from django.views import View
from django import http
import re
# import phone
from users.models import User
from django.db import DatabaseError
from django.contrib.auth import login
from meiduo_mall.utils.response_code import RETCODE
# import jso
# Create your views here.
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