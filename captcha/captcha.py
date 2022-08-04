from io import BytesIO
import random
from PIL import Image, ImageDraw, ImageFont
import json
import base64


data = json.loads(
    open('captcha/history_in_today.json', encoding="utf8").read())

LINE_CHAR_COUNT = 20
CHAR_SIZE = 30
TYPES = {1: "大事件", 2: "出生", 3: "逝世"}
BASE64_FMT = 'png'


def _line_break(line):
    _WIDTH = 0
    list = [""]
    for c in line:
        if len(c.encode("utf8")) == 3:
            _CHAR_SIZE = CHAR_SIZE  # 中文全宽
        else:
            _CHAR_SIZE = CHAR_SIZE // 2
        if(c == "\n"):
            _WIDTH = 0
            list.append("")
            continue
        if LINE_CHAR_COUNT*CHAR_SIZE >= _WIDTH + _CHAR_SIZE:
            _WIDTH += _CHAR_SIZE
            list[-1] += c
        else:
            _WIDTH = 0
            _WIDTH += _CHAR_SIZE
            list.append(c)
    return(list)


def _getImg(content):
    output_str = "["+TYPES[content['type']]+"]"+content['data']
    output_str = _line_break(output_str)
    # print(output_str)
    d_font = ImageFont.truetype(
        font="captcha/SourceHanSansCN-Normal.otf", size=CHAR_SIZE)
    # lines = output_str.count("\n")
    lines = len(output_str)

    image = Image.new(
        "L", ((LINE_CHAR_COUNT * CHAR_SIZE) + 1,
              CHAR_SIZE * lines + 20), "white"
    )
    draw_table = ImageDraw.Draw(im=image)
    for i in range(lines):
        draw_table.text((0, i * CHAR_SIZE),
                        output_str[i], font=d_font, fill="black")
    output_buffer = BytesIO()
    image.save(output_buffer, format=BASE64_FMT)
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode('utf-8')
    return f'data:image/{BASE64_FMT};base64,' + base64_str
    # image.save(name, "PNG")
    # image.close()


def getCaptcha():
    _random_num = random.randint(0, len(data) - 1)
    print(data[_random_num]['year'])
    return {
        "id": _random_num,
        "base64": _getImg(data[_random_num])
    }

def checkCaptcha(id, answer):
    if data[id]['year'] == str(answer):
        return True
    else:
        return False

# print(getCaptcha())