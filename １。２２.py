# import pymysql
#
# class ADDmysql(object):
#     def __init__(self, **option):
#         self.option = option
#     def __enter__(self):
#         self.con = pymysql.connect(self.option)
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
# with ADDmysql(**conf) as mysqlsd:
#     executes = "show tables;"
#     mysqlsd.execute(executes)
#