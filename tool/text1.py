import pymysql
import random
import time

host = 'localhost'
port = 3306
user = 'root'
password = 'clw20040202'
database = 'clw_models'


def check_for_charts():
    try:
        # 连接数据库
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
        try:
            # 创建游标对象
            with conn.cursor() as cursor:
                # 查询最新十条数据
                query = "SELECT * FROM temtime ORDER BY savetime DESC LIMIT 7"
                cursor.execute(query)
                results = cursor.fetchall()
                for result in results:
                    result = list(result)
                    # 打印每一条数据
                    # [90, 23, 9, 90.96, datetime.datetime(2024, 4, 22, 17, 4, 41)]
                    # 使用列表推导式获取每个结果列表的第一个元素并放入一个新列表中
                    air_humidity = [result[0] for result in results]
                    air_temperature = [result[1] for result in results]
                    CO2_Percentage = [result[2] for result in results]
                    Soil_moisture = [result[3] for result in results]
                    savetime = [result[4].strftime("%m月%d日%H:%M") for result in results]
                    # 打印新列表
                    result_chart = [air_humidity, air_temperature, CO2_Percentage, Soil_moisture, savetime]
                print(result_chart)
        finally:
            # 关闭数据库连接
            conn.close()


    except pymysql.MySQLError as e:
        print(f"数据库连接错误: {e}")


check_for_charts()
