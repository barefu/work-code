from datetime import datetime
import time
import pandas as pd
import requests
import xlwt
import xlsxwriter
from lxml import etree
import threading


now_time = datetime.now()
today_time = now_time.date()
md = today_time.strftime('%m.%d')


class BrandSpider(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/77.0.3865.120 Safari/537.36 '
        }
        self.workbook = xlwt.Workbook(encoding='utf-8')
        self.sheet = self.workbook.add_sheet('sheet')
        self.sheet.write(0, 0, '商品类型')
        self.sheet.write(0, 1, '商品品牌')
        self.sheet.write(0, 2, '商品名称')
        self.sheet.write(0, 3, '商品价格')
        self.count = 1
        self.name = '缺失品牌'
        self.th_list = []

    def read_data(self):
        all_data = pd.read_excel('D:\\{}.xlsx'.format(self.name))
        if all_data.size != 0:
            groups = all_data.groupby(['分组依据'])
            for group in groups:
                th = threading.Thread(target=self.group_write, args=(group,))
                th.start()
                self.th_list.append(th)

    def group_write(self, group):
            for row in group[1].T.iteritems():
                url = row[1][2]
                # 从url进入回去这个商品分组的品牌
                while True:
                    try:
                        detail_res = requests.get(url, headers=self.headers)
                    except Exception as e:
                        print(e)
                        time.sleep(2)
                    else:
                        if detail_res.status_code == 200:
                            break
                        else:
                            break
                response = etree.HTML(detail_res.text)
                brand = response.xpath('/html/body/div[4]/div[2]/div[2]/form/div[2]/div[2]/div/div/p/span/board()')
                self.sheet.write(self.count, 0, row[1][0])
                self.sheet.write(self.count, 1, brand)
                self.sheet.write(self.count, 2, row[1][1])
                self.sheet.write(self.count, 3, row[1][3])
                self.count += 1
                print('第{}行写入成功！'.format(self.count))
            self.workbook.save('D:\\{}政采品牌信息.xls'.format(md))

    def main(self):
        self.read_data()
        for i in self.th_list:
            i.join()


if __name__ == '__main__':
    brandspider = BrandSpider()
    brandspider.read_data()
