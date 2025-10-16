from django.shortcuts import render
from django.http import JsonResponse
import paho.mqtt.publish as publish
from tool import index_SQL_update
import os


# Create your views here.
# 展示主页面
def viewsindex(request):
    file_path = os.path.join(os.path.dirname(__file__), '..', 'tool', 'user_setting.txt')
    with open(file_path, 'r') as file:
        # 读取文件的每一行
        lines = file.readlines()
    # 将第一行的值赋给 min_data
    min_data = eval(lines[0].strip())
    # 将第二行的值赋给 max_data
    max_data = eval(lines[1].strip())
    user_settings = {
        "max_data": max_data,
        "min_data": min_data
    }
    print(user_settings)
    return render(request, "index.html", user_settings)


# 获取实时监控数据
def get_models_datas(request):
    models_datas = index_SQL_update.check_for_updates()
    # print(models_datas)
    models_datas_all = {
        "models_datas": models_datas
    }
    return JsonResponse(models_datas_all)


# 插入包含时间的数据函数
# 获取表格实时数据的函数
def insert_temtime_data(request):
    index_SQL_update.insert_temtime_data()
    all_datas, charts_datas = index_SQL_update.check_for_charts()
    charts_datas_all = {
        "charts_datas": charts_datas
    }
    return JsonResponse(charts_datas_all)


def On_off_ontrol(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        switch_status = request.POST.get('switch_status')
        # 在这里执行您需要的操作，比如保存状态到数据库或者执行其他业务逻辑
        print("switch_status", switch_status)
        # 风扇1
        if switch_status == '1_switch_1':
            publish.single("control", "fan_on", hostname="12.tcp.vip.cpolar.cn",port=11850,auth={'username': 'admin', 'password': '1234'})  # 运行这一行就可以开
        elif switch_status == '1_switch_2':
            publish.single("control", "fan_off", hostname="12.tcp.vip.cpolar.cn",port=11850,auth={'username': 'admin', 'password': '1234'})  # 运行这一行就可以关

        # 风扇2
        elif switch_status == '2_switch_1':
            publish.single("control", "pump_on",  hostname="12.tcp.vip.cpolar.cn",port=11850,auth={'username': 'admin', 'password': '1234'})  # 运行这一行就可以关
        elif switch_status == '2_switch_2':
            publish.single("control", "pump_off",  hostname="12.tcp.vip.cpolar.cn",port=11850,auth={'username': 'admin', 'password': '1234'})  # 运行这一行就可以关

        # 水泵
        elif switch_status == '3_switch_1':
            publish.single("control", "pump_on", hostname="12.tcp.vip.cpolar.cn",port=11850,auth={'username': 'admin', 'password': '1234'})  # 运行这一行就可以关
        elif switch_status == '3_switch_2':
            publish.single("control", "pump_off", hostname="12.tcp.vip.cpolar.cn",port=11850,auth={'username': 'admin', 'password': '1234'})  # 运行这一行就可以关

        # 施肥
        elif switch_status == '4_switch_1':
            publish.single("control", "on", hostname="47.95.9.124")  # 运行这一行就可以关
        elif switch_status == '4_switch_2':
            publish.single("control", "off", hostname="47.95.9.124")  # 运行这一行就可以关

        return JsonResponse({'status': 'success'})  # 返回 JSON 响应
    return JsonResponse({'status': 'error'}, status=400)  # 如果请求不是 POST 或者不是 AJAX 请求，返回错误


def wechat(request):
    print("12123231")
    return JsonResponse({"1": 1})


# 更新用户输入数据
def update_user_settings(request):
    if request.method == 'POST':
        try:
            # 从 POST 请求中获取要更新的数据
            min_data = request.POST.get('min_data')
            max_data = request.POST.get('max_data')
            # 构建文件路径
            file_path = os.path.join(os.path.dirname(__file__), '..', 'tool', 'user_setting.txt')
            # 将数据更新到 txt 文件中
            print("min_data", min_data)
            print("min_data", max_data)
            with open(file_path, 'w') as file:
                file.write(f"{min_data}\n{max_data}")
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST requests are allowed."}, status=405)
