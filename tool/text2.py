# 打开文件
with open('../tool/user_setting.txt', 'r') as file:
    # 读取文件的每一行
    lines = file.readlines()

# 将第一行的值赋给 min_data
min_data = eval(lines[0].strip())
# 将第二行的值赋给 max_data
max_data = eval(lines[1].strip())

# 打印结果
print("min_data:", min_data)
print("max_data:", max_data)
