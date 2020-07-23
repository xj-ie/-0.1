from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register',  views.RegisterView.as_view(), name="register"),
    url(r'^user/(?P<usrname>[A-Za-z-0-9-_]{5,20})/conuter', views.UserCountView.as_view()),
    url(r'phone/(?P<phone>1[3-9]\d{9})/counter', views.PhoneCountView.as_view())

]