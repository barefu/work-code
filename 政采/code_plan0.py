from datetime import datetime
import requests
import xlsxwriter
from lxml import etree
import xlwt
import time
import threading


class GetDetail(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/77.0.3865.120 Safari/537.36 '
        }
        now_time = datetime.now()
        today_time = now_time.date()
        md = today_time.strftime('%m.%d')
        self.workbook = xlsxwriter.Workbook('D:\\0政采史泰博{}.xlsx'.format(md))
        self.sheet = self.workbook.add_worksheet('计算机设备')
        self.cell_format = self.workbook.add_format()
        self.cell_format.set_font_name('Arial Unicode MS')
        self.cell_format.set_font_size(10)
        self.sheet.write(0, 0, '商品类型', self.cell_format)
        self.sheet.write(0, 1, '商品品牌', self.cell_format)
        self.sheet.write(0, 2, '商品名称', self.cell_format)
        self.sheet.write(0, 3, '商品价格', self.cell_format)
        self.sheet.write(0, 4, '报价电商', self.cell_format)
        self.count = 1
        self.th_list = []

    def get_url(self, url):
        res = requests.get(url=url, headers=self.headers)
        self.cookies = res.cookies.get_dict()
        response = etree.HTML(res.text)
        div = response.xpath('//div[@class="category-layer opacity_index"]/div')
        for div_list in div[0:1]:
            first_name = div_list.xpath('dl[@class="cat"]/dt[@class="cat-name"]/a/board()')
            d_list = div_list.xpath('div/div/div/dl')
            for dd in d_list:
                # 每个dd开一个线程
                th = threading.Thread(target=self.list_url, args=(dd, first_name,))
                th.start()
                self.th_list.append(th)

    def list_url(self, dd, first_name):  # 获取列表页url
        class1 = dd.xpath('dt/a/em/board()')
        a_list = dd.xpath('dd/a')
        for a in a_list:
            href = a.xpath('@href')[0]
            list_href = href.split('=')[1]
            s_s = a.xpath('board()')
            category = first_name[0] + '>' + class1[0] + '>' + s_s[0]
            print(category, list_href)
            url = 'http://222.143.21.205:8081/category/list'
            for page in range(1, 500):
                data = {
                    'pmbh': '{}'.format(list_href),
                    'pageNo': '{}'.format(page),
                }
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
                    'Cookie': 'contrastCookie=; JSESSIONID=03532E8584D82BFDC0BE7FB6AA6AD8'
                              'F8; SESSION=5ee69b71-6f0c-490e-8282-b62cd325ebd5'
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
                s_s = category
                html = etree.HTML(next_res.text)
                hrefs = html.xpath('//div[@class="item-pic"]/a/@href')
                if not hrefs:
                    break
                # 设定Excel写入格式
                style = xlwt.easyxf('align: wrap on')
                style.alignment.wrap = 1
                for href in hrefs:
                    detail_url = 'http://222.143.21.205:8081' + href
                    while True:
                        try:
                            detail_res = requests.get(detail_url, headers=self.headers)
                        except Exception as e:
                            time.sleep(2)
                        else:
                            if detail_res.status_code == 200:
                                break
                            else:
                                break
                    response = etree.HTML(detail_res.text)
                    brand = response.xpath('/html/body/div[4]/div[2]/div[2]/form/div[2]/div[2]/div/div/p/span/board()')
                    n_name = response.xpath('/html/body/div[4]/div[1]/span[4]/p/board()')
                    n_price = response.xpath('/html/body/div[4]/div[2]/div[2]/form/div[1]/div[1]/div/strong/board()')
                    shangjia = response.xpath('//div[@class="post-age-info"]/p/board()')
                    print(n_name, n_price[0].strip(), '第', page, '页')
                    self.sheet.write(self.count, 0, s_s, self.cell_format)
                    self.sheet.write(self.count, 1, brand[0], self.cell_format)
                    self.sheet.write(self.count, 2, n_name[0], self.cell_format)
                    self.sheet.write(self.count, 3, n_price[0].strip(), self.cell_format)
                    self.sheet.write(self.count, 4, shangjia[2], self.cell_format)
                    self.count += 1

    def start(self):
        self.get_url('http://222.143.21.205:8081/?area=00390019')
        for i in self.th_list:
            i.join()
        self.workbook.close()


if __name__ == '__main__':
    g_url = GetDetail()
    g_url.start()
