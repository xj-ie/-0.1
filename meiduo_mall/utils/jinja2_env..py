from jinja2 import Environment
from django.urls import reverse
import os
def finja2_environment(**option):

   env = Environment(**option)
   env.globals.update({
       "static": os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static"),
       "url": reverse
    })
   return env