import json
import time
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
# Create your views here.
from django import http
from django.views import View
from django_redis import get_redis_connection

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods
from users.models import Address
from django.db import transaction


# class OrderSettlementView(LoginRequiredMixin, View):
#     def get(self, request):
#         user = request.user
#         redis_conn = get_redis_connection('carts')
#         try:
#             addresses = Address.objects.filter(id__in=user.id, is_deleted=False)
#         except Exception as e:
#             addresses = {}
#         str_dict = redis_conn.hgetall('cart_{}'.format(user.id))
#         cart_selected = redis_conn.smembers('selected_%s' % user.id)

# new_cart_dict = {}
# for sku_id in redis_selected:
#     new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])

#         total_count = 0
#         total_amount = Decimal(0.00)
#
#         skus = SKU.objects.filter(id__in=cart.keys())
#         for sku in skus:
#             sku.count = cart[sku.id]
#             sku.amount = sku.count * sku.price
#             total_count += sku.count
#             total_amount += sku.count * sku.price
#         freight = Decimal('10.00')
#
#         # 查询商品信息
#
#         context = {
#             'addresses': addresses,
#             'skus': skus,
#             'total_count': total_count,
#             'total_amount': total_amount,
#             'freight': freight,
#             'payment_amount': total_amount + freight
#         }
#         response = render(request, 'place_order.html', context=context)
#         return response


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""

    def get(self, request):
        """查询并展示要结算的订单数据"""
        # 获取登录用户
        user = request.user

        # 查询用户收货地址:查询登录用户的没有被删除的收货地址
        try:
            addresses = Address.objects.filter(user=user, is_deleted=False)
        except Exception as e:
            # 如果没有查询出地址，可以去编辑收货地址
            addresses = None

        # 查询redis购物车中被勾选的商品
        redis_conn = get_redis_connection('carts')
        # 所有的购物车数据，包含了勾选和未勾选 ：{b'1': b'1', b'2': b'2'}
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)
        # 被勾选的商品的sku_id：[b'1']
        redis_selected = redis_conn.smembers('selected_%s' % user.id)
        # 构造购物车中被勾选的商品的数据 {b'1': b'1'}
        new_cart_dict = {int(sku_id): int(redis_cart[sku_id]) for sku_id in redis_selected}
        # for sku_id in redis_selected:
            # new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])

        # 获取被勾选的商品的sku_id
        sku_ids = new_cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)

        total_count = 0
        total_amount = Decimal(0.00)
        # 取出所有的sku
        for sku in skus:
            # 遍历skus给每个sku补充count（数量）和amount（小计）
            sku.count = new_cart_dict[sku.id]
            sku.amount = sku.price * sku.count # Decimal类型的

            # 累加数量和金额
            total_count += sku.count
            total_amount += sku.amount # 类型不同不能运算

        # 指定默认的邮费
        freight = Decimal(10.00)

        # 构造上下文
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight,
        }

        return render(request, 'place_order.html', context)


class OrderCommitView(View):

    def post(self, request):
        """保存订单信息和订单商品信息"""
        # 获取当前要保存的订单数据
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        # 校验参数
        user = request.user
        if not user.is_authenticated:
            return http.HttpResponseForbidden('缺少必传参数')


        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断address_id是否合法
        try:
            # address = Address.objects.get(id=address_id)
            address = Address.objects.get(id=address_id)
        except Exception:
            return http.HttpResponseForbidden('参数address_id错误')
        # 判断pay_method是否合法
        # if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            # return http.HttpResponseForbidden('参数pay_method错误')

        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method错误')

        with transaction.atomic():
            tra1 = transaction.savepoint()
            try:
                date = time.localtime()[0:-1]
                date = ''.join([str(i) for i in date])
                order_id = date + '%09d'%user.id
                orderinfo = OrderInfo.objects.create(
                    order_id=order_id,
                user = user,
                address = address,
                total_count = 0,
                total_amount = Decimal(0.00),
                freight = Decimal(10.00),
                pay_method = pay_method,
                status = OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else
                    OrderInfo.ORDER_STATUS_ENUM['UNSEND'])

                conn_redis = get_redis_connection('carts')
                str_dict = conn_redis.hgetall('carts_%s'%user.id)
                str_list = conn_redis.smembers('selected_%s' % user.id)

                for sku_id in str_list:
                    while True:
                        count = int(str_dict[sku_id])
                        sku = SKU.objects.get(id=sku_id)
                        if count> sku.stock:
                            transaction.rollback(using=tra1)
                            return http.JsonResponse({'code':1, 'errmsg':'error'})
                        reault = SKU.objects.get(id=sku_id, stock=sku.stock).update(stock=sku.stock-count,sales=sku.sales+count)
                        if reault == 0:
                            continue

                        # sku.stock -= count
                        # sku.save()
                        # sku.spu.sales += count
                        # sku.spu.save()
                        # sku.goods.sales += count
                        # sku.goods.save()



                        OrderGoods.objects.create(order = orderinfo,
                                                    sku = sku,
                                                    count = count,
                                                    price = sku.price)
                        orderinfo.total_amount += sku.price*count
                        orderinfo.total_count += count
                        break
                orderinfo.total_count += 10
                orderinfo.save()

            except Exception as e:
                print(e)
                transaction.rollback(tra1)
                return http.JsonResponse({'code': 1, 'errmsg': 'e'})
            transaction.savepoint_commit(tra1)

        return http.JsonResponse({'code': 0, 'errmsg': '下单成功', 'order_id': orderinfo.order_id})


class OrderSuccessView(LoginRequiredMixin, View):
    def get(self, request):
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id':order_id,
            'pay_method':pay_method,
            'payment_amount':payment_amount
        }
        return render(request, 'order_success.html', context=context)



