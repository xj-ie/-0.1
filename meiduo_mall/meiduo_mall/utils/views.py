from django.contrib.auth.mixins import LoginRequiredMixin

from django import http


class LoginRequireJSONdMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        return http.JsonResponse(http.JsonResponse({"code": 4101, "errmsg": 'use not !'}))