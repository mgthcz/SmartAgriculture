import pymysql
import random
import time

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='123456',
    database = 'shiyan'
)
cursor = conn.cursor()


# 检查并删除多余数据的函数
def delete_old_data(max_count=10):
    query_count = "SELECT COUNT(*) FROM tem"
    cursor.execute(query_count)
    count = cursor.fetchone()[0]
    if count > max_count:
        delete_count = count - max_count
        query_delete = "DELETE FROM tem ORDER BY id LIMIT %s" % delete_count
        cursor.execute(query_delete)
        conn.commit()
        print(f"Deleted {delete_count} old records.")


# 定义插入数据的函数
def insert_random_data():
    air_humidity = random.randint(0, 100)
    air_temperature = random.randint(-20, 40)
    CO2_Percentage = random.randint(0, 100)
    soil_moisture = round(random.uniform(0, 100), 2)
    dan = round(random.uniform(0, 100), 2)
    lin = round(random.uniform(0, 100), 2)
    jia = round(random.uniform(0, 100), 2)

    query = "INSERT INTO tem (air_humidity, air_temperature, CO2_Percentage, soil_moisture, dan, lin, jia) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (air_humidity, air_temperature, CO2_Percentage, soil_moisture, dan, lin, jia))
    conn.commit()

    print(
        f"Inserted: Air Humidity = {air_humidity}, Air Temperature = {air_temperature}, CO2 Percentage = {CO2_Percentage}, Soil Moisture = {soil_moisture},"
        f"dan = {dan},lin = {lin},jia = {jia}")
    delete_old_data()


# 每隔一秒插入一条随机数据
while True:
    insert_random_data()
    time.sleep(5)

# 关闭连接
cursor.close()
conn.close()
