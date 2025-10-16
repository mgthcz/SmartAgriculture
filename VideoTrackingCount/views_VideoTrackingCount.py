from django.shortcuts import render
from django.http import JsonResponse
import base64
import cv2
import subprocess
import os
from django.conf import settings
from collections import defaultdict
import numpy as np
from ultralytics import YOLO
from tool import name_modelpath, spark

names = name_modelpath.names_ripe
model_path = name_modelpath.model_path_ripe
output_video_path = ".\\media\\temp_processed_video.mp4"  # 全局变量 pests_names

# 全局变量
class_cls = []
model = None

"""
video标签对这三种视频格式是有具体要求的：
Ogg = 带有 Theora 视频编码 + Vorbis 音频编码
MPEG4 = 带有 H.264 视频编码 + AAC 音频编码
WebM = 带有 VP8 视频编码 + Vorbis 音频编码
"""


def upload(request):
    # 渲染上传页面
    return render(request, 'VideoTrackingCount.html')


def name_data():
    pests_names = ''
    # 假设这里是您的数据获取逻辑，这里使用了一些假数据作为示例
    # class_cls[18.0, 77.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0]
    # ['sheep', 'teddy bear']
    # [9, 1]
    print("class_cls", class_cls)
    class_cls_set1 = class_cls
    class_cls_set1 = set(class_cls_set1)
    class_cls_name = []
    class_cls_count = []
    print(class_cls_set1)
    for x in class_cls_set1:
        class_cl_name = name_modelpath.names_china[int(x)]
        pests_names = pests_names + class_cl_name + '，'
        class_cl_count = class_cls.count(x)
        class_cls_name.append(class_cl_name)
        class_cls_count.append(class_cl_count)
    print(class_cls_name)
    print(class_cls_count)
    print('pests_names', pests_names)
    return class_cls_name, class_cls_count, pests_names


# 图表数据上传
def get_chart_data(request):
    class_cls_name, class_cls_count, pests_names = name_data()
    chart_data = {
        # 'chart_title': 'ECharts 入门示例',
        'legend_name': '病虫害种类',
        'x_axis_data': class_cls_name,
        'series_name': '病虫害种类',
        'series_data': class_cls_count
    }
    return JsonResponse(chart_data)


def load_yolo_model():
    """预加载YOLO模型"""
    global model
    if model is None:
        print("正在初始化YOLO模型...")
        model = YOLO(model_path)
        print("YOLO模型初始化完成")
    return model


def process_video(request):
    if request.method == 'POST':
        # 从POST请求中获取base64编码的视频数据
        video_data = request.POST.get('video_base64')
        # 去掉base64编码中的前缀部分（data:image/...;base64）
        video_base64 = video_data.split(",")[1]

        # 解码base64数据到视频文件
        video_filename = decode_base64_to_video(video_base64)

        # 处理视频
        processed_video_url = process_video_function(video_filename)
        class_cls_name, class_cls_count, pests_names = name_data()
        print("pests_names", pests_names)
        tips = spark.spark(
            "请简单介绍下面几种植物病虫害，" + pests_names + "，并分别给出简单的专家建议，150字以内。然后综合分析一下这些植物病虫害，且给出整体建议。")
        print("tips", tips)

        # 返回处理后的视频URL给前端
        return JsonResponse({'processed_video_url': processed_video_url, 'tips': tips})
    else:
        print('Only POST method is allowed')
        return JsonResponse({'error': 'Only POST method is allowed'})


def decode_base64_to_video(base64_data):
    """
    将base64编码的视频数据解码成视频文件并保存
    :param base64_data: base64编码的视频数据
    :return: 视频文件路径
    """
    # 将base64编码的数据解码成视频文件
    video_bytes = base64.b64decode(base64_data)
    video_filename = os.path.join(settings.MEDIA_ROOT, 'uploaded_video.mp4')  # 媒体文件目录
    with open(video_filename, 'wb') as f:
        f.write(video_bytes)
        # video_filename G:\2024\text_325\media\uploaded_video.mp4
    return video_filename


def process_video_function(video_filename):
    """
    处理视频的函数，添加帧编号并将视频转换为H.264 + AAC编码的MP4格式
    :param video_filename: 输入视频文件路径
    :return: 处理后的视频URL
    """
    input_video_path = video_filename

    if not os.path.exists(os.path.dirname(output_video_path)):
        os.makedirs(os.path.dirname(output_video_path))

    add_frame_numbers(input_video_path, output_video_path)

    # Convert the video to H.264 + AAC using FFmpeg
    ffmpeg_command = f'ffmpeg -i "{output_video_path}" -c:v libx264 -c:a aac "{output_video_path[:-4]}_H264_AAC.mp4"'
    subprocess.call(ffmpeg_command, shell=True)

    print("Conversion to H.264 + AAC complete")
    # 返回处理后的视频URL
    return settings.MEDIA_URL + 'temp_processed_video.mp4'  # 返回相对URL


