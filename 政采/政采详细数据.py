import requests
from lxml import etree
import xlwt, time


class GetDetail(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'
        }
        self.workbook = xlwt.Workbook(encoding='utf-8', style_compression=2)
        self.sheet = self.workbook.add_sheet('全部信息', cell_overwrite_ok=True)
        self.sheet.write(0, 0, '商品类型')
        self.sheet.write(0, 1, '商品品牌')
        self.sheet.write(0, 2, '商品名称')
        self.sheet.write(0, 3, '商品价格')
        self.sheet.write(0, 4, '商品红字')
        self.sheet.write(0, 5, '商品属性')
        self.count = 1

    def get_url(self, url):
        res = requests.get(url=url, headers=self.headers)
        response = etree.HTML(res.text)
        div = response.xpath('//div[@class="category-layer opacity_index"]/div')
        for div_list in div[3:4]:
            first_name = div_list.xpath('dl[@class="cat"]/dt[@class="cat-name"]/a/board()')
            d_list = div_list.xpath('div/div/div/dl')
            for dd in d_list:
                class1 = dd.xpath('dt/a/em/board()')
                a_list = dd.xpath('dd/a')
                for a in a_list:
                    href = a.xpath('@href')[0]
                    href = href.split('?')[1]
                    href = href.split('=')[1]
                    s_s = a.xpath('board()')
                    category =first_name[0] + '>' + class1[0] + '>' + s_s[0]
                    print(category)
                    self.list_url(href, category)

    def list_url(self, href, cate):  # 获取列表页url
        url = 'http://222.143.21.205:8081/category/list?pmbh=' + href
        for page in range(1, 200):
            data = {
                'pmbh': ''.format(href),
                'sort': '0',
                'pageNo': '{}'.format(str(page)),
            }
            while True:
                try:
                    next_res = requests.post(url=url, data=data, headers=self.headers, timeout=10)  # 获取下一个列表页
                except Exception as e:
                    print(e)
                    time.sleep(3)
                else:
                    if next_res.status_code == 200:
                        break
                    else:
                        break
            s_s = cate
            html = etree.HTML(next_res.text)
            hrefs = html.xpath('//div[@class="item-pic"]/a/@href')
            for href in hrefs:
                detail_url = 'http://222.143.21.205:8081' + href
                while True:
                    try:
                        detail_res = requests.get(detail_url, headers=self.headers)
                    except Exception as e:
                        time.sleep(2)
                    else:
                        if next_res.status_code == 200:
                            break
                        else:
                            break
                response = etree.HTML(detail_res.text)
                company_list = response.xpath(
                    '//*[@class="goods-detail-con goods-detail-tabs consh"]//tbody//span[@class="icon_ds"]/a/board()')
                price_list_all = response.xpath('//*[@id="content"]/table/tbody/tr/td[5]/board()')
                brand = response.xpath('/html/body/div[4]/div[2]/div[2]/form/div[2]/div[2]/div/div/p/span/board()')
                n_name = response.xpath('/html/body/div[4]/div[1]/span[4]/p/board()')
                n_price = response.xpath('/html/body/div[4]/div[2]/div[2]/form/div[1]/div[1]/div/strong/board()')
                red_words = response.xpath('//p[@class="goods-brief second-color"]/board()')
                print(brand, n_name, n_price)
                li_list = response.xpath('//div[@class="Ptable"]/div/ul/li')
                attr_list = []
                for li in li_list:
                    attr_cate = li.xpath('span/board()')
                    attr_text = li.xpath('em/board()')
                    attr = attr_cate[0].strip() + '：' + attr_text[0].strip()
                    attr_list.append(attr)
                parameter = '\r\n'.join(attr_list)
                self.sheet.write(self.count, 0, s_s)
                self.sheet.write(self.count, 1, brand)
                self.sheet.write(self.count, 2, n_name)
                self.sheet.write(self.count, 3, n_price)
                self.sheet.write(self.count, 4, red_words)
                try:
                    style = xlwt.easyxf('align: wrap on')
                    style.alignment.wrap = 1
                    self.sheet.write(self.count, 5, parameter, style)
                except Exception as e:
                    print(e)
                self.count += 1
            self.workbook.save('D:\\政采详细数据家具.xls')

    def start(self):
        self.get_url('http://222.143.21.205:8081/index')

if __name__ == '__main__':
    g_url = GetDetail()
    g_url.start()