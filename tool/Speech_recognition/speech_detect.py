from aip import AipSpeech

""" 你的 APPID AK SK """
APP_ID = '70432890'
API_KEY = '9mZinloFiT4WkfwPcmJXzZnC'
SECRET_KEY = 'BKoSghGipUOpmo7afRL833IXEhV0vdCx'  # 此处填写自己的密钥

"""调用接口, 调用BaiDu AI 接口进行录音、语音识别"""
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)


class ReadWav():
    # 读取文件
    def get_file_content(self, filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    def predict(self):
        # 调用百度AI的接口, 识别本地文件
        return client.asr(self.get_file_content('./voices/myvoices.wav'), 'wav', 16000, {
            'dev_pid': 1537,
        })


# readWav = ReadWav()  # 实例化方法
# print(readWav.predict())  # 调用识别方法, 并输出