def add_frame_numbers(video_path, output_path):
    """
    为视频添加帧编号并保存
    :param video_path: 输入视频文件路径
    :param output_path: 输出视频文件路径
    """
    global annotated_frame, class_cls

    # 预加载模型
    model = load_yolo_model()

    max_id = 0
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("打开视频文件失败")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"视频信息: {frame_width}x{frame_height}, FPS: {fps}, 总帧数: {total_frames}")

    # 定义编解码器并创建VideoWriter对象
    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264编解码器
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    # 优化参数：跳帧处理
    frame_skip = max(1, fps // 15)  # 根据帧率动态调整跳帧
    print(f"使用跳帧设置: 每{frame_skip}帧处理1帧")

    track_history = defaultdict(lambda: [])
    class_ids = []
    class_cls = []  # 重置class_cls

    frame_count = 0
    processed_frames = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # 跳帧处理
        if frame_count % frame_skip != 0:
            continue

        processed_frames += 1

        # 显示进度
        if processed_frames % 10 == 0:
            progress = (frame_count / total_frames) * 100
            print(f"处理进度: {progress:.1f}% ({frame_count}/{total_frames} 帧)")

        # 在帧上运行YOLOv8追踪，持续追踪帧间的物体
        results = model.track(frame, persist=True, verbose=False)  # 关闭详细输出提高性能

        # 获取框和追踪ID
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xywh.cpu()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            max_id = max(max_id, max(track_ids, default=0))  # 更新最大ID
            class_datas = results[0].boxes.data.tolist()
            for sublist in class_datas:
                id_element = sublist[4]  # 获取id
                cls_element = sublist[6]  # 获取cls
                if id_element not in class_ids:  # 判断id_element是否在列表中
                    class_ids.append(id_element)
                    class_cls.append(cls_element)
            # class_ids [[429.401123046875, 369.25750732421875, 554.725830078125, 500.8100891113281, 5.0, 0.14823909103870392, 0.0]]
            # 这是一个包含了每个检测对象的详细信息的张量，其中每行代表一个对象。每行的数据格式为 [x_min, y_min, x_max, y_max, id, conf, cls]。
            print("class_datas", class_datas)
            print("class_ids:", class_ids)
            print("class_cls:", class_cls)
            class_cls_set = class_cls
            class_cls_set = set(class_cls_set)
            class_cls_set = list(class_cls_set)
            i = 0
            # 在帧上展示结果
            annotated_frame = results[0].plot()

            # 绘制追踪路径
            # for box, track_id in zip(boxes, track_ids):
            for box, track_id, class_cl_set in zip(boxes, track_ids, class_cls_set):
                x, y, w, h = box
                track = track_history[track_id]
                track.append((float(x), float(y)))  # x, y中心点
                if len(track) > 30:  # 在90帧中保留90个追踪点
                    track.pop(0)
                # 绘制追踪线
                points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)

                cv2.putText(
                    annotated_frame,
                    f"{names[int(class_cl_set)]}: {class_cls.count(class_cl_set)}",
                    (int(annotated_frame.shape[1] / 4), 50 + i * 30),
                    cv2.FONT_HERSHEY_SIMPLEX,  # 使用 cv2.FONT_HERSHEY_SIMPLEX 字体
                    1,
                    (0, 255, 0),
                    2,
                )  # 在视频帧中添加最大ID信息
                i = i + 1
            cv2.putText(
                annotated_frame,
                f"ALL Target object: {max_id}",
                (int(annotated_frame.shape[1] / 4), 50 + i * 30),
                cv2.FONT_HERSHEY_SIMPLEX,  # 使用 cv2.FONT_HERSHEY_SIMPLEX 字体
                1,
                (0, 255, 0),
                2,
            )  # 在视频帧中添加最大ID信息
        else:
            # 如果没有检测到目标，直接写入原帧
            annotated_frame = frame

        # 将帧写入输出视频
        out.write(annotated_frame)

        # 可选：显示处理进度（会降低性能）
        # cv2.imshow("RKNN Real-time inference screen", annotated_frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    # 释放资源
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"视频处理完成，共处理 {processed_frames} 帧")
# from django.shortcuts import render
# from django.http import JsonResponse
# import base64
# import cv2
# import subprocess
# import os
# from django.conf import settings
# from collections import defaultdict
# import numpy as np
# from ultralytics import YOLO
# from tool import name_modelpath, spark
#
# names = name_modelpath.names_ripe
# model_path = name_modelpath.model_path_ripe
# output_video_path = ".\\media\\temp_processed_video.mp4"  # 全局变量 pests_names
#
# """
# video标签对这三种视频格式是有具体要求的：
# Ogg = 带有 Theora 视频编码 + Vorbis 音频编码
# MPEG4 = 带有 H.264 视频编码 + AAC 音频编码
# WebM = 带有 VP8 视频编码 + Vorbis 音频编码
# """
#
#
# def upload(request):
#     # 渲染上传页面
#     return render(request, 'VideoTrackingCount.html')
#
#
# def name_data():
#     pests_names = ''
#     # 假设这里是您的数据获取逻辑，这里使用了一些假数据作为示例
#     # class_cls[18.0, 77.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0, 18.0]
#     # ['sheep', 'teddy bear']
#     # [9, 1]
#     print("class_cls", class_cls)
#     class_cls_set1 = class_cls
#     class_cls_set1 = set(class_cls_set1)
#     class_cls_name = []
#     class_cls_count = []
#     print(class_cls_set1)
#     for x in class_cls_set1:
#         class_cl_name = name_modelpath.names_china[int(x)]
#         pests_names = pests_names + class_cl_name + '，'
#         class_cl_count = class_cls.count(x)
#         class_cls_name.append(class_cl_name)
#         class_cls_count.append(class_cl_count)
#     print(class_cls_name)
#     print(class_cls_count)
#     print('pests_names', pests_names)
#     return class_cls_name, class_cls_count, pests_names
#
#
# # 图表数据上传
# def get_chart_data(request):
#     class_cls_name, class_cls_count, pests_names = name_data()
#     chart_data = {
#         # 'chart_title': 'ECharts 入门示例',
#         'legend_name': '病虫害种类',
#         'x_axis_data': class_cls_name,
#         'series_name': '病虫害种类',
#         'series_data': class_cls_count
#     }
#     return JsonResponse(chart_data)
#
#
# def process_video(request):
#     if request.method == 'POST':
#         # 从POST请求中获取base64编码的视频数据
#         video_data = request.POST.get('video_base64')
#         # 去掉base64编码中的前缀部分（data:image/...;base64）
#         video_base64 = video_data.split(",")[1]
#
#         # 解码base64数据到视频文件
#         video_filename = decode_base64_to_video(video_base64)
#
#         # 处理视频
#         processed_video_url = process_video_function(video_filename)
#         class_cls_name, class_cls_count, pests_names = name_data()
#         print("pests_names", pests_names)
#         tips = spark.spark(
#             "请简单介绍下面几种植物病虫害，" + pests_names + "，并分别给出简单的专家建议，150字以内。然后综合分析一下这些植物病虫害，且给出整体建议。")
#         print("tips", tips)
#
#         # 返回处理后的视频URL给前端
#         return JsonResponse({'processed_video_url': processed_video_url, 'tips': tips})
#     else:
#         print('Only POST method is allowed')
#         return JsonResponse({'error': 'Only POST method is allowed'})
#
#
# def decode_base64_to_video(base64_data):
#     """
#     将base64编码的视频数据解码成视频文件并保存
#     :param base64_data: base64编码的视频数据
#     :return: 视频文件路径
#     """
#     # 将base64编码的数据解码成视频文件
#     video_bytes = base64.b64decode(base64_data)
#     video_filename = os.path.join(settings.MEDIA_ROOT, 'uploaded_video.mp4')  # 媒体文件目录
#     with open(video_filename, 'wb') as f:
#         f.write(video_bytes)
#         # video_filename G:\2024\text_325\media\uploaded_video.mp4
#     return video_filename
#
#
# def process_video_function(video_filename):
#     """
#     处理视频的函数，添加帧编号并将视频转换为H.264 + AAC编码的MP4格式
#     :param video_filename: 输入视频文件路径
#     :return: 处理后的视频URL
#     """
#     input_video_path = video_filename
#
#     if not os.path.exists(os.path.dirname(output_video_path)):
#         os.makedirs(os.path.dirname(output_video_path))
#
#     add_frame_numbers(input_video_path, output_video_path)
#
#     # Convert the video to H.264 + AAC using FFmpeg
#     ffmpeg_command = f'ffmpeg -i "{output_video_path}" -c:v libx264 -c:a aac "{output_video_path[:-4]}_H264_AAC.mp4"'
#     subprocess.call(ffmpeg_command, shell=True)
#
#     print("Conversion to H.264 + AAC complete")
#     # 返回处理后的视频URL
#     return settings.MEDIA_URL + 'temp_processed_video.mp4'  # 返回相对URL
#
#
# def add_frame_numbers(video_path, output_path):
#     """
#     为视频添加帧编号并保存
#     :param video_path: 输入视频文件路径
#     :param output_path: 输出视频文件路径
#     """
#     global annotated_frame, class_cls
#     max_id = 0
#     cap = cv2.VideoCapture(video_path)
#     if not cap.isOpened():
#         print("打开视频文件失败")
#         return
#
#     frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#     fps = int(cap.get(cv2.CAP_PROP_FPS))
#
#     # 定义编解码器并创建VideoWriter对象
#     fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264编解码器
#     out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
#
#     # 加载YOLOv8模型
#     model = YOLO(model_path)
#
#     track_history = defaultdict(lambda: [])
#     class_ids = []
#     class_cls = []
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#         # 在帧上运行YOLOv8追踪，持续追踪帧间的物体
#         results = model.track(frame, persist=True)
#
#         # 获取框和追踪ID
#         if results[0].boxes.id is not None:
#             boxes = results[0].boxes.xywh.cpu()
#             track_ids = results[0].boxes.id.int().cpu().tolist()
#             max_id = max(max_id, max(track_ids, default=0))  # 更新最大ID
#             class_datas = results[0].boxes.data.tolist()
#             for sublist in class_datas:
#                 id_element = sublist[4]  # 获取id
#                 cls_element = sublist[6]  # 获取cls
#                 if id_element not in class_ids:  # 判断id_element是否在列表中
#                     class_ids.append(id_element)
#                     class_cls.append(cls_element)
#             # class_ids [[429.401123046875, 369.25750732421875, 554.725830078125, 500.8100891113281, 5.0, 0.14823909103870392, 0.0]]
#             # 这是一个包含了每个检测对象的详细信息的张量，其中每行代表一个对象。每行的数据格式为 [x_min, y_min, x_max, y_max, id, conf, cls]。
#             print("class_datas", class_datas)
#             print("class_ids:", class_ids)
#             print("class_cls:", class_cls)
#             class_cls_set = class_cls
#             class_cls_set = set(class_cls_set)
#             class_cls_set = list(class_cls_set)
#             i = 0
#             # 在帧上展示结果
#             annotated_frame = results[0].plot()
#
#             # 绘制追踪路径
#             # for box, track_id in zip(boxes, track_ids):
#             for box, track_id, class_cl_set in zip(boxes, track_ids, class_cls_set):
#                 x, y, w, h = box
#                 track = track_history[track_id]
#                 track.append((float(x), float(y)))  # x, y中心点
#                 if len(track) > 30:  # 在90帧中保留90个追踪点
#                     track.pop(0)
#                 # 绘制追踪线
#                 points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
#                 cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)
#
#                 cv2.putText(
#                     annotated_frame,
#                     f"{names[int(class_cl_set)]}: {class_cls.count(class_cl_set)}",
#                     (int(annotated_frame.shape[1] / 4), 50 + i * 30),
#                     cv2.FONT_HERSHEY_SIMPLEX,  # 使用 cv2.FONT_HERSHEY_SIMPLEX 字体
#                     1,
#                     (0, 255, 0),
#                     2,
#                 )  # 在视频帧中添加最大ID信息
#                 i = i + 1
#             cv2.putText(
#                 annotated_frame,
#                 f"ALL Target object: {max_id}",
#                 (int(annotated_frame.shape[1] / 4), 50 + i * 30),
#                 cv2.FONT_HERSHEY_SIMPLEX,  # 使用 cv2.FONT_HERSHEY_SIMPLEX 字体
#                 1,
#                 (0, 255, 0),
#                 2,
#             )  # 在视频帧中添加最大ID信息
#         else:
#             pass
#
#         # 将帧写入输出视频
#         out.write(annotated_frame)
#         cv2.imshow("RKNN Real-time inference screen", annotated_frame)
#         if cv2.waitKey(25) & 0xFF == ord('q'):
#             break
#
#     # 释放资源
#     cap.release()
#     out.release()
#     cv2.destroyAllWindows()
#     print("视频处理完成")
