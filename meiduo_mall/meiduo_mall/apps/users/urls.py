from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register',  views.RegisterView.as_view(), name="register"),
    url(r'^user/(?P<usrname>[A-Za-z-0-9-_]{5,20})/conuter', views.UserCountView.as_view()),
    url(r'phone/(?P<phone>1[3-9]\d{9})/counter', views.PhoneCountView.as_view()),
    url(r'^login/', views.LoginView.as_view(), name="login"),
    url(r'^logout/', views.LogOut.as_view(), name="logout"),
    url(r'^user_center_info', views.UserInfoView.as_view(), name="info"),
    url(r'^emails/', views.EmailView.as_view(), name='email'),
    url(r'^emails/verification/', views.Emali_Verifications.as_view()),
    url(r'^Orders', views.OrdersViews.as_view(), name="address"),
    url(r'^addresses/create/$', views.Create_Addresses.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/', views.UpdateDestroyAddressView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/default/', views.DefaultAddressView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/title/', views.UpdateTitleAddressView.as_view()),
    url('^browse_histories/$', views.UserBrowseHistory.as_view())

]