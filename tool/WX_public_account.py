import json
import requests

# 微信公众测试号账号（填写自己的）
APPID = "wx3ea1cfaaeea911de"
# 微信公众测试号密钥（填写自己的）
APPSECRET = "e92af7ea0bea11284d917f64241c52a3"
# 消息接收者
TOUSER = 'oiTcJ6T37iICxi8b52j2oLtP1JU0'
# 消息模板id
TEMPLATE_ID = 'GFTi2yf65znoVXMbT0sNLXsgK_G9WJbDiXuc7uuS7g0'
# 点击跳转链接（可无）
CLICK_URL = 'https://blog.net/sxdgy_?spm=1011.2415.3001.5349'


class AccessToken(object):
    def __init__(self, app_id=APPID, app_secret=APPSECRET) -> None:
        self.app_id = app_id
        self.app_secret = app_secret

    def get_access_token(self) -> str:
        """
        获取access_token凭证
        :return: access_token
        """
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        resp = requests.get(url)
        result = resp.json()
        if 'access_token' in result:
            return result["access_token"]
        else:
            print(result)


class SendMessage(object):
    def __init__(self, touser=TOUSER, template_id=TEMPLATE_ID, click_url=CLICK_URL) -> None:
        """
        构造函数
        :param touser: 消息接收者
        :param template_id: 消息模板id
        :param click_url: 点击跳转链接（可无）
        """
        self.access_token = AccessToken().get_access_token()
        self.touser = touser
        self.template_id = template_id
        self.click_url = click_url

    def get_send_data(self, json_data) -> object:
        """
        获取发送消息data
        :param json_data: json数据对应模板
        :return: 发送的消息体
        """
        return {
            "touser": self.touser,
            "template_id": self.template_id,
            "url": self.click_url,
            "topcolor": "#FF0000",
            # json数据对应模板
            "data": {
                "name": {
                    "value": json_data["name"],
                    # 字体颜色
                    "color": "#173177"
                },
                "code": {
                    "value": json_data["code"],
                    "color": "#173177"
                },
            }
        }

    def send_message(self, json_data) -> None:
        """
        发送消息
        :param json_data: json数据
        :return:
        """
        # 模板消息请求地址
        url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={self.access_token}"
        data = json.dumps(self.get_send_data(json_data))
        resp = requests.post(url, data=data)
        result = resp.json()
        if result["errcode"] == 0:
            print("消息发送成功")
        else:
            print(result)


def main(name="种植户", code="大棚土壤湿度低于警戒值，请及时浇水！"):
    # 实例SendMessage
    sm = SendMessage()
    # 获取接口返回数据
    json_data = {"name": name, "code": code}
    # 发送消息
    sm.send_message(json_data=json_data)


main()
