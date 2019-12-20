import requests
from lxml import etree
import time
import os
import PIL.Image
import pandas as pd


class GetDetail(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'
        }

    def img_download(self, row):
                cate = row[0]
                if '/' in cate:
                    cate = cate.replace('/', '、')
                cate = cate.replace('>', '\\')
                self.path = 'D:\\imgs\\' + cate
                if os.path.exists(self.path):
                    pass
                else:
                    os.makedirs(self.path)
                detail_url = row[2]
                while True:
                    try:
                        detail_res = requests.get(detail_url, headers=self.headers)
                    except Exception as e:
                        print('Error!', e)
                        time.sleep(3)
                    else:
                        if detail_res.status_code == 200:
                            break
                        else:
                            print('Error!')
                            time.sleep(3)
                response = etree.HTML(detail_res.text)
                n_name_list = response.xpath('/html/body/div[4]/div[1]/span[4]/p/board()')
                if n_name_list:
                    n_name = n_name_list[0]
                else:
                    return 'Game over!!!'
                n_name = n_name.replace('"', '').replace('*', '-').replace('|', '、').replace('/', '、')
                print(n_name)
                main_img_urls = response.xpath('//ul[@id="img-items"]/li/img/@src')
                info_img_urls = response.xpath('//div[@class="procuct_detail_fl"]/img/@src')
                main_img_name = []
                for n in range(len(main_img_urls[:3])):
                    while True:
                        try:
                            res = requests.get(main_img_urls[n], headers=self.headers)  # 获取下一个列表页
                        except Exception as e:
                            print('Error!', e)
                            time.sleep(2)
                        else:
                            if res.status_code == 200:
                                break
                            else:
                                print('Error!')
                                return
                    filename = n_name + '_' + str(n)+'.jpg'
                    main_img_name.append(filename)
                    with open(self.path + '\\' + filename, 'wb') as f:
                        f.write(res.content)
                    try:
                        img = PIL.Image.open(self.path + '\\' + filename)
                        img = img.resize((800, 800))
                        image = img.convert("RGB")
                        image.save(self.path + '\\' + filename, "JPEG")
                    except Exception as e:
                        print('Error!', e)
                        pass
                for n in range(len(info_img_urls)):
                    while True:
                        try:
                            res = requests.get(info_img_urls[n], headers=self.headers)
                        except Exception as e:
                            print('Error!', e)
                            time.sleep(2)
                        else:
                            if res.status_code == 200:
                                break
                            else:
                                print('Error!')
                                time.sleep(2)
                                return
                    filename = n_name + '_' + str(n) + '.jpg'
                    with open('D:\\infoimg' + '\\' + filename, 'wb') as f:
                        f.write(res.content)
                if len(info_img_urls) == 1:
                    no_img_url = 'http://222.143.21.205:8081/static/os/images/no_picture.png'
                    if info_img_urls[0] != no_img_url:
                        while True:
                            try:
                                res = requests.get(info_img_urls[0], headers=self.headers)
                            except Exception as e:
                                print('Error!', e)
                                time.sleep(2)
                            else:
                                if res.status_code == 200:
                                    break
                                else:
                                    print('Error!')
                                    return
                        filename = n_name + '.jpg'
                        with open(self.path + '\\' + filename, 'wb') as f:
                            f.write(res.content)
                    else:
                        # 拼接主图作为详情图
                        IMAGES_PATH = self.path + '\\'  # 图片集地址
                        IMAGE_SIZE = 800  # 每张小图片的大小
                        IMAGE_ROW = len(main_img_name)  # 图片间隔，也就是合并成一张图后，一共有几行
                        IMAGE_COLUMN = 1  # 图片间隔，也就是合并成一张图后，一共有几列
                        # 获取图片集地址下的所有图片名称
                        # image_names = []
                        # for n in range(len(info_img_urls)):
                        #     file = n_name + '_' + str(n) + '.jpg'
                        #     image_names.append(file)
                        to_image = PIL.Image.new('RGB', (IMAGE_COLUMN * IMAGE_SIZE, IMAGE_ROW * IMAGE_SIZE))  # 创建一个新图
                        # 循环遍历，把每张图片按顺序粘贴到对应位置上
                        file = n_name + '.jpg'
                        for y in range(1, IMAGE_ROW + 1):
                            for x in range(1, IMAGE_COLUMN + 1):
                                try:
                                    from_image = PIL.Image.open(
                                        IMAGES_PATH + main_img_name[IMAGE_COLUMN * (y - 1) + x - 1]).resize(
                                        (IMAGE_SIZE, IMAGE_SIZE), PIL.Image.ANTIALIAS)
                                    to_image.paste(from_image, ((x - 1) * IMAGE_SIZE, (y - 1) * IMAGE_SIZE))
                                    to_image.save(self.path + '\\' + file)
                                except Exception as e:
                                    print('join img error!', e)
                                    pass
                else:
                    IMAGES_PATH = 'D:\\infoimg' + '\\'  # 图片集地址
                    IMAGE_SIZE = 800  # 每张小图片的大小
                    IMAGE_ROW = len(info_img_urls)  # 图片间隔，也就是合并成一张图后，一共有几行
                    IMAGE_COLUMN = 1  # 图片间隔，也就是合并成一张图后，一共有几列
                    # 获取图片集地址下的所有图片名称
                    image_names = []
                    for n in range(len(info_img_urls)):
                        file = n_name + '_' + str(n) + '.jpg'
                        image_names.append(file)
                    to_image = PIL.Image.new('RGB', (IMAGE_COLUMN * IMAGE_SIZE, IMAGE_ROW * IMAGE_SIZE))  # 创建一个新图
                    # 循环遍历，把每张图片按顺序粘贴到对应位置上
                    file = n_name + '.jpg'
                    for y in range(1, IMAGE_ROW + 1):
                        for x in range(1, IMAGE_COLUMN + 1):
                            try:
                                from_image = PIL.Image.open(IMAGES_PATH + image_names[IMAGE_COLUMN * (y - 1) + x - 1]).resize(
                                    (IMAGE_SIZE, IMAGE_SIZE), PIL.Image.ANTIALIAS)
                                to_image.paste(from_image, ((x - 1) * IMAGE_SIZE, (y - 1) * IMAGE_SIZE))
                                to_image.save(self.path + '\\' + file)
                            except Exception as e:
                                print('join img error!', e)
                                pass

    def read_data(self):
        all_data = pd.read_excel('D:\\base of data.xlsx')
        shape = all_data.shape[0]
        for row in range(34224, shape):
            row_data = all_data.iloc[row]
            self.img_download(row_data)


if __name__ == '__main__':
    g_url = GetDetail()
    g_url.read_data()
