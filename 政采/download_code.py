import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
}
url = 'http://222.143.21.205:8081/policy/saleArticleList?code=w7wc'
base_url = 'http://222.143.21.205:8081/captcha-image'
res = requests.get(base_url, headers=headers)
path = '123.jpg'
with open(path, "wb")as f:
    f.write(res.content)
    f.close()
    print("文件保存成功！")
