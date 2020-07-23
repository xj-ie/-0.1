from django.conf.urls import url, include
from .views import INDEX_VIEWS

urlpatterns = [

    url(r'^$', INDEX_VIEWS.as_view(), name="index"),

]