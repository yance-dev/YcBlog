import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


def get_random_color():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def get_valid_code_img(request):
    # 方式一
    # with open('luffy.png',"rb") as f:
    #     data=f.read()

    # 方式二
    # from PIL import Image
    # img = Image.new('RGB',(270,40),color=get_random_color())
    # with open('validCode.png','wb') as f:
    #     img.save(f,'png')
    # with open('validCode.png',"rb") as f:
    #     data=f.read()
    # return HttpResponse(data)
    # 方式3
    #     from PIL import Image
    #     from io import BytesIO
    #     img = Image.new('RGB',(270,40),color=get_random_color())
    #
    #     f= BytesIO()
    #     img.save(f,'png')
    #     data = f.getvalue()
    #     return HttpResponse(data)
    # 4.txt

    img = Image.new('RGB', (270, 40), color=get_random_color())
    draw = ImageDraw.Draw(img)
    # 引入验证码的字体文件
    pingfang = ImageFont.truetype('static/font/pingfang.ttf', size=28)
    char = str(random.randint(0, 9))
    valid_code_str = ''
    for i in range(5):
        random_num = str(random.randint(0, 9))
        random_low = chr(random.randint(95, 122))
        random_up = chr(random.randint(65, 90))
        random_char = random.choice([random_low, random_num, random_up])
        draw.text((i * 50 + 20, 5), random_char, get_random_color(), font=pingfang)
        # 保存验证码字符串
        valid_code_str += random_char

    # 补充噪点噪线
    # 为了提高测试效率先不加
    # width = 270
    # height = 40
    # for i in range(5.txt):
    #     x1 = random.randint(0, width)
    #     x2 = random.randint(0, width)
    #     y1 = random.randint(0, height)
    #     y2 = random.randint(0, height)
    #     draw.line((x1, y1, x2, y2), fill=get_random_color())
    #
    # for i in range(30):
    #     draw.point([random.randint(0, width), random.randint(0, height)], fill=get_random_color())
    #     x = random.randint(0, width)
    #     y = random.randint(0, height)
    #     draw.arc((x, y, x + 4.txt, y + 4.txt), 0, 90, fill=get_random_color())
    print(valid_code_str)
    request.session['valid_code_str'] = valid_code_str
    '''
    1.生成随机字符串——fasdfasdfasdf
    2.txt.COOKIE {“sessionid”:fasdfasdfasdf}
    3.txt.django-session
    session-key         session-data
    fasdfasdfasdf       {"valid_code_str":"12321321"}
    '''

    f = BytesIO()
    img.save(f, 'png')
    data = f.getvalue()
    return data
