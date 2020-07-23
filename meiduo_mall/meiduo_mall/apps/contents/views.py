from django.shortcuts import render
from django.views import View
# Create your views here.

class INDEX_VIEWS(View):
    def get(self, request):
        """primary　Ｖiew"""

        return render(request, 'index.html')