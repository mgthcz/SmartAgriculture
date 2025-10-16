import input_speech, print_speech, speech_detect
import tool.spark as spark

speak = input_speech.Speak()  # 用户输入
readTalk = speech_detect.ReadWav()  # 语音转文字
robotSay = print_speech.RobotSay()  # 文字转语音

robotSay.say("欢迎使用语音问答及模块控制系统，快来向我提问叭！")  # 播放回答信息
while True:
    speak.my_record()  # 录音
    text = readTalk.predict()['result'][0]  # 调用百度AI接口, 将录音转化为文本信息
    if "退出" in text:
        robotSay.say("系统已退出！感谢您的使用！")  # 播放回答信息
        break

    print("本人说:", text)  # 输出文本信息
    response_dialogue = spark.spark(text)  # 调用青云客机器人回答文本信息并返回
    print("青云客说:", response_dialogue)  # 输出回答文本信息
    robotSay.say(response_dialogue)  # 播放回答信息
