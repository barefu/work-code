from datetime import datetime
import requests
import xlsxwriter
from lxml import etree
import xlwt
import time
import threading
import pandas as pd

now_time = datetime.now()
today_time = now_time.date()
md = today_time.strftime('%m.%d')


class GetDetail(object):
    def __init__(self, i):
        self.i = i
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/77.0.3865.120 Safari/537.36 '
        }
        if self.i == 0:
            self.exl_name = '鹤壁平氏'
        else:
            self.exl_name = '郑州平氏'
        self.workbook = xlsxwriter.Workbook('D:\\{}显示.xlsx'.format(md + self.exl_name))
        self.sheet = self.workbook.add_worksheet('data')
        self.cell_format = self.workbook.add_format()
        self.cell_format.set_font_name('Arial Unicode MS')
        self.cell_format.set_font_size(10)
        self.sheet.write(0, 0, '一级类型', self.cell_format)
        self.sheet.write(0, 1, '二级类型', self.cell_format)
        self.sheet.write(0, 2, '三级类型', self.cell_format)
        self.sheet.write(0, 3, '商品名称', self.cell_format)
        self.sheet.write(0, 4, '详情页链接', self.cell_format)
        self.sheet.write(0, 5, '商品价格', self.cell_format)
        self.sheet.write(0, 6, '供应商', self.cell_format)
        self.count = 1
        self.th_list = []

    def get_url(self, url):
        res = requests.get(url=url, headers=self.headers)
        self.cookies = res.cookies.get_dict()
        response = etree.HTML(res.text)
        div = response.xpath('//div[@class="category-layer opacity_index"]/div')
        for div_list in div:
            first_name = div_list.xpath('dl[@class="cat"]/dt[@class="cat-name"]/a/text()')
            d_list = div_list.xpath('div/div/div/dl')
            for dd in d_list:
                # 每个dd开一个线程
                th = threading.Thread(target=self.list_url, args=(dd, first_name,))
                th.start()
                self.th_list.append(th)

    def list_url(self, dd, first_name):  # 获取列表页url
        class1 = dd.xpath('dt/a/em/text()')
        a_list = dd.xpath('dd/a')
        for a in a_list:
            href = a.xpath('@href')[0]
            list_href = href.split('=')[1]
            s_s = a.xpath('text()')
            category = first_name[0] + '>' + class1[0] + '>' + s_s[0].strip()
            # print(category)
            url = 'http://222.143.21.205:8081/category/list'
            for page in range(1, 500):
                data = {
                    'pmbh': '{}'.format(list_href),
                    # 'ppbh': '40282a3e177c9ede01177cafd2c5003b',
                    'pageNo': '{}'.format(page),
                    'dsmc': '{}'.format(self.exl_name)
                }
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
                    'Cookie': 'contrastCookie=; SESSION=ed9a6d0f-96d2-4d93-9d7c-e6a14d74f806',
                }
                while True:
                    try:
                        next_res = requests.post(url=url, headers=headers, data=data, timeout=20)  # 获取下一个列表页
                    except Exception as e:
                        print(e)
                        time.sleep(3)
                    else:
                        if next_res.status_code == 200:
                            break
                        else:
                            break
                html = etree.HTML(next_res.text)
                a_s = html.xpath('//div[@class="item-name"]/a')
                prices = html.xpath('//div[@class="item-price"]/em/text()')
                companys = html.xpath('//div[@class="item-company "]/em/text()')
                if not a_s:
                    print(category, 'page:', page)
                    break
                # 设定Excel写入格式
                style = xlwt.easyxf('align: wrap on')
                style.alignment.wrap = 1
                for num in range(len(a_s)):
                    company = companys[num]
                    href = a_s[num].xpath('@href')[0]
                    name = a_s[num].xpath('@title')
                    price = prices[num]
                    price = price.split('￥')
                    detail_url = 'http://222.143.21.205:8081' + href
                    self.sheet.write(self.count, 0, first_name[0], self.cell_format)
                    self.sheet.write(self.count, 1, class1[0], self.cell_format)
                    self.sheet.write(self.count, 2, s_s[0], self.cell_format)
                    self.sheet.write(self.count, 3, name[0], self.cell_format)
                    self.sheet.write(self.count, 4, detail_url, self.cell_format)
                    self.sheet.write(self.count, 5, price[1], self.cell_format)
                    self.sheet.write(self.count, 6, company, self.cell_format)
                    self.count += 1

    def start(self):
        base_url = ['http://222.143.21.205:8081/?area=00390006', 'http://222.143.21.205:8081/?area=00390019']
        self.get_url(base_url[self.i])
        for i in self.th_list:
            i.join()
        self.workbook.close()


class NumberSum(object):
    def __init__(self):
        self.workbook = xlsxwriter.Workbook('D:\\{}.xlsx'.format(md + '政采显示数量'))
        self.sheet = self.workbook.add_worksheet('sheet')
        self.cell_format = self.workbook.add_format()
        self.cell_format.set_font_name('Arial Unicode MS')
        self.cell_format.set_font_size(10)
        self.sheet.write(0, 0, '一级分类', self.cell_format)
        self.sheet.write(0, 1, '二级分类', self.cell_format)
        self.sheet.write(0, 2, '总显示数', self.cell_format)
        self.sheet.write(0, 3, '郑州平氏上架数', self.cell_format)
        self.sheet.write(0, 4, '鹤壁平氏上架数', self.cell_format)
        self.count = 1


if __name__ == '__main__':
    for i in range(2):
        g_url = GetDetail(i)
        g_url.start()
