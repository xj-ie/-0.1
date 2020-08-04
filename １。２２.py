# import pymysql, sys
# # print(sys.path)
#
# class ADDmysql(object):
#     def __init__(self, option):
#         self.option = option
#
#     def __enter__(self):
#
#         self.con = pymysql.connect(**self.option)
#         self.cursor = self.con.cursor()
#
#         return self.cursor
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.con.close()
#         self.cursor.close()
#
# conf = {"host": "192.168.43.185", "port": 3306, "user": "itheima_it", "password": "chuanzhi", "database":"meiduo"}
#
# with ADDmysql(conf) as mysqlsd:
#     executes = "select * from django_migrations;"
#     result = mysqlsd.execute(executes)
#     print(result)

# a = False
# b = 0
# c = 21
# f = a if b else c
# print(f)
#
# a = {
#         "begin": "a",
#         "end": "b"
#     }
#
# inputs = "a"
# print([i for i,j in a.items() if j==inputs])

a = []
b = 0
c = ''
d = {}
f = None
s = [None]
print(bool(a))
print(bool(b))
print(bool(c))
print(bool(d))
print(bool(f))
if s:
    print(s)
