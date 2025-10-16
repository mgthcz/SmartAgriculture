# import pymysql
# import time
# import numpy as np
#
# # 阿里云服务器MySQL数据库连接信息
# host = 'localhost'
# port = 3306
# user = 'root'
# password = 'clw20040202'
# database = 'clw_models'
#
#
# def check_for_updates():
#     try:
#         result_old = None
#         while True:
#             # 连接数据库
#             conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
#
#             try:
#                 # 创建游标对象
#                 with conn.cursor() as cursor:
#                     # 查询最新一条数据
#                     query = "SELECT * FROM tem ORDER BY id DESC LIMIT 1"
#                     # (2, 23, 23, datetime.datetime(2024, 4, 1, 20, 49))
#                     # query = "SELECT * FROM TimeTem ORDER BY id DESC LIMIT 1"
#                     cursor.execute(query)
#                     result = cursor.fetchone()
#
#                     if result_old is None or not np.array_equal(result, result_old):
#                         result_old = tuple(result)
#                         # 打印最新一条数据
#                         print("最新一条数据：", result)
#                     else:
#                         # print("暂时无数据更新")
#                         pass
#             finally:
#                 # 关闭数据库连接
#                 conn.close()
#             # 每隔一段时间再次查询，比如每10秒查询一次
#             time.sleep(1)
#
#     except pymysql.MySQLError as e:
#         print(f"数据库连接错误: {e}")
#
#
# if __name__ == "__main__":
#     check_for_updates()

import pymysql
import time
import numpy as np

# 阿里云服务器MySQL数据库连接信息
host = 'localhost'
port = 3306
user = 'root'
password = '3.141592655Hzh'
database = 'clw_models'

# 阿里云服务器MySQL数据库连接信息
# host = '47.95.9.124'
# port = 3306
# user = 'tem'
# password = '1'
# database = 'tem'


def check_for_updates():
    try:
        # 连接数据库
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
        try:
            # 创建游标对象
            with conn.cursor() as cursor:
                # 查询最新一条数据
                query = "SELECT * FROM tem ORDER BY id DESC LIMIT 1"
                # (2, 23, 23, datetime.datetime(2024, 4, 1, 20, 49))
                # query = "SELECT * FROM TimeTem ORDER BY id DESC LIMIT 1"
                cursor.execute(query)
                result = cursor.fetchone()
                result = list(result)
                # 打印最新一条数据
                return result
        finally:
            # 关闭数据库连接
            conn.close()

    except pymysql.MySQLError as e:
        print(f"数据库连接错误: {e}")


# result = check_for_updates()
# print("最新一条数据：", result)
