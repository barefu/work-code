import csv
import requests
import time
import xlwt
from lxml import etree

headers = {
            'Cookie': 'PHPSESSID=1qmgmmlj2ut6dsef9bae9q66tu',
            'User_Agent': "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
}
url = 'http://www.ping1go.com/home/product/detail/product_id/14920.html'
r = requests.get(url, headers=headers)
html = etree.HTML(r.text)
li = html.xpath('//ul[@class="img_x"]/li')
print(len(li))
