import os
import subprocess


def process_video_function(video_filename):
    """
    处理视频的函数，添加空白音频并将视频转换为H.264 + AAC编码的MP4格式
    :param video_filename: 输入视频文件路径
    :return: 处理后的视频文件路径
    """
    # 获取输入视频的目录和文件名
    input_video_path = video_filename
    video_directory = os.path.dirname(input_video_path)
    video_filename_without_extension = os.path.splitext(os.path.basename(input_video_path))[0]

    # 构造输出视频的路径
    output_video_path = os.path.join(video_directory, f"{video_filename_without_extension}_with_blank_audio.mp4")
    output_h264_aac_path = os.path.join(video_directory, f"{video_filename_without_extension}_H264_AAC.mp4")

    # 确保输出文件夹存在
    if not os.path.exists(video_directory):
        os.makedirs(video_directory)

    # 使用FFmpeg给视频添加空白音频
    # -an：表示不处理原始音频
    # -f lavfi：使用lavfi（FFmpeg的虚拟音频生成器）
    # -t 00:00:10：设置空白音频的时长为10秒（可以根据视频的实际时长调整）
    ffmpeg_command = f'ffmpeg -i "{input_video_path}" -f lavfi -t 00:00:10 -i anullsrc=r=44100:cl=stereo -c:v copy -c:a aac -shortest "{output_video_path}"'

    # 调用 FFmpeg 命令
    print(f"Running command: {ffmpeg_command}")
    subprocess.call(ffmpeg_command, shell=True)

    # 现在使用FFmpeg将视频转换为H.264 + AAC
    ffmpeg_command = f'ffmpeg -i "{output_video_path}" -c:v libx264 -c:a aac "{output_h264_aac_path}"'

    # 调用 FFmpeg 命令
    print(f"Running command: {ffmpeg_command}")
    subprocess.call(ffmpeg_command, shell=True)

    print(f"视频处理完成，保存为: {output_h264_aac_path}")

    return output_h264_aac_path


# 示例调用
output_path = process_video_function(r"D:\xiangmu\xianshangjiaoxue\jiankong\1.mp4")
print(f"处理后的视频文件保存在: {output_path}")
