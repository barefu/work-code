import re
import time
import requests
from lxml import etree
import xlwt
from datetime import datetime, timedelta
from 政采.chaojiying import *
now_time = datetime.now()
today_time = now_time.date()
yesterday = today_time + timedelta(days=-1)


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
        self.sheet.write(0, 7, '品牌')
        self.sheet.write(0, 8, '数量')
        self.sheet.write(0, 9, '单价')
        self.sheet.write(0, 10, '总价')
        self.count = 1

    def captcha(self):
        base_url = 'http://222.143.21.205:8081/captcha-image'
        while True:
            try:
                res = requests.get(base_url, headers=self.headers)
            except Exception as e:
                print(e)
                time.sleep(3)
            else:
                if res.status_code == 200:
                    break
                else:
                    break
        path = '123.jpg'
        with open(path, "wb")as f:
            f.write(res.content)
            f.close()
        chaojiying = Chaojiying_Client()
        im = open('123.jpg', 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
        self.captcha_json = chaojiying.PostPic(im, 1902)
        captcha = self.captcha_json['pic_str']
        with open('D:\\captcha-img\\{}.jpg'.format(captcha), "wb")as f:
            f.write(res.content)
            f.close()
        return captcha

    def page_data(self):
        for page in range(1, 33):
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
                list_time = tr.xpath('td[6]/text()')[0]
                s_time = str(list_time).strip().split(' ')[0]
                if str(s_time) == str(yesterday):
                    # captcha = self.captcha()
                    detail_url = 'http://222.143.21.205:8081/policy/articleDetail?id=' + p + '&deep_learn_code={}'.format(captcha)
                    while True:
                        try:
                            detail_res = requests.get(url=detail_url, headers=self.headers)
                            detail_html = etree.HTML(detail_res.text)
                            title = detail_html.xpath('//h2[@class="title"]/text()')
                        except Exception as e:
                            print(e)
                            time.sleep(3)
                        else:
                            if title:
                                break
                            # else:
                            #     chaojiying = Chaojiying_Client()
                            #     chaojiying.ReportError(self.captcha_json['pic_id'])
                            #     print(self.captcha_json['pic_str'], '*******************************************************************************')
                    title = detail_html.xpath('//h2[@class="title"]/text()')
                    cai_gou = detail_html.xpath('//div[@class="annoucement"]/ul/li[1]/em/text()')
                    gong_ying = detail_html.xpath('//div[@class="annoucement"]/ul/li[2]/em/text()')
                    shi_jian = detail_html.xpath('//div[@class="annoucement"]/ul/li[3]/em/text()')
                    bian_hao = detail_html.xpath('//div[@class="annoucement"]/ul/li[4]/em/text()')
                    trs = detail_html.xpath('//table[@class="layui-table"]/tbody/tr')
                    print(shi_jian, place)
                    for tr in trs[0:-1]:
                        name = tr.xpath('td[2]/span/text()')
                        p_name = tr.xpath('td[3]/span/text()')
                        num = tr.xpath('td[4]/span/text()')
                        price = tr.xpath('td[5]/span/text()')
                        total_price = tr.xpath('td[7]/span/text()')
                        self.sheet.write(self.count, 0, place)
                        self.sheet.write(self.count, 1, title)
                        self.sheet.write(self.count, 2, cai_gou)
                        self.sheet.write(self.count, 3, gong_ying)
                        self.sheet.write(self.count, 4, shi_jian)
                        self.sheet.write(self.count, 5, bian_hao)
                        self.sheet.write(self.count, 6, name)
                        self.sheet.write(self.count, 7, p_name)
                        self.sheet.write(self.count, 8, num)
                        self.sheet.write(self.count, 9, price)
                        self.sheet.write(self.count, 10, total_price)
                        self.count += 1
                else:
                    break
            self.workbook.save(str(yesterday) + '成交公告.xls')


if __name__ == '__main__':
    cj = CJ_data()
    cj.page_data()
