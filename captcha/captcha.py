import os
import re
import random
from PIL import Image, ImageDraw, ImageFont
import json

history_in_today = json.loads(open('history_in_today.json').read())
# type: 1：大事件，2：出生，3：逝世
# print(history_in_today[0])

LINE_CHAR_COUNT = 20 * 2
CHAR_SIZE = 35
TABLE_WIDTH = 5
TYPES = {1: "大事件", 2: "出生", 3: "逝世"}


def line_break(line):
    ret = ""
    width = 0
    for c in line:
        if len(c.encode("utf8")) == 3:  # 中文
            if LINE_CHAR_COUNT == width + 1:  # 剩余位置不够一个汉字
                width = 2
                ret += "\n" + c
            else:  # 中文宽度加2，注意换行边界
                width += 2
                ret += c
        else:
            if c == "\t":
                space_c = TABLE_WIDTH - width % TABLE_WIDTH  # 已有长度对TABLE_WIDTH取余
                ret += " " * space_c
                width += space_c
            elif c == "\n":
                width = 0
                ret += c
            else:
                width += 1
                ret += c
        if width >= LINE_CHAR_COUNT:
            ret += "\n"
            width = 0
    if ret.endswith("\n"):
        return ret
    return ret + "\n"


def getImg(content, name):
    output_str = "["+TYPES[content['type']]+"]"+content['data']
    output_str = line_break(output_str + "\n")
    d_font = ImageFont.truetype(font="./SourceHanSansCN-Normal.otf", size=CHAR_SIZE)
    lines = output_str.count("\n")

    image = Image.new(
        "L", (LINE_CHAR_COUNT * CHAR_SIZE // 2, CHAR_SIZE * (lines+1)), "white"
    )
    draw_table = ImageDraw.Draw(im=image)
    draw_table.text(xy=(0, 0), text=output_str,
                    fill="#000000", font=d_font, spacing=4)
    # image.save('../../static/tmp/'+name, 'PNG')
    image.save(name, "PNG")
    image.close()


getImg(history_in_today[random.randint(
    0, len(history_in_today) - 1)], "captcha.png")
