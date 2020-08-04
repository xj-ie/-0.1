from django.shortcuts import render
from django.views import View
from django import http
from areas.models import Area
from django.core.cache import cache
import logging
logging.getLogger('django')

class AreasViews(View):
    def get(self, request):
        # province_dict =cache.get('province_dict')
        # if not province_dict:
        area_id = request.GET.get('area_id')
        if not area_id:
            province_dict = cache.get('province_dict')
            if not province_dict:
                try:
                    province_model_list = Area.objects.filter(parent__isnull=True)
                    province_dict = [{"id": province_model.id, 'name': province_model.name} for province_model in province_model_list]
                    cache.set("province_dict",province_dict, 3600)
                except Exception as e:
                    response_errer = {"code": 1, "errmsg": "filter_db_errer"}
                    logging.error(e)
                    return http.JsonResponse(response_errer)
            response = {"code": 0, "errmsg": "info", "province_list": province_dict}
            return http.JsonResponse(response)
        else:
            sub_data = cache.get('sub_areas_'+str(area_id))
            if not sub_data:
                try:
                    parent_model = Area.objects.get(id=area_id)
                    # sub_model_list = parent_model.area_set.all()
                    sub_model_list = parent_model.subs.all()
                    sub_data = {
                        'id': parent_model.id,
                        'name':parent_model.name,
                        "subs":[{'id':sub_model.id, 'name': sub_model.name } for sub_model in sub_model_list]
                    }
                    cache.set('sub_areas_' + str(area_id), sub_data,3600)

                except Exception as e:
                    response_errer = {"code": 1, "errmsg": "filter_db_errer"}
                    logging.error(e)
                    return http.JsonResponse(response_errer)
            response = {"code": 0, "errmsg": "info", "sub_data": sub_data}
            return http.JsonResponse(response)