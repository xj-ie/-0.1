import re
# from users.models import User
from django.conf import settings
from django.contrib.auth.backends import ModelBackend

# from meiduo_mall.settings.dev import logger
from users.models import User
from meiduo_mall.utils.secret import SecretOauth

def decorate_verify_email_url(coten):
    data = SecretOauth().loads(coten)
    if not data:
        return None
    user_id = data.get('id')
    email = data.get('email')
    if not all(user_id, email):
        return None
    try:
        user = User.objects.get(user_id=user_id, email=email)
    except Exception as e:
        return None
    return user

def get_user_by_account(account):
    """
    通过账号获取用户
    :param account: 用户名或者手机号
    :return: user
    """
    try:
        #[a-zA-Z0-9]{5,20} 1302030402

        if re.match(r'^1[3-9]\d{9}$', account):
            # account == 手机号
            user = User.objects.get(mobile=account)
            if user is None:
                user = User.objects.get(username=account)


        else:
            # account == 用户名
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user

class UsernameMobileBackend(ModelBackend):
    """自定义用户认证后端"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        重写用户认证的方法
        :param username: 用户名或手机号
        :param password: 密码明文
        :param kwargs: 额外参数
        :return: user
        """
        # 查询用户
        user = get_user_by_account(username)

        # 如果可以查询到用户，好需要校验密码是否正确
        if user and user.check_password(password):
            # 返回user
            return user
        else:
            return None




# 构建激活链接
def generate_verify_email_url(user):
    dict_data = {"id": user.id, "email": user.email}

    # 加密
    secret_data = SecretOauth().dumps(dict_data)

    # 拼接激活链接
    active_url = settings.EMAIL_VERIFY_URL + '?token=' + secret_data

    return active_url
