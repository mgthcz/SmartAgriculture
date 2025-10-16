import pymysql
from datetime import datetime

# 阿里云服务器MySQL数据库连接信息
host = 'localhost'
port = 3306
user = 'root'
password = '3.141592655Hzh'
database = 'clw_models'


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
                cursor.execute(query)
                result = cursor.fetchone()
                result = list(result)
                # 打印最新一条数据
                return result
        finally:
            # 关闭数据库连接
            conn.close()
            delete_old_data(logo="id")


    except pymysql.MySQLError as e:
        print(f"数据库连接错误: {e}")


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
                    air_humidity = [result[0] for result in results][::-1]
                    air_temperature = [result[1] for result in results][::-1]
                    CO2_Percentage = [result[2] for result in results][::-1]
                    Soil_moisture = [result[3] for result in results][::-1]
                    dan = [result[4] for result in results][::-1]
                    dan.insert(0, "氮")
                    lin = [result[5] for result in results][::-1]
                    lin.insert(0, "磷")
                    jia = [result[6] for result in results][::-1]
                    jia.insert(0, "钾")

                    savetime = [result[7].strftime("%m月%d日%H:%M") for result in results][::-1]
                    savetime_dlj = [result[7].strftime("%H:%M") for result in results][::-1]
                    savetime_dlj.insert(0, "product")
                # 打印新列表
                # print("air_humidity:", air_humidity)
                # print("air_temperature:", air_temperature)
                # print("CO2_Percentage:", CO2_Percentage)
                # print("Soil_moisture:", Soil_moisture)
                # print("savetime:", savetime)
                result_chart = [air_humidity, air_temperature, CO2_Percentage, Soil_moisture, savetime, dan, lin, jia,
                                savetime_dlj]
                print(result_chart)
                return result, result_chart
        finally:
            # 关闭数据库连接
            conn.close()


    except pymysql.MySQLError as e:
        print(f"数据库连接错误: {e}")


# 检查并删除多余数据的函数
def delete_old_data(logo, max_count=10):
    try:
        # 连接数据库
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
        try:
            # 创建游标对象
            with conn.cursor() as cursor:
                if logo == "id":
                    query_count = "SELECT COUNT(*) FROM tem"
                    cursor.execute(query_count)
                    count = cursor.fetchone()[0]
                    if count > max_count:
                        delete_count = count - max_count
                        query_delete = "DELETE FROM tem ORDER BY id LIMIT %s" % delete_count
                        cursor.execute(query_delete)
                        conn.commit()
                        print(f"Deleted id {delete_count} old records.")
                elif logo == "time":
                    query_count = "SELECT COUNT(*) FROM temtime"
                    cursor.execute(query_count)
                    count = cursor.fetchone()[0]
                    if count > max_count:
                        delete_count = count - max_count
                        query_delete = "DELETE FROM temtime ORDER BY savetime LIMIT %s" % delete_count
                        cursor.execute(query_delete)
                        conn.commit()
                        print(f"Deleted time {delete_count} old records.")

        finally:
            # 关闭数据库连接
            conn.close()

    except pymysql.MySQLError as e:
        print(f"数据库连接错误: {e}")


# 定义插入数据的函数
def insert_temtime_data():
    try:
        # 连接数据库
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
        try:
            # 创建游标对象
            with conn.cursor() as cursor:
                # 查询最新的温度数据
                query_latest_temp = "SELECT * FROM tem ORDER BY id DESC LIMIT 1"
                cursor.execute(query_latest_temp)
                latest_temp_data = cursor.fetchone()  # 获取查询结果的第一行数据

                # 获取当前时间
                current_time = datetime.now()

                # 将最新的温度数据和当前时间插入到temtime表中
                insert_query = "INSERT INTO temtime (air_humidity, air_temperature, CO2_Percentage, soil_moisture, dan, lin, jia ,savetime) VALUES (%s, %s, %s, %s ,%s,%s ,%s ,%s)"
                data_to_insert = (*latest_temp_data, current_time)  # 将元组拆分为参数列表
                # print(insert_query, data_to_insert)
                data_to_insert = data_to_insert[1:]
                # print(insert_query, data_to_insert)
                cursor.execute(insert_query, data_to_insert)
                conn.commit()

                print("数据插入成功")
        finally:
            # 关闭数据库连接
            conn.close()
            delete_old_data(logo="time")

    except pymysql.MySQLError as e:
        print(f"index_SQL_update_161:数据库连接错误: {e}")
