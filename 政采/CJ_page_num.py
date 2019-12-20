import re

import requests, time
from lxml import etree
import xlwt
from datetime import datetime
from bs4 import BeautifulSoup
from 政采.chaojiying import Chaojiying_Client


now_time = datetime.now()
today_time = now_time.date()


class CJ_data(object):
    def __init__(self):
        self.baseurl = 'http://222.143.21.205:8081/policy/saleArticleList?code='
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
        }
        self.workbook = xlwt.Workbook(encoding='utf-8')
        self.sheet = self.workbook.add_sheet('成交结果')
        self.sheet.write(0, 0, '地区')
        self.sheet.write(0, 1, '项目名称')
        self.sheet.write(0, 2, '采购方')
        self.sheet.write(0, 3, '供应商')
        self.sheet.write(0, 4, '时间')
        self.sheet.write(0, 5, '项目编号')
        self.sheet.write(0, 6, '货物名称')
        self.sheet.write(0, 7, '品类')
        self.sheet.write(0, 8, '品牌')
        self.sheet.write(0, 9, '数量')
        self.sheet.write(0, 10, '单价')
        self.sheet.write(0, 11, '总价')
        self.count = 1

    def page_data(self):
        for page in range(1, 1000):
            data = {
                'pageNo': '{}'.format(page)
            }
            while True:
                base_url = 'http://222.143.21.205:8081/captcha-image'
                while True:
                    try:
                        res_img = requests.get(base_url, headers=self.headers)
                    except Exception as e:
                        print(e)
                        time.sleep(3)
                    else:
                        if res_img.status_code == 200:
                            break
                        else:
                            break
                path = '123.jpg'
                with open(path, "wb") as f:
                    f.write(res_img.content)
                    f.close()
                chaojiying = Chaojiying_Client()
                im = open('123.jpg', 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
                self.captcha_json = chaojiying.PostPic(im, 1902)
                captcha = self.captcha_json['pic_str']
                url = self.baseurl + captcha
                try:
                    res = requests.post(url=url, headers=self.headers, data=data)  # 获取下一个列表页
                except Exception as e:
                    print(e)
                    time.sleep(3)
                else:
                    response = etree.HTML(res.text)
                    table = response.xpath('//table[@class="layui-table clinch_success"]/tbody/tr')
                    if len(table) > 10:
                        with open('D:\\captcha-img\\{}.jpg'.format(captcha), "wb")as f:
                            f.write(res_img.content)
                            f.close()
                        break
                    else:
                        with open('D:\\captcha-error-img\\{}.jpg'.format(captcha), "wb")as f:
                            f.write(res_img.content)
                            f.close()
                        chaojiying = Chaojiying_Client()
                        chaojiying.ReportError(self.captcha_json['pic_id'])
                        print(captcha,
                              '*******************************************************************************')
            for tr in table[1:]:
                href = tr.xpath('td[7]/a/@onclick')[0]
                patt = "'(.*)'"
                p = re.findall(patt, href)[0]
                place = tr.xpath('td[5]/text()')[0]
                detail_url = 'http://222.143.21.205:8081/policy/articleDetail?id=' + p + '&deep_learn_code={}'.format(captcha)
                while True:
                    try:
                        detail_res = requests.get(url=detail_url, headers=self.headers, timeout=20)  # 获取下一个列表页
                    except Exception as e:
                        time.sleep(1)
                    else:
                        if detail_res.status_code == 200:
                            break
                        else:
                            time.sleep(1)
                bs = BeautifulSoup(detail_res.content, 'lxml')
                title = bs.select('div.nes_details h2')[0].text
                xin_xi = bs.select('div.annoucement ul li em')
                cai_gou = xin_xi[0].text
                gong_ying = xin_xi[1].text
                shi_jian = xin_xi[2].text
                bian_hao = xin_xi[3].text
                xx = bs.find_all('tr')
                for td in xx[1:-1]:
                    xq = td.find_all('td')
                    name = xq[1].get_text()
                    p_name = xq[2].get_text()
                    category = p_name.split('/')[:-1]
                    logo = p_name.split('/')[-1]
                    num = xq[3].get_text()
                    price = xq[4].get_text()
                    total_price = xq[6].get_text()
                    print(shi_jian)
                    self.sheet.write(self.count, 0, place)
                    self.sheet.write(self.count, 1, title)
                    self.sheet.write(self.count, 2, cai_gou)
                    self.sheet.write(self.count, 3, gong_ying)
                    self.sheet.write(self.count, 4, shi_jian)
                    self.sheet.write(self.count, 5, bian_hao)
                    self.sheet.write(self.count, 6, name)
                    self.sheet.write(self.count, 7, category)
                    self.sheet.write(self.count, 8, logo)
                    self.sheet.write(self.count, 9, num)
                    self.sheet.write(self.count, 10, price)
                    self.sheet.write(self.count, 11, total_price)
                    self.count += 1
            self.workbook.save('月、周成交公告.xls')


if __name__ == '__main__':
    cj = CJ_data()
    cj.page_data()