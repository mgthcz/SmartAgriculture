# 导入 Django 相关模块
from django.shortcuts import render
# 导入图像处理所需的模块
from PIL import Image
from io import BytesIO
import base64
import cv2
import numpy as np
from ultralytics import YOLO
import time
from tool import name_modelpath, spark

names = name_modelpath.names
model_path = name_modelpath.model_path


def make_image_size(image_bgr, target_size=(640, 640)):
    # 直接改变图片大小
    # image_bgr = cv2.resize(image_bgr, target_size)

    # 添加白边
    # 计算原始图像的宽高比
    image_height, image_width, _ = image_bgr.shape
    aspect_ratio = image_width / image_height
    # 计算图像在画布中的位置
    if aspect_ratio > target_size[0] / target_size[1]:
        # 如果原始图像宽高比更大，则根据目标宽度进行缩放
        new_width = target_size[0]
        new_height = int(new_width / aspect_ratio)
    else:
        # 如果原始图像高宽比更大，则根据目标高度进行缩放
        new_height = target_size[1]
        new_width = int(new_height * aspect_ratio)
    # 缩放图像
    resized_image = cv2.resize(image_bgr, (new_width, new_height))
    # 创建一个新的白色画布
    canvas = np.full((target_size[1], target_size[0], 3), 255, dtype=np.uint8)
    # 计算图像在画布中的位置
    x_offset = (target_size[0] - new_width) // 2
    y_offset = (target_size[1] - new_height) // 2
    # 将缩放后的图像粘贴到画布中心
    canvas[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized_image
    return canvas


# 图片检测代码
def image_detect(image):
    tips = ''
    pests_names = ''
    # 将图像转换为 OpenCV 格式（BGR）
    image_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    # image_bgr = make_image_size(image_bgr)
    # 使用模型对图片进行预测
    print("模型加载中：")
    time1 = time.time()
    model = YOLO(model_path)  # 加载YOLO模型，参数为模型文件路径
    time2 = time.time()
    print("模型加载时间：", time2 - time1)
    res = model.predict(image_bgr)
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
        tips = "植株正常，请您放心！"
    # 将图像转换回 PIL 格式（RGB）
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    # 返回处理后的图像
    return Image.fromarray(image_rgb), tips


# 目标跟踪检测代码
def image_track_detect(image):
    tips = ''
    # 将图像转换为 OpenCV 格式（BGR）
    image_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    # image_bgr = make_image_size(image_bgr)
    max_id = 0  # 初始化最大ID
    processed_frames = []  # 初始化处理过的帧列表
    print("开始检测：")
    time3 = time.time()
    print("模型加载中：")
    time1 = time.time()
    model = YOLO(model_path)  # 加载YOLO模型，参数为模型文件路径
    time2 = time.time()
    print("模型加载时间：", time2 - time1)
    results = model.track(image_bgr, persist=True)  # 使用YOLO模型进行目标跟踪
    time5 = time.time()
    print("跟踪完成:", time5 - time3)
    if results[0].boxes.id is not None:  # 如果检测到目标
        class_ids = results[0].boxes.cls.tolist()
        boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)  # 获取目标框坐标
        ids = results[0].boxes.id.cpu().numpy().astype(int)  # 获取目标ID
        max_id = max(max_id, max(ids, default=0))  # 更新最大ID
        print(class_ids)
        image_bgr = results[0].plot()
        for box, id, class_id in zip(boxes, ids, class_ids):  # 遍历目标框和ID
            print(id, "==============", time.time())
            # cv2.rectangle(image_bgr, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)  # 绘制目标框
            # cv2.putText(
            #     image_bgr,
            #     f"Id {id}",
            #     (box[0], box[1]),
            #     cv2.FONT_HERSHEY_SIMPLEX,
            #     1,
            #     (0, 0, 255),
            #     2,
            # )  # 在目标框附近添加ID标签
            # # 标出最大值
        time4 = time.time()
        print("检测结束，检测耗时：", time4 - time3)
        class_ids_set = class_ids
        class_ids_set = set(class_ids_set)
        class_ids_set = list(class_ids_set)
        i = 0
        for class_id_set in class_ids_set:
            cv2.putText(
                image_bgr,
                f"{names[int(class_id_set)]}: {class_ids.count(class_id_set)}",
                (int(image_bgr.shape[1] / 4), 50 + i * 30),
                cv2.FONT_HERSHEY_SIMPLEX,  # 使用 cv2.FONT_HERSHEY_SIMPLEX 字体
                1,
                (0, 255, 0),
                2,
            )  # 在视频帧中添加最大ID信息
            i = i + 1
        cv2.putText(
            image_bgr,
            f"ALL Target object: {max_id}",
            (int(image_bgr.shape[1] / 4), 50 + i * 30),
            cv2.FONT_HERSHEY_SIMPLEX,  # 使用 cv2.FONT_HERSHEY_SIMPLEX 字体
            1,
            (0, 255, 0),
            2,
        )  # 在视频帧中添加最大ID信息
        processed_frames.append(image_bgr)  # 将处理后的帧添加到列表中
        pests_names = name_modelpath.names_china[int(results[0].boxes.data.tolist()[0][5])]
        tips = spark.spark("请简单介绍一下植物" + pests_names + "，并给出简单的解决方案，150字以内。")
    else:
        cv2.putText(
            image_bgr,
            f"Target object not detected!",
            (int(image_bgr.shape[1] / 10), 50),
            cv2.FONT_HERSHEY_SIMPLEX,  # 使用 cv2.FONT_HERSHEY_SIMPLEX 字体
            1,
            (0, 255, 0),
            2,
        )
        tips = "植株正常，请您放心！"
    # 将图像转换回 PIL 格式（RGB）
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    # 返回处理后的图像
    return Image.fromarray(image_rgb), tips


# 定义视图函数
def ImageDetectionAndCounting(request):
    # 初始化原始图片和处理后的图片
    global processed_img, original_img, tips
    original_image = None
    processed_image = None
    tips = ''

    # 判断请求方法是否为 POST
    if request.method == 'POST':
        # 处理上传的图片
        uploaded_image = request.FILES.get('image')
        # 获取用户选择的操作类型
        operation = request.POST.get('operation')
        print(operation)
        if uploaded_image:
            try:
                # 尝试打开上传的图片
                original_img = Image.open(uploaded_image)
                # 检查图片格式是否为JPEG，如果不是，则转换为JPEG格式
                if original_img.mode == "P" or "RGBA":
                    original_img = original_img.convert("RGB")
                # 创建一个字节流缓冲区，用于保存原始图片
                original_img_buffered = BytesIO()
                # 将原始图片保存到缓冲区，格式为 JPEG
                original_img.save(original_img_buffered, format="JPEG")
                # 将原始图片转换成 Base64 编码的字符串
                original_image = base64.b64encode(original_img_buffered.getvalue()).decode("utf-8")
            except Exception as e:
                # 处理异常情况，比如图片无法打开等
                print("Error:", e)

            # 在这里执行相应的处理，根据选择的操作类型进行不同的处理
            if operation == 'objectDetection':
                # 执行目标检测的处理逻辑
                processed_img, tips = image_detect(original_img)

            elif operation == 'objectTracking':
                # 执行跟踪计数的处理逻辑
                processed_img, tips = image_track_detect(original_img)

            # 创建一个字节流缓冲区，用于保存处理后的图片
            processed_img_buffered = BytesIO()
            # 将处理后的图片保存到缓冲区，格式为 JPEG
            processed_img.save(processed_img_buffered, format="JPEG")
            # 将处理后的图片转换成 Base64 编码的字符串
            processed_image = base64.b64encode(processed_img_buffered.getvalue()).decode("utf-8")

    # 渲染模板并传递原始图片和处理后的图片数据
    return render(request, 'ImageDetectionAndCounting.html',
                  {'original_image': original_image, 'processed_image': processed_image, "tips": tips})
