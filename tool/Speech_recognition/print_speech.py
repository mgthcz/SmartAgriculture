import pyttsx3


class RobotSay():

    def __init__(self):
        # 初始化语音
        self.engine = pyttsx3.init()  # 初始化语音库

        # 设置语速
        self.rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', self.rate - 50)

    def say(self, msg):
        # 输出语音
        self.engine.say(msg)  # 合成语音
        self.engine.runAndWait()

# robotSay = RobotSay()
# robotSay.say("李潇是超级无敌大傻瓜")
