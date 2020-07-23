from jinja2 import Environment
from django.urls import reverse
from django.contrib.staticfiles.storage import staticfiles_storage
import os

def jinja2_environment(**option):

   env = Environment(**option)
   env.globals.update({
       "static": staticfiles_storage.url,
       "url": reverse
    })
   return env