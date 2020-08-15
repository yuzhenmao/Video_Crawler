import requests
from bs4 import BeautifulSoup
import time
import re
import heapq
from urllib.parse import urlparse
import sys
import json
from contextlib import closing
from pyquery import PyQuery as pq
from requests import RequestException

PATTERN = '((ftp|http|https):\/\/)?'
count = 0


def Crawler(url, heap, result):
    
    parsed = urlparse(url)    
    base = f"{parsed.scheme}://{parsed.netloc}"

    try:
        req_obj = requests.get(url)
    except BaseException:
        return
    
    bresp = BeautifulSoup(req_obj.text,"html.parser")  
    a = bresp.find_all('a')
    a = filter(lambda a: a.has_attr('href'), a)	

    for item in a:             
        url = item['href']
        parsed = urlparse(url)    
        if not parsed.netloc:
            url = base + url
        elif not parsed.scheme:
            url = "http:" + url
        url_sub = re.sub(PATTERN, '', url).strip().strip('/#')
        if (("video" in url) and (url_sub not in result)):
            global count
            count = count + 1
            heapq.heappush(heap, (count,url))
            result.add(url_sub)

    return


def crawl():
# 'result' stores all the unduplicated websites (no http etc.) the crawler has met before
# 'heap' stores all the unduplicated websites the crawler needs to access in the future
# 'output' stores all the unduplicated websites the crawler has accessed alre

    l = []
    url = "https://www.bilibili.com/video/BV1P54y1R7hB?from=search&seid=10954872432932590672"
    url_sub = re.sub(PATTERN, '', url).strip().strip('/#')
    result = set()
    heap = []
    output = list()
    result.add(url_sub)
    
    while len(output) < 50:   
        Crawler(url, heap, result)
        output.append(url)
        print(url)
        l.append(url)
        try:
            i, url = heapq.heappop(heap)
        except BaseException:
            print("No more URL!")

    print(len(result))

    return l
   
l = crawl()
urls=[]
for url in l:
    if "/video/" in url:
        urls.append(url)

class bilibili():
    def __init__(self):
        self.getHtmlHeaders={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q = 0.9'
        }

        self.downloadVideoHeaders={
            'Origin': 'https://www.bilibili.com',
            'Referer': 'https://www.bilibili.com/video/av26522634',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        }

    def getHtml(self,url):
        try:
            response = requests.get(url=url, headers= self.getHtmlHeaders)
#             print(response.status_code)
            if response.status_code == 200:
                return response.text
        except RequestException:
            print('Request Html Error:')

    def parseHtml(self,html):
        doc = pq(html)
        video_title = doc('#viewbox_report > h1 > span').text()
        
        pattern = r'\<script\>window\.__playinfo__=(.*?)\</script\>'
        result = re.findall(pattern, html)[0]
        temp = json.loads(result)
        #video_url = temp['durl']
        if temp['data']['timelength']>=300000:
            return 0
        if 'durl' in temp['data'].keys():
            for item in temp['data']['durl']:
                if 'url' in item.keys():
                    video_url = item['url']
        else:
            for item in temp['data']['dash']['video']:
                if 'baseUrl' in item.keys():
                    video_url = item['baseUrl']
        #print(video_url)
        return{
            'title': video_title,
            'url': video_url
        }

    def download_video(self,video):
        title = re.sub(r'[\/:*?"<>|]', '-', video['title']) 
        url = video['url']
        filename = title +'.flv'
        with open(filename, "wb") as f:
            f.write(requests.get(url=url, headers=self.downloadVideoHeaders, stream=True, verify=False).content)

        # with closing(requests.get(video['url'], headers=self.downloadVideoHeaders, stream=True, verify=False)) as res:
        #     if res.status_code == 200:
        #         with open(filename, "wb") as f:
        #             for chunk in res.iter_content(chunk_size=1024):
        #                 if chunk:
        #                     f.write(chunk)

    def run(self,url):
        if self.parseHtml(self.getHtml(url)) ==0:
            return
        self.download_video(self.parseHtml(self.getHtml(url)))


for url in urls:
    bilibili().run(url)
    print(url)    
    
    
