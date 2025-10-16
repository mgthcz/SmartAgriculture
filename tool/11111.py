from PIL import Image
import os

# 定义文件夹路径
folder_path = r'D:\web大作业\imagessss\love\2023'  # 请替换为你图片文件夹的路径

# 设定目标宽度和高度
target_width = 250
target_height = 360

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    # 构造文件的完整路径
    file_path = os.path.join(folder_path, filename)

    # 检查文件是否为图片
    if os.path.isfile(file_path):
        try:
            # 打开图片文件
            with Image.open(file_path) as img:
                # 获取图片的原始宽高
                width, height = img.size

                # 调整图片大小，保持比例
                img_resized = img.resize((target_width, target_height))

                # 保存调整后的图片，覆盖原文件
                img_resized.save(file_path)

                print(f"已处理: {filename} (原始大小: {width}x{height}, 调整后: {target_width}x{target_height})")
        except Exception as e:
            print(f"无法处理 {filename}: {e}")
