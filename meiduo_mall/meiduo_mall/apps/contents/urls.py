from django.conf.urls import url, include
from . import views

urlpatterns = [

    url(r'^$', views.INDEX_VIEWS.as_view(), name="index"),

]