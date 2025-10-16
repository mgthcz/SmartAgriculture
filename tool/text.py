import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np

cap = cv2.VideoCapture(0)


# font=cv2.FONT_ITALIC
def cv2AddChineseText(img, text, position, textColor=(0, 255, 0), textSize=30):
    if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype(
        "simsun.ttc", textSize, encoding="utf-8")
    # 绘制文本
    draw.text(position, text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


while (1):
    ret, frame = cap.read()
    # 展示图片
    frame = cv2AddChineseText(frame, "劳资最帅", (123, 123), (0, 255, 0), 30)
    cv2.imshow('capture', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# 释放对象和销毁窗口
cap.release()
cv2.destroyAllWindows()
