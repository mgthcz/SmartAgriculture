# Create your views here.
from django.shortcuts import render
import cv2
import numpy as np
import base64
from django.http import JsonResponse
import time
from ultralytics import YOLO
from PIL import Image
import io
from tool import name_modelpath, spark

names = name_modelpath.names
model_path = name_modelpath.model_path


def camera_capture_view(request):
    # 返回包含摄像头捕获页面的渲染结果
    return render(request, 'PhotoDetectionAndRecognition.html')


# 图片检测代码
def image_detect(image_bgr):
    tips = ''
    pests_names = ''
    # 使用模型对图片进行预测
    print("模型加载中：")
    time1 = time.time()
    model = YOLO(model_path)  # 加载YOLO模型，参数为模型文件路径
    time2 = time.time()
    print("模型加载时间：", time2 - time1)
    res = model.predict(image_bgr, conf=0.8)
    # 对预测结果进行可视化
    if len(res[0].boxes.cls.tolist()) > 0:
        image_bgr = res[0].plot()
        pests_names = name_modelpath.names_china[int(res[0].boxes.data.tolist()[0][5])]
        tips = spark.spark("请简单介绍一下植物" + pests_names + "，并给出简单的解决方案，150字以内。")
    else:
        cv2.putText(
            image_bgr,
            f"object not detected!",
            (int(image_bgr.shape[1] / 10), 50),
            cv2.FONT_HERSHEY_SIMPLEX,  # 使用 cv2.FONT_HERSHEY_SIMPLEX 字体
            1,
            (0, 255, 0),
            2,
        )
        pests_names = "正常植株"
        tips = "植株正常，请您放心！"
    # 将图像转换回 PIL 格式（RGB）
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    # 返回处理后的图像
    return image_rgb, tips, pests_names


def capture_and_process(request):
    # 检查请求方法是否为 POST，并且是否包含名为 'image' 的文件
    if request.method == 'POST' and request.FILES['image']:
        # 读取图像数据
        image = request.FILES['image'].read()
        # 将图像数据转换为 NumPy 数组
        nparr = np.frombuffer(image, np.uint8)
        # 使用 OpenCV 解码图像
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        processed_img, tips, pests_names = image_detect(img)
        # 将 numpy 数组转换为 PIL Image 对象
        img_pil = Image.fromarray(processed_img)
        # 将图像转换为 PNG 格式
        with io.BytesIO() as output:
            img_pil.save(output, format="PNG")
            img_encoded = output.getvalue()
        # 将编码后的图像转换为 base64 编码
        img_base64 = base64.b64encode(img_encoded)
        # 将 base64 编码的图像转换为字符串并返回给客户端
        img_base64 = img_base64.decode('utf-8')
        print("tips", tips)
        return JsonResponse({'image': img_base64, "pests_names": pests_names, "tips": tips})
    else:
        # 如果没有找到图像文件，则返回错误信息
        return JsonResponse({'error': 'No image found'})
