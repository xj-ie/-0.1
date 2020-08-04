from itsdangerous import TimedJSONWebSignatureSerializer
# from django.conf import settings


class Serializer:
    def __init__(self):
        self.s = TimedJSONWebSignatureSerializer("settings.EMAIL_BACKEND", 600)
    def dupmsl(self, data):
        data = {'openid':data}
        cakes = self.s.dumps(data)
        return cakes
    def loadsl(self, cakes):
        try:
            data = self.s.loads(cakes)
        except Exception:
            return None
        else:
            return data.get('openid')



if __name__ == '__main__':
    s = Serializer()
    a = s.dupmsl(1)
    print(a.decode('utf-8'))
    b = s.loadsl(a)
    print(b)
