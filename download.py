import requests
from urllib import request
from lxml import etree
#from selenium import webdriver
import selenium.webdriver.chrome as  webdriver
#import selenium.webdriver.firefox as  webdriver
import platform
import os
import time


headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36',
        'Host': 'music.163.com',
        'Referer': 'https://music.163.com/'
    }


def get_url(url):
    """从歌单中获取歌曲链接"""

    req = requests.get(url, headers=headers)

    root = etree.HTML(req.text)
    items = root.xpath('//ul[@class="f-hide"]//a')
    print(items)

    return items


def download_song(song_id, song_name):
    """通过外链下载歌曲"""

    url = 'https://music.163.com/song/media/outer/url?id={}.mp3'.format(song_id)

    req = requests.get(url, headers=headers, allow_redirects=False)
    song_url = req.headers['Location']
    print(req.status_code,url,song_url)
    if("mp3" not in song_url):
        return "NotFound"
    try:
        #request.urlretrieve(song_url, path + "/" + song_name + ".mp3")
        name=path + "/" + song_name + ".mp3"
        os.system("wget {} -O {} ".format(url,name))
        os.system("ffplay \"{}\"".format(name))
        correct=input("是否下载正确Y/N")
        if(correct == "N"):
            os.unlink()
            return "NotCorrect"
        print("{}--下载完成".format(song_name))
    except:
        print("{}--下载失败".format(song_name))


def download(items):
    """全部歌曲下载"""
    ret=None
    for item in items:
        song_id = item.get('href').strip('/song?id=')
        song_name = item.text
        ret=download_song(song_id, song_name)
    print("－－－－－－－下载完成－－－－－－－")


def artist_id_down(id):
    """根据歌手id下载全部歌曲"""

    artist_url = 'https://music.163.com/artist?id={}'.format(id)

    items = get_url(artist_url)
    download(items)


def playlist_id_down(id):
    """根据歌单id下载全部歌曲"""
    playlist_url = 'https://music.163.com/playlist?id={}'.format(id)

    items = get_url(playlist_url)
    download(items)


def get_song_name(url):
    """在歌曲页面获得名字"""

    req = requests.get(url, headers=headers)

    root = etree.HTML(req.text)
    name = root.xpath('//em[@class="f-ff2"]/text()')

    return name[0]


def song_id_down(id):
    """根据歌曲id下载"""

    url = 'https://music.163.com/song?id={}'.format(id)

    name = get_song_name(url)
    ret=download_song(id, name)
    if(ret==None):
        return True
    else:
        return False

class WebDriver():
    @classmethod
    def Instance(cls, *args, **kwargs):
        if not hasattr(WebDriver, "_instance"):
            WebDriver._instance = WebDriver(*args, **kwargs)
        return WebDriver._instance
    def releaseInstance():
        if hasattr(WebDriver, "_instance"):
            del WebDriver._instance 
        
    def __init__(self):
        options = webdriver.options.Options()
        options.add_argument(
            'User-Agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"')
        options.add_argument('--headless')
        self.driver = webdriver.webdriver.WebDriver(options=options)
    def __del__(self):
        #self.driver.close()
        self.driver.quit()



def selenium_get_html(url):
    """通过selenium获得页面源码"""

    try:
        driver=WebDriver.Instance().driver
        driver.get(url)
        driver.switch_to.frame('contentFrame')
        ret=driver.page_source
    except Exception as e:
           print(e) 
           ret=None
    return ret


def search_input_song(url):
    """获取歌曲名字和id"""

    html=None
    while(html == None):
        html = selenium_get_html(url)

    root = etree.HTML(html)
    id = root.xpath('//div[@class="srchsongst"]//div[@class="td w0"]//div[@class="text"]/a[1]/@href')
    artist = root.xpath('//div[@class="srchsongst"]//div[@class="td w1"]//div[@class="text"]/a[1]/text()')
    name = root.xpath('//div[@class="srchsongst"]//div[@class="td w0"]//div[@class="text"]//b/@title')

    id = [i.strip('/song?id==') for i in id]
    return zip(name, artist, id)


def search_input_artist(url):
    """获取歌手id"""

    html = selenium_get_html(url)

    root = etree.HTML(html)
    id = root.xpath('//div[@class="u-cover u-cover-5"]/a[1]/@href')

    return id[0].strip('/artist?id==')


def search_input_playlist(url):
    """获取歌单名字和id"""

    html = selenium_get_html(url)

    root = etree.HTML(html)
    id = root.xpath('//div[@class="u-cover u-cover-3"]/a/@href')
    name = root.xpath('//div[@class="u-cover u-cover-3"]//span/@title')

    id = [i.strip('/playlist?id==') for i in id]
    return zip(name, id)


def main(name, choose_id):
    if choose_id == 1:
        url = 'https://music.163.com/#/search/m/?s={}&type=1'.format(name)
        com = search_input_song(url)
        ids = []
        for i, j, k in com:
            ids.append(k)
            print("歌曲名称:{0}-------演唱者:{1}-------id: {2}".format(i, j, k))
        while True:
            id = input("请输入需要下载的id(输入q退出):")
            if id == 'q':
                return
            if id in ids:
                ret=song_id_down(id)
                if(ret):
                    return
            print("请输入正确的id!!!")
    elif choose_id == 2:
        url = 'https://music.163.com/#/search/m/?s={}&type=100'.format(name)
        id = search_input_artist(url)
        artist_id_down(id)
    elif choose_id == 3:
        url = 'https://music.163.com/#/search/m/?s={}&type=1000'.format(name)
        com = search_input_playlist(url)
        ids = []
        for i, j in com:
            ids.append(j)
            print("歌单名称:{0}-------id:{1}".format(i, j))
        while True:
            id = input("请输入需要下载的id(输入q退出):")
            if id == 'q':
                return
            if id in ids:
                playlist_id_down(id)
                return
            print("请输入正确的id(输入q退出):")


def recognition():
    """判断系统,执行清屏命令"""
    sysstr = platform.system()
    if (sysstr == "Windows"):
        os.system('cls')
    elif (sysstr == "Linux"):
        os.system('clear')


if __name__ == '__main__':
    path = "./download"#input("请输入完整路径地址:")
    if not os.path.exists(path):
        os.makedirs(path)
    while True:
        print("=========================")
        print("请按提示选择搜索类型:")
        print("1.歌曲")
        print("2.歌手")
        print("3.歌单")
        print("4.退出")
        print("=========================")
        choose_id = int(input("搜索类型:"))
        if choose_id == 4:
            WebDriver.releaseInstance()
            break
        elif choose_id != 1 and choose_id != 2 and choose_id != 3:
            print("请按要求输入!!!")
            continue
        else:
            recognition()
            name = input("请输入搜索内容:")
            main(name, choose_id)

