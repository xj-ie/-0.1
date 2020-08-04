# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client


# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
# account_sid = 'AC51b544c96ff4a44f05c7b21bdb6d9ce8'

# auth_token = 'your_auth_token'

account_sid= 'AC51b544c96ff4a44f05c7b21bdb6d9ce8'
auth_token = 'f6dafbe643fc3048ea8b3112545d9605'

# client = Client(account_sid, auth_token)

# message = client.messages.create(
#                      body="check:0015",
#                      from_='+12058398559',
#                      to='+8618478043402'
#                  )


class CCP(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_inder'):
            cls._inder = super(CCP, cls).__new__(cls, *args, **kwargs)
            cls._inder.client = Client(account_sid, auth_token)

        return cls._inder
    def get_conde(self, body, to):
        conde = self.client.messages.create(
            body=body,
            from_='+12058398559',
            to=to)
        print(conde)

if __name__ == '__main__':
    CCP().get_conde("【云通讯】您的验证码是4095", '+8618478043402')
