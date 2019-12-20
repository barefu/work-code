import time

import requests
import xlsxwriter
from lxml import etree


class BackgroundSprider(object):
    def __init__(self):
        self.workbook = xlsxwriter.Workbook('D:\\后台数据.xlsx')
        self.sheet = self.workbook.add_worksheet('data')
        self.cell_format = self.workbook.add_format()
        self.cell_format.set_font_name('Arial Unicode MS')
        self.cell_format.set_font_size(10)
        self.sheet.write(0, 0, 'ID', self.cell_format)
        self.sheet.write(0, 1, '商品名字', self.cell_format)
        self.sheet.write(0, 2, '编码', self.cell_format)
        self.sheet.write(0, 3, '价格', self.cell_format)
        self.sheet.write(0, 4, '主图', self.cell_format)
        self.sheet.write(0, 5, '轮播图', self.cell_format)
        self.sheet.write(0, 6, '详情图', self.cell_format)
        self.sheet.write(0, 7, '小字段数', self.cell_format)
        self.count = 1
        self.headers = {
            'Cookie': 'PHPSESSID=1qmgmmlj2ut6dsef9bae9q66tu',
            'User_Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKi'
                          't/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
        }

    def details_number(self, id):
        url = 'http://www.ping1go.com/admin/product/param.html?id={}'.format(id)
        while True:
            try:
                r = requests.get(url, headers=self.headers)
            except Exception as e:
                print(e)
                time.sleep(3)
            else:
                if r.status_code == 200:
                    break
                else:
                    break
        html = etree.HTML(r.text)
        value = html.xpath('//input[@class="layui-input paramValueTitle"]/@value')
        count = 0
        for i in value:
            if i:
                count += 1
            else:
                pass
        return count

    def info_page(self):
        url = 'http://www.ping1go.com/admin/product/lists/node_id/58.html'
        for page in range(1, 1483):
            data = {
                'page': '{}'.format(page),
                'limit': '10'
            }
            while True:
                try:
                    r = requests.post(url, headers=self.headers, data=data)
                except Exception as e:
                    print(e)
                    time.sleep(3)
                else:
                    if r.status_code == 200:
                        break
                    else:
                        break
            info_json = r.json()
            self.info_json(info_json)
            print("End of page {}".format(page))

    def store_img_number(self, id):
        url = 'http://www.ping1go.com/home/product/search.html?keywords={}'.format(id)
        while True:
            try:
                r = requests.get(url, headers=self.headers)
            except Exception as e:
                print(e)
                time.sleep(3)
            else:
                if r.status_code == 200:
                    break
                else:
                    break
        html = etree.HTML(r.text)
        img = html.xpath('//div[@class="layui-col-md4"]/div/a/img/@src')
        if img:
            number = 1
        else:
            number = 'None'
        url1 = 'http://www.ping1go.com/home/product/detail/product_id/{}.html'.format(id)
        while True:
            try:
                r1 = requests.get(url1, headers=self.headers)
            except Exception as e:
                print(e)
                time.sleep(3)
            else:
                if r1.status_code == 200:
                    break
                else:
                    break
        html = etree.HTML(r1.text)
        li = html.xpath('//ul[@class="img_x"]/li')
        if li:
            number1 = len(li)
        else:
            number1 = 'None'
        return number, number1

    def info_json(self, json):
        info_list = json['data']['data']
        for info in info_list:
            ID = info['id']
            title = info['title']
            xhbh = info['xhbh']
            price = info['price']
            main_img_number,  little_img_number = self.store_img_number(ID)
            info_img = info['content']
            if info_img:
                html = etree.HTML(info_img)
                img = html.xpath('//img')
                info_img_count = len(img)
            else:
                info_img_count = 0
            details_num = self.details_number(ID)
            self.sheet.write(self.count, 0, ID, self.cell_format)
            self.sheet.write(self.count, 1, title, self.cell_format)
            self.sheet.write(self.count, 2, xhbh, self.cell_format)
            self.sheet.write(self.count, 3, price, self.cell_format)
            self.sheet.write(self.count, 4, main_img_number, self.cell_format)
            self.sheet.write(self.count, 5, little_img_number, self.cell_format)
            self.sheet.write(self.count, 6, info_img_count, self.cell_format)
            self.sheet.write(self.count, 7, details_num, self.cell_format)
            self.count += 1

    def main(self):
        self.info_page()
        self.workbook.close()


if __name__ == '__main__':
    bg_spider = BackgroundSprider()
    bg_spider.main()
