import base64, pickle
from datetime import timezone, datetime
import time, json
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View
from contents.utils import get_categories
from goods.utils import get_breadcrumb
from goods.models import GoodsCategory, SKU, GoodsVisitCount
from django import http
from django_redis import get_redis_connection


# from django.
# Create your views here.
class HotGoodsView(View):
    def get(self, request, category_id):
        skus = SKU.objects.filter(category_id=category_id,is_launched=True).order_by('-sales')[:2]
        hot_skus = [{"id":sku.id,
            "default_image_url":sku.default_image.url,
            "name":sku.name,
            "price":sku.price} for sku in skus]
        response = {'code':0,"errmsg":'ok','hot_skus':hot_skus}
        return http.JsonResponse(response)


class ListView(View):
    """商品列表页"""

    def get(self, request, category_id, page_num):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except Exception as e:
            return http.HttpResponseForbidden('code:dataEREEOr login')

        categories = get_categories()
        breadcrumb = get_breadcrumb(category)
        sort = request.GET.get('sort', 'defualt')
        if sort == 'price':
            sort_field = 'price'
        elif sort == 'hot':
            sort_field = '-sales'
        else:
            sort = 'default'
            sort_field = 'create_time'
        sksu = SKU.objects.filter(category=category, is_launched=True).order_by(sort_field)
        paginator = Paginator(sksu, 5)
        try:
            page_skus = paginator.page(page_num)
        except Exception as e :
            return http.HttpResponseForbidden('404')

        total_page = paginator.num_pages

        context = {
            'categories': categories,  # 频道分类
            'breadcrumb': breadcrumb,  # 面包屑导航
            'sort': sort,  # 排序字段
            'category_id': category_id,  # 第三级分类
            'page_skus': page_skus,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码
        }
        return render(request, 'list.html', context)




        return render(request, 'list.html', context)




class DetailView(View):
    def get(self, request, sku_id):
        try:
            sku = SKU.objects.get(id=sku_id)
        except Exception as e:
            return render(request, '404.html')

        categories = get_categories()
        breadcrumb = get_breadcrumb(category=sku.category)

        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
        }
        return render(request, 'detail.html',context)

class DetailVisitView(View):
    def get(self, request, category_id):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except Exception as e:
            return http.HttpResponseForbidden('dtype=NONE')

        t1 = time.localtime(time.time())
        t1 = '{}-{}-{}'.format(t1.tm_year, t1.tm_mon, t1.tm_mday)

        t1 = datetime.strptime(t1,'%Y-%m-%d')
        try:
            counts_datd =GoodsVisitCount.objects.get(date=t1, category=category)
        except Exception as e:
            counts_datd = GoodsVisitCount()

        counts_datd.category = category
        counts_datd.count += 1
        counts_datd.date = t1

        try:
            counts_datd.save()
        except Exception as e:
            return http.HttpResponseServerError('Eroor')

        response = {'conde':0,'error':'info'}
        return http.JsonResponse(response)


