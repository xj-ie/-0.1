import base64
import http
import json
import pickle

from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection
from django import http
from goods.models import SKU


class CartsView(View):
    def post(self, request):
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected', True)
        if not all([count, sku_id]):
            return http.JsonResponse({'code': 1, 'errormsg': 'error'})
        try:
            count = int(count)
            a = SKU.objects.get(id=sku_id)
        except Exception as e:
            return http.JsonResponse({'code': 1, 'errormsg': 'error'})
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')
        user = request.user
        if user.is_authenticated:
            redis_conns = get_redis_connection('carts')
            pl = redis_conns.pipeline()
            pl.hincrby('carts_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
                # 执行管道
            pl.execute()
            # 响应结果
            return http.JsonResponse({'code': 0, 'errmsg': '添加购物车成功'})
        else:
            cookies_str = request.COOKIES.get('carts')
            if cookies_str:
                str_bytes = cookies_str.encode()
                str_bytes = base64.b64decode(str_bytes)
                cart_dict = pickle.loads(str_bytes)

            else:
                cart_dict = {}

            if sku_id in cart_dict:
                count += cart_dict.get(sku_id)['count']

            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            cart_dict = pickle.dumps(cart_dict)
            cart_dict = base64.b64encode(cart_dict)
            cart_dict = cart_dict.decode('utf-8')

            response = http.JsonResponse({'code': 0, 'error_msg': '0000000'})
            response.set_cookie('carts', cart_dict, max_age=24 * 30 * 3600)
            return response

    def get(self, request):
        '''
        {
        "sku_id1":{
        "count":"1",
        "selected":"True"
        },
        '''


        user = request.user


        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            dect_str = redis_conn.hgetall('carts_%s' % user.id)
            # sku_id{商品id：数量}
            list_str = redis_conn.smembers('selected_%s' % user.id)
            # 是否选中 「sku_id」
            cart_dict = {int(key): {
                "count": int(value),
                "selected": user.id in list_str
            } for key, value in dect_str.items()}

        else:

            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_by = cart_str.encode('utf-8')
                cart_str_by = base64.b64decode(cart_by)
                cart_dict = pickle.loads(cart_str_by)
            else:
                cart_dict = {}

        sku_ids = cart_dict.keys()
        sku_list = SKU.objects.filter(id__in=sku_ids)#「<objects>」

        cart_skus = [{'id': sku.id,
                      'name': sku.name,
                      'count': cart_dict.get(sku.id).get('count'),
                      'selected': str(cart_dict.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
                      'default_image_url': sku.default_image.url,
                      'price': str(sku.price),  # 从Decimal('10.2')中取出'10.2'，方便json解析
                      'amount': str(sku.price * cart_dict.get(sku.id).get('count'))} for sku in sku_list]
        context = {
            'cart_skus': cart_skus,
        }
        response = render(request, 'cart.html', context)
        # response = mcookie_to_redis(request, user, response)
        # 渲染购物车页面
        return response
    def put(self,request):
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        cart_str = ''
        selected = data.get('selected', True)
        if not all([count, sku_id]):
            return http.JsonResponse({'code': 1, 'errormsg': 'error'})

        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')
        user = request.user
        sku = SKU.objects.get(id=sku_id)
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            redis_conn.hset('carts_{}'.format(user.id), sku_id, count)
            if selected:
                redis_conn.sadd('selected_{}'.format(user.id), sku_id)
            else:
                redis_conn.srem('selected_{}'.format(user.id), sku_id)


        else:
            # carts_srt = request.COOKIES.get('carts')
            # 用户未登录，修改cookie购物车
            cart_str = request.COOKIES.get('carts')

            # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典

            cart_dict = pickle.loads(base64.b64decode(cart_str.encode())) if cart_str else {}
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            cart_dict = pickle.dumps(cart_dict)
            cart_str_by = base64.b64encode(cart_dict)
            cart_str = cart_str_by.decode()

        cart_sku = {
            'id': sku_id,
            'count': count,
            'selected': selected,
            'name': sku.name,
            'default_image_url': sku.default_image.url,
            'price': sku.price,
            'amount': sku.price * count,
        }

        response = http.JsonResponse({'code': 0 , 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
        if cart_str:
            response.set_cookie('carts', cart_str, max_age=24 * 30 * 3600)
        return response
    def delete(self, request):

        sku_id = json.loads(request.body.decode()).get('sku_id')

        user = request.user
        response = http.JsonResponse({'code': 0, 'errmsg': '删除购物车成功'})

        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hdel('carts_{}'.format(user.id), sku_id)
            pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()


        else:
            cart_dist = request.COOKIES.get('carts')
            cart_dist = pickle.loads(base64.b64decode(cart_dist.encode())) if cart_dist else {}
            if sku_id in cart_dist:
                del cart_dist[sku_id]
                cookie_cart_str = base64.b64encode(pickle.dumps(cart_dist)).decode()
                response.set_cookie('carts', cookie_cart_str, max_age=24 * 30 * 3600)

        return response

class CartsSelectAllView(View):
    def put(self, request):
            # 接收参数
        cart_dict = ''
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected', True)

            # 校验参数
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')

        user = request.user
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            cart = redis_conn.hgetall('carts_{}'.format(user.id))
            sku_id_list = cart.keys()
            redis_conn.sadd('selected_{}'.format(user.id), *sku_id_list) if selected else redis_conn.srem('selected_{}'.format(user.id), *sku_id_list)

        else:
            cart = pickle.loads(base64.b64decode(request.COOKIES.get('carts').encode('utf-8')))
            if cart:
                for key in cart.keys():
                    cart[key]['selected'] = selected
                cart_dict = base64.b64decode(pickle.dumps(cart)).decode('utf-8')

        response = http.JsonResponse({'code': 0, 'errormsg': 'info'})
        response.set_cookie('carts', cart_dict) if cart_dict else 0
        return response