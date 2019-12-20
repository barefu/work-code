import numpy as np
from PIL import Image, ImageEnhance
import pytesseract
import os

# standard = 50
# im = Image.open('123.jpg')
# # im = ImageEnhance.Contrast(im)
# # im = im.enhance(1)
# im.show(im)
# print(pytesseract.image_to_string(im))

# a = "yzmxq('ZDE1MWVjNDg1M2JiNDUyMTgzYzIwZWIyMjE1ZTUwN2M')"
# patt = "'(.*)'"
# p = re.findall(patt, a)[0]
# print(p)
#
# s = b'\u9a8c\u8bc1\u7801\u9519\u8bef'
# print(s.decode('unicode_escape'))
#
file_name = os.listdir('D:\\captcha-img')
names = [name.split('.')[0] for name in file_name]
l = [os.path.join('D:\\captcha-img', name) for name in file_name]
for i in range(356):
    image_data = Image.open(l[i])
    im = ImageEnhance.Contrast(image_data)
    im = im.enhance(4)
    im = im.convert('L')
    im.save('D:\\captcha-img-deal\\{}.png'.format(names[i]))
    print('第{}张写入成功！'.format(i))
