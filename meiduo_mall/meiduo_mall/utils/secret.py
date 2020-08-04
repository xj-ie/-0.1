from itsdangerous import TimedJSONWebSignatureSerializer

from django.conf import settings


class SecretOauth(object):
    def __init__(self):
        self.serializer = TimedJSONWebSignatureSerializer(secret_key=settings.SECRET_KEY, expires_in=3600*10)

    def dumps(self, data):
        result = self.serializer.dumps(data)
        code_result = result.decode()
        return code_result

    def loads(self, data):
        result = self.serializer.loads(data)
        return result