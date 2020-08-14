import django_redis, base64, pickle

def mcookie_to_redis(request, user, response):
    cookie_cart_str = request.COOKIES.get('carts')
    if not cookie_cart_str:
        return response
    cookie_cart =  pickle.loads(base64.b64decode(cookie_cart_str.encode()))
    #user_id:{sku.id:id,
    #          count:count,
    #          sele_:True}
    new_cart_dict = {key: values['count'] for key,values in cookie_cart.items()}
    new_cart_selected_add = [key for key, values in cookie_cart.items() if values['selected']]
    new_cart_selected_remove = [key for key, values in cookie_cart.items() if not values['selected']]

    redis_conn = django_redis.get_redis_connection('carts')
    redis_conn.hmset('carts_%s' % user.id, new_cart_dict)
    if new_cart_selected_add:
        redis_conn.ladd('selected_%s' % user.id, *new_cart_selected_add)
    if new_cart_selected_remove:
        redis_conn.lrem('selected_%s' % user.id, *new_cart_selected_remove)

    response.delete_cookie('carts')

    return response