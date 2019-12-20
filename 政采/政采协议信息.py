import asyncio
import requests
import xlwt
from lxml import etree
from pyppeteer import launch


class CatxSpider(object):
    def __init__(self):
        self.workbook = xlwt.Workbook(encoding='utf-8')
        self.sheet = self.workbook.add_sheet('info', cell_overwrite_ok=True)
        self.sheet.write(0, 0, '商品类型')
        self.sheet.write(0, 1, '商品品牌')
        self.sheet.write(0, 2, '商品名称')
        self.sheet.write(0, 3, '协议价格')
        self.sheet.write(0, 4, '市场价格')
        self.sheet.write(0, 5, '配置参数')
        self.sheet.write(0, 6, '品牌联系人')
        self.sheet.write(0, 7, '供货商信息')
        self.count = 1

    def list_page(self, url):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/75.0.3770.100 Safari/537.36',
            'Cookie': '_zcy_log_client_uuid=c60d28e0-0a64-11ea-a251-cfc4592a6595; _dg_check.bbc15f7dfd2de351.63bf=-1; '
                      '_dg_playback.bbc15f7dfd2de351.63bf=1; user_type=0202; tenant_code=001000; '
                      'acw_tc=76b20fea15741241735293269e0540c1228f60963cd5d04f541a8c0921ab8f; aid=410102; '
                      'UM_distinctid=16e813a1156da-0b799f706ee1cc-51402e1a-1fa400-16e813a11572ab; '
                      'CNZZDATA1259303436=1017874749-1574123859-%7C1574134659; '
                      'SESSION=NWZkOGU1NDItNTVkZi00MjZjLWExNDktMDg1MTE5N2QwZjg0; wsid=3000184210#1574135444554; '
                      'uid=10007539810; districtCode=001000; '
                      'districtName=%E5%9B%BD%E5%AE%B6%E7%A8%8E%E5%8A%A1%E6%80%BB%E5%B1%80%E6%9C%AC%E7%BA%A7; '
                      '_dg_id.bbc15f7dfd2de351.63bf=77b9b47fb19858c5%7C%7C%7C1574123853%7C%7C%7C76%7C%7C%7C1574135583'
                      '%7C%7C%7C1574135583%7C%7C%7C%7C%7C%7Cc06c37dd8c9ce000%7C%7C%7C%7C%7C%7C%7C%7C%7C1%7C%7C'
                      '%7Cundefined',
            'Referer': '{}'.format(url)
        }
        list_res = requests.get(url, headers=self.headers)
        list_html = etree.HTML(list_res.text)
        a_list = list_html.xpath('//ul[@class="list_style"]/li/a/@href')
        for a in a_list:
            base = 'https://ctaxccgp.zcygov.cn'
            info_url = base + a + 'a0004.6e93fe6e.0.0.9a898d10ddac11e9b32547e0b2881f33'
            self.info_page(info_url)

    async def get_data(self, url):
        browser = await launch(headless=False)
        page = await browser.newPage()
        await page.setViewport({"width": 1366, "height": 768})
        await page.setExtraHTTPHeaders(self.headers)
        await page.goto(url)
        await asyncio.sleep(100)
        tr_list = await page.xpath('//tr[@data-supcode="410000"]')
        for tr in tr_list:
            td_text = await (await tr.getProperty('textContent')).jsonValue()
            print(td_text)
        # await page.screenshot(path="screen.png")
        await browser.close()

    def info_page(self, url):
        while True:
            try:
                info_res = requests.get(url, headers=self.headers)
            except Exception as e:
                print(e)
            else:
                if info_res.status_code == 200:
                    break
                else:
                    break
        info_html = etree.HTML(info_res.text)
        name = info_html.xpath('//div[@class="item-title"]/h1/board()')
        shichang_price = info_html.xpath('//span[@id="js-item-platform-price"]/board()')[0].strip()
        xieyi_price = info_html.xpath('//span[@id="js-item-price"]/board()')[0].strip()
        cate = info_html.xpath('//span[@class="total-sold"]/board()')
        brand = info_html.xpath('//ul[@class="spu-info clearfix"]/li[1]/board()')[0].split(':')[1].strip()
        parameters = info_html.xpath('//table[@class="attribute-tab"]')
        parameter_list = []
        for param in parameters[1:3]:
            trs = param.xpath('tbody/tr')
            for tr in trs:
                attr_cate = tr.xpath('td[1]/board()')
                attr_text = tr.xpath('td[2]/board()')
                attr = attr_cate[0].strip() + '：' + attr_text[0].strip()
                parameter_list.append(attr)
        parameter_list = '\r\n'.join(parameter_list)
        try:
            cate = cate[0].strip().split(' ')[1].strip()
        except Exception as e:
            print(e)
        brand_head = info_html.xpath('//table[@class="table"][1]/thead/tr/th/board()')
        brand_body = info_html.xpath('//table[@class="table"][1]/tbody/tr/td/board()')
        brand_contact = []
        for num in range(4):
            if len(brand_body) == 4:
                brand_start = brand_head[num + 8]
                brand_end = brand_body[num]
                brand_all = brand_start + '：' + brand_end
                brand_contact.append(brand_all)
            else:
                brand_start = brand_head[num + 8]
                brand_end = brand_body[num-4]
                brand_all = brand_start + '：' + brand_end
                brand_contact.append(brand_all)
        brand_contact = '\r\n'.join(brand_contact)
        company_thead = info_html.xpath('//table[@class="table L_supplierList"]/thead/tr/th/board()')
        company_tbody = info_html.xpath('//table[@class="table L_supplierList"]/tbody/tr[@data-supcode="410000"]')
        company_list = []
        # company_list1 = asyncio.get_event_loop().run_until_complete(self.get_data(url))
        for company_tr in company_tbody:
            company_ends = company_tr.xpath('td/board()')
            if len(company_ends) == 5:
                for num in range(5):
                    add_info = company_thead[num] + '：' + company_ends[num]
                    company_list.append(add_info)
                add_info = company_thead[5] + '：'
                company_list.append(add_info)
            elif len(company_ends) == 6:
                for num in range(5):
                    add_info = company_thead[num] + '：' + company_ends[num]
                    company_list.append(add_info)
                add_info = company_thead[5] + '：' + company_ends[5]
                company_list.append(add_info)
            else:
                pass
        company_list = '\r\n'.join(company_list)
        print(cate, brand, name, xieyi_price, shichang_price)
        self.sheet.write(self.count, 0, cate)
        self.sheet.write(self.count, 1, brand)
        self.sheet.write(self.count, 2, name)
        self.sheet.write(self.count, 3, xieyi_price)
        self.sheet.write(self.count, 4, shichang_price)
        self.sheet.write(self.count, 5, parameter_list)
        self.sheet.write(self.count, 6, brand_contact)
        self.sheet.write(self.count, 7, company_list)
        self.count += 1
        self.workbook.save('D:\\协议商品信息.xls')

    def work_on(self):
        for page in range(1, 27):
            base_url = 'https://ctaxccgp.zcygov.cn/search?pageSize=100&pageNo={}&showType=img&utm=a0004.4513c3a7.0.0.94841bb0ddac11e9a853c9825080c2b1'.format(str(page))
            self.list_page(base_url)


if __name__ == '__main__':
    catx = CatxSpider()
    catx.work_on()
