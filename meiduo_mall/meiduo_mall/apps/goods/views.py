from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View
from contents.utils import get_categories
from goods.utils import get_breadcrumb
from goods.models import GoodsCategory, SKU
from django import http

# Create your views here.
class HotGoodsView(View):
    def get(self, category_id):
        skus = SKU.objcets.filter(id=category_id,is_launched=True).order_by('-sales')[1]
        hot_skus = [{"id":sku.id,
            "default_image_url":sku.default_image_url,
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
            'category': category,  # 第三级分类
            'page_skus': page_skus,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码
        }
        return render(request, 'list.html', context)




        return render(request, 'list.html', context)