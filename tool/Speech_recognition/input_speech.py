import time
import wave
from pyaudio import PyAudio, paInt16

framerate = 16000  # 采样率
num_samples = 2000  # 采样点
channels = 1  # 声道
sampwidth = 2  # 采样宽度2bytes
FILEPATH = './voices/myvoices.wav'  # 该文件目录要存在


# 用于接收用户的语音输入, 并生成wav音频文件(wav、pcm、mp3的区别可详情百度)
class Speak():

    # 将音频数据保存到wav文件之中
    def save_wave_file(self, filepath, data):
        wf = wave.open(filepath, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(framerate)
        wf.writeframes(b''.join(data))
        wf.close()

    # 进行语音录制工作
    def my_record(self):
        pa = PyAudio()
        # 打开一个新的音频stream
        stream = pa.open(format=paInt16, channels=channels,
                         rate=framerate, input=True, frames_per_buffer=num_samples)
        my_buf = []  # 存放录音数据

        t = time.time()
        print('正在讲话...')

        while time.time() < t + 5:  # 设置录音时间（秒）
            # 循环read，每次read 2000frames
            string_audio_data = stream.read(num_samples)
            my_buf.append(string_audio_data)

        print('讲话结束')
        self.save_wave_file(FILEPATH, my_buf)  # 保存下录音数据
        stream.close()
#
#
# speech = Speak()
# speech.my_record()
