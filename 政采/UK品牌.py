from datetime import datetime
import requests
import xlsxwriter
from lxml import etree
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
        self.workbook = xlsxwriter.Workbook('D:\\UK品牌.xlsx'.format(md))
        self.sheet_all = self.workbook.add_worksheet('all of data')
        self.cell_format = self.workbook.add_format()
        self.cell_format.set_font_name('Arial Unicode MS')
        self.cell_format.set_font_size(10)
        self.sheet_all.write(0, 0, '商品类型', self.cell_format)
        self.sheet_all.write(0, 1, '商品品牌', self.cell_format)
        self.sheet_all.write(0, 2, '商品名称', self.cell_format)
        self.sheet_all.write(0, 3, '详情页链接', self.cell_format)
        self.sheet_all.write(0, 4, '商品价格', self.cell_format)
        self.sheet_all.write(0, 5, '供应商', self.cell_format)
        self.count_all = 1
        self.th_list = []

    def deal_data(self):
        pass

    def get_url(self, url):
        res = requests.get(url=url, headers=self.headers)
        response = etree.HTML(res.text)
        div = response.xpath('//div[@class="category-layer opacity_index"]/div')
        brand_nums = ['6f2494397c0043e4bdf3d7e4d5ef7937', 'dfe05ab7e1a64477b8e9d0d524e59b9d',
                     '24a0db059c2d44f8bf8de108909f3ce0', 'ff80808151cc41bc0151cd159edb714a',
                     '40282a3e177c9ede01177caf22800036', '3733211c95724662a0ba8a58227da16e',
                     '8026b9fcf54548f7a6ae65a730e9ee9f', 'd179e87b36e14188bb8c3a68c44a8312',
                     '2ce496b65db443138192ca3fe740e1e4', '979be297d94544ae9842eee073078989',
                     'ff8080815bc397b2015bcd2f7fd8545d', 'd7e15b3bb1414a4a8cc08d50337784c9',
                     'ff8080815c04a864015c0a099c495d60', 'ff8080815d88af95015d9b8456db19c3',
                     'a47e50889aa944c19b1198e03148436f', '9c8b1fd1862d4838a2e96ee8929c9b80',
                     '817f9ba72dfc4380bfbd75a74a443605', '2612c4e330734af4a95876006e042a1e',
                     'a2dd277a11f346998350666d4795c316', '1a3c0ee5b43940a086b3a82a9c66513a',
                     'c6b24d6818f94bdb959e5064d76f2f59', '3679d13c0d42483e8981297785aa05d5',
                      'dd57edf7d95743d194727d062d2e9db6', 'eb561806c198470c9a02a309366ceb16',
                      'd2ad69474ac24629aeb2c465f78c70db', '45c393ee7d534e56b505414b234ec49b',
                      '9e94aad5c63e4a9b93524f0260f212b4', 'f5298fd0e302433ba935665131aed3cc',
                       '0e9cee3c41a2438cbf8df44355a575f0']
        brand_names = ['碧涞', '幸福森林', '益而高', '鸿合 HITEVISION', '旅之星', '金创伟', '创显',
                      '清大视讯QDTECH', '全朗', '荣事达', '豫鼎鑫', '育隆', '荣青', '华燕天成', '海天地',
                      '思进', '欧帝', '特固', '酷比客', 'GXIN', 'ARRIVEtext', 'FITOUCH', 'MINDHUB', '杰必喜', '肯辛通',
                       'JIUFANG 9', 'SHD', '南翼', '正浩仪器']
        # brand_nums = ['cb1f73ebfc6b4ee393dda21a015a2286', 'f81044b3ce984f5190ce39d11e589573',
        #               'edbb24dc2850460e977c37bfec2b0252', 'ff8080815a6f779c015a7e9e10fc796d',
        #               'ff8080815b5b4827015b5c4ea3044078', 'ff8080814a0ac42f014a0eb26e713217',
        #               'ff808081604a584601604a6ad4bd00e4', '']
        # brand_names = ['史密斯 A.O.SMITH', '高宝 COBOL', 'AOC', '乐歌', '凯龙达', '影源', 'maxhub']

        for i in range(len(brand_names)):
            brand_name = brand_names[i]
            print(brand_name)
            self.num = brand_nums[i]
            self.sheet = self.workbook.add_worksheet('{}'.format(brand_name))
            self.sheet.write(0, 0, '商品类型', self.cell_format)
            self.sheet.write(0, 1, '商品品牌', self.cell_format)
            self.sheet.write(0, 2, '商品名称', self.cell_format)
            self.sheet.write(0, 3, '详情页链接', self.cell_format)
            self.sheet.write(0, 4, '商品价格', self.cell_format)
            self.sheet.write(0, 5, '供应商', self.cell_format)
            self.count = 1
            for div_list in div:
                first_name = div_list.xpath('dl[@class="cat"]/dt[@class="cat-name"]/a/text()')
                d_list = div_list.xpath('div/div/div/dl')
                for dd in d_list:
                    # 每个dd开一个线程
                    th = threading.Thread(target=self.list_url, args=(dd, first_name, brand_name))
                    th.start()
                    self.th_list.append(th)
            for thing in self.th_list:
                thing.join()
        self.workbook.close()

    def list_url(self, dd, first_name, brand_name):  # 获取列表页url
        class1 = dd.xpath('dt/a/em/text()')
        a_list = dd.xpath('dd/a')
        for a in a_list:
            href = a.xpath('@href')[0]
            list_href = href.split('=')[1]
            s_s = a.xpath('text()')
            category = first_name[0] + '>' + class1[0] + '>' + s_s[0].strip()
            url = 'http://222.143.21.205:8081/category/list'
            for page in range(1, 500):
                data = {
                    'pmbh': '{}'.format(list_href),
                    'ppbh': '{}'.format(self.num),
                    'pageNo': '{}'.format(page),
                }
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
                    'Cookie': 'contrastCookie=; SESSION=c565d123-75f9-4f35-b710-cc625fb4e35d'
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
                a_s = html.xpath('//div[@class="item-name"]/a')
                prices = html.xpath('//div[@class="item-price"]/em/text()')
                companys = html.xpath('//div[@class="item-company "]/em/text()')
                if not a_s:
                    break
                # 设定Excel写入格式
                for num in range(len(a_s)):
                    company = companys[num]
                    href = a_s[num].xpath('@href')[0]
                    name = a_s[num].xpath('@title')
                    price = prices[num]
                    price = price.split('￥')
                    detail_url = 'http://222.143.21.205:8081' + href
                    self.sheet.write(self.count, 0, s_s, self.cell_format)
                    self.sheet.write(self.count, 1, brand_name, self.cell_format)
                    self.sheet.write(self.count, 2, name[0], self.cell_format)
                    self.sheet.write(self.count, 3, detail_url, self.cell_format)
                    self.sheet.write(self.count, 4, price[1], self.cell_format)
                    self.sheet.write(self.count, 5, company, self.cell_format)
                    self.count += 1
                    self.sheet_all.write(self.count_all, 0, s_s, self.cell_format)
                    self.sheet_all.write(self.count_all, 1, brand_name, self.cell_format)
                    self.sheet_all.write(self.count_all, 2, name[0], self.cell_format)
                    self.sheet_all.write(self.count_all, 3, detail_url, self.cell_format)
                    self.sheet_all.write(self.count_all, 4, price[1], self.cell_format)
                    self.sheet_all.write(self.count_all, 5, company, self.cell_format)
                    self.count_all += 1

    def start(self):
        self.get_url('http://222.143.21.205:8081/?area=00390019')


if __name__ == '__main__':
    g_url = GetDetail()
    g_url.start()
