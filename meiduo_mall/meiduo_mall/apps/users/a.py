# 自定义用户认证的后端:实现多账号登录
from django.contrib.auth.backends import ModelBackend
import re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from itsdangerous import BadData

from users.models import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from . import constants
class SECRET_TXT(object):
    secret = "QEPWQLLLI*KD"
    expiration = 3000
class SECRET_key(object):
    def __init__(self, TXT):
        self.TXT = TXT
        self.s = Serializer(self.TXT.secret, self.TXT.expiration)
    def dumpsl(self, data):
        return self.s.dumps(data)

    def loadsl(self, coekt):
        return self.s.loads(coekt)

if __name__ == '__main__':
    sTXT = SECRET_TXT()
    s1 = SECRET_key(sTXT)
    data = 'q ep wq '
    cehoes = s1.dupmsl(data)
    print(s1.loadsl(cehoes))


    ##############################
    sTXT2 = SECRET_TXT()
    sTXT2.secret = "1111122222333"
    sTXT2.expiration = 2000
    s2 = SECRET_key(sTXT2)
    data1 = 'g tg g an'
    choens1 = s2.dupmsl(data1)
    print(s2.loadsl(choens1))






#
# def check_verify_email_token(token):
#     """
#     反序列化token,获取到user
#     :param token: 序列化后的用户信息
#     :return: user
#     """
#     s = Serializer(settings.SECRET_KEY, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
#     try:
#         data = s.loads(token)
#     except BadData:
#         return None
#     else:
#         # 从data中取出user_id和email
#         user_id = data.get('user_id')
#         email = data.get('email')
#         try:
#             user = User.objects.get(id=user_id, email=email)
#         except User.DoesNotExist:
#             return None
#         else:
#             return user


# def generate_verify_email_url(user):
#     """
#     生成邮箱激活链接
#     :param user: 当前登录用户
#     :return: http://www.meiduo.site:8000/emails/verification/?token=eyJhbGciOiJIUzUxMiIsImlhdCI6MTU1ODA2MDE0MSwiZXhwIjoxNTU4MTQ2NTQxfQ.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InpoYW5namllc2hhcnBAMTYzLmNvbSJ9.y1jaafj2Mce-LDJuNjkTkVbichoq5QkfquIAhmS_Vkj6m-FLOwBxmLTKkGG0Up4eGGfkhKuI11Lti0n3G9XI3Q
#     """
#     s = Serializer(settings.SECRET_KEY, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
#     data = {'user_id': user.id, 'email': user.email}
#     token = s.dumps(data)
#     return settings.EMAIL_VERIFY_URL + '?token=' + token.decode()

