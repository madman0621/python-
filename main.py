import json
import random
import time
from datetime import datetime, timedelta, timezone, tzinfo
import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 获取基础配置 注意更新cookie和token
with open("./config/index.json", "r", encoding='utf-8') as file:
    config = json.load(file)
    userConfig = config['userInfo']
    weChatConfig = config['weChatInfo']

headers = {
    "Cookie": userConfig['cookie'],
    "User-Agent": userConfig['userAgent']
}


def log(*msg):
    print(datetime.now(tz=timezone(timedelta(hours=8))).strftime(
        '%Y-%m-%d %H:%M:%S'), *msg)

# 通过query关键字查询公众号信息


def findWeChatInfo(query):
    search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?'
    # 搜索微信公众号接口需要传入的参数，有三个变量：微信公众号token、随机数random、搜索的微信公众号名字
    params = {
        'action': 'search_biz',
        'token': userConfig['token'],
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
        'random': random.random(),
        'query': query,
        'begin': '0',
        'count': '5'
    }
    # 打开搜索微信公众号接口地址，需要传入相关参数信息如：cookies、params、headers
    search_response = requests.get(
        search_url,  headers=headers, params=params)
    # log('search_response:', search_response.json())
    # 取搜索结果中的第一个公众号
    info = search_response.json().get('list')[0]
    return info


# 通过关键字list获取一系列的公众号信息
def findAllWeChatInfo(queryList):
    result = []
    for query in queryList:
        queryInfo = findWeChatInfo(query)
        result.append(
            {"name": queryInfo['nickname'], "fakeid": queryInfo['fakeid']})
    print(result)


# 获取该公众号全部文章
def getAllWeChatArticle(info):
    if 'name' not in info or 'fakeid' not in info:
        print('需要设置公众号名称name以及fakeid')
        return

    # 1、循环抓取全部公众号文章
    # 请求链接
    url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
    begin = 0
    articles = []
    lastTime = info.get('lastTime', 0)

    # 获取请求缓存
    cacheFilePath = './cache/getAllWeChatArticle_%s.json' % (info['name'])
    if os.path.exists(cacheFilePath) and os.path.getsize(cacheFilePath):
        with open(cacheFilePath, "r", encoding='utf-8') as dataFile:
            cacheData = json.load(dataFile)
            begin = cacheData['begin']
            articles = cacheData['articles']

    while True:
        params = {
            "action": "list_ex",
            "begin": begin,  # 不同页，此参数变化，变化规则为每页加5
            "count": 5,
            "fakeid": info['fakeid'],
            "type": "9",
            "token": userConfig['token'],
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1"
        }
        resp = requests.get(url, headers=headers,
                            params=params, verify=False).json()
        # log('resp:', resp)
        num = resp['app_msg_cnt']
        articleList = resp['app_msg_list']
        begin += len(articleList)
        log('当前抓取进度：', info['name'], ' ', begin, '/', num)

        for articleItem in articleList:
            articles.append({
                "aid": articleItem['aid'],
                "appmsgid": articleItem['appmsgid'],
                "title": articleItem['title'],
                "link": articleItem['link'],
                "create_time": articleItem['create_time'],
                "update_time": articleItem['update_time'],
            })
        if (begin >= num):
            break
        # 每次查询间隔一段时间，防止账号被封
        time.sleep(5)

    if not len(articles):
        print('无文章获取')
        return

    # 2、将查询的全部文章data-json进行保存data/artilces/公众号名称.json中
    jsonFilePath = './data/articles/%s.json' % (info['name'])
    with open(jsonFilePath, 'w+', encoding='utf-8') as dataFile:
        json.dump(articles, dataFile, indent=2)

    # 3、根据全部文章data-json生成对应的md文件
    # 格式：2023-02-22 14:14:33  [通过 React Router V6 源码，掌握前端路由](http://mp.weixin.qq.com/s?)
    mdText = ''
    for articleItem in articles:
        createTime = datetime.fromtimestamp(
            articleItem['create_time'], tz=timezone(timedelta(hours=8)))
        mdText += '%s [%s](%s)  \n' % (createTime.strftime('%Y-%m-%d %H:%M:%S'),
                                       articleItem['title'], articleItem['link'])
    mdFilePath = './dist/articles/%s.md' % (info['name'])
    with open(mdFilePath, 'w+', encoding='utf-8') as mdFile:
        mdFile.write(mdText)


# 获取所有公众号的到指定日期间的新增文章
def getLastWeChatArticle(info):
    # info = {'name': '抖音前端技术团队', 'fakeid': 'Mzg3MDY2NTEyNg=='}

    # 1、获取本地公众号信息中最新一篇文章创建时间
    jsonFilePath = './data/articles/%s.json' % (info['name'])
    if os.path.exists(jsonFilePath) and os.path.getsize(jsonFilePath):
        with open(jsonFilePath, "r", encoding='utf-8') as dataFile:
            oldDataJson = json.load(dataFile)
            lastTime = oldDataJson[0]['create_time']
    else:
        oldDataJson = []
        lastTime = info.get('lastTime', 0)

    # 请求链接
    url = "https://mp.weixin.qq.com/cgi-bin/appmsg"
    num = 1
    begin = 0
    articles = []
    timeData = {}

    # 获取请求缓存
    cacheFilePath = './cache/getLastWeChatArticle_%s.json' % (info['name'])
    if os.path.exists(cacheFilePath) and os.path.getsize(cacheFilePath):
        with open(cacheFilePath, "r", encoding='utf-8') as dataFile:
            cacheData = json.load(dataFile)
            begin = cacheData['begin']
            articles = cacheData['articles']
            num = cacheData['num']

    while True:
        params = {
            "action": "list_ex",
            "begin": begin,  # 不同页，此参数变化，变化规则为每页加5
            "count": 5,
            "fakeid": info['fakeid'],
            "type": "9",
            "token": userConfig['token'],
            "lang": "zh_CN",
            "f": "json",
            "ajax": "1"
        }
        resp = requests.get(url, headers=headers,
                            params=params, verify=False).json()
        # log("resp:", resp)
        if ("app_msg_list" not in resp or len(resp['app_msg_list']) == 0) and begin < num:
            log("请求失败,记录缓存:", resp)
            cacheData = {"begin": begin, "articles": articles, "num": num}
            with open(cacheFilePath, 'w+', encoding='utf-8') as dataFile:
                json.dump(cacheData, dataFile, indent=2)
            return

        num = resp['app_msg_cnt']
        begin += 5
        log('当前抓取进度：', info['name'], ' ', begin, '/', num)
        # log("app_msg_list:", resp['app_msg_list'])
        isBreak = False
        for articleItem in resp['app_msg_list']:
            if articleItem['create_time'] <= lastTime:
                isBreak = True
                break
            # if (len(articles)):
            #     lastCreateTime = articles[-1]['create_time']
            #     if (articleItem['create_time'] > lastCreateTime):
            #         continue
            articles.append({
                "aid": articleItem['aid'],
                "appmsgid": articleItem['appmsgid'],
                "from": info['name'],
                "title": articleItem['title'],
                "link": articleItem['link'],
                "create_time": articleItem['create_time'],
                "update_time": articleItem['update_time'],
            })
        if isBreak:
            break
        if (begin >= num):
            break
        # 每次查询间隔一段时间，放置账号被封
        time.sleep(5)
    if os.path.exists(cacheFilePath):
        os.remove(cacheFilePath)

    if not len(articles):
        print('无新增文章')
        return

    # 2、更新公众号json本地数据
    with open(jsonFilePath, 'w+', encoding='utf-8') as dataFile:
        json.dump(articles+oldDataJson, dataFile, indent=2)

    # 3、更新公众号md内容以及初始化时间线数据
    mdText = ''
    for articleItem in articles:
        # 拼接mdText文案
        createTime = datetime.fromtimestamp(
            articleItem['create_time'], tz=timezone(timedelta(hours=8)))
        mdText += '%s [%s](%s)  \n' % (createTime.strftime('%Y-%m-%d %H:%M:%S'),
                                       articleItem['title'], articleItem['link'])
        # 设置每日日报数据对象
        strYear = str(createTime.year)
        indexMonth = createTime.month
        indexDay = createTime.day

        yearData = []
        if strYear not in timeData:
            yearDataFile = './data/time/%s.json' % strYear
            if os.path.exists(yearDataFile) and os.path.getsize(yearDataFile):
                with open(yearDataFile, "r", encoding='utf-8') as dataFile:
                    yearData = json.load(dataFile)
            if len(yearData) < 12:
                yearData.extend(list() for i in range(12-len(yearData)))

            timeData[strYear] = yearData
        else:
            yearData = timeData[strYear]

        monthData = yearData[indexMonth-1]
        if len(monthData) < 31:
            monthData.extend(list() for i in range(31-len(monthData)))
        monthData[indexDay-1].append(articleItem)

    # 设置公众号md内容
    mdFilePath = './dist/articles/%s.md' % (info['name'])
    oldFileText = ''
    if os.path.exists(mdFilePath) and os.path.getsize(mdFilePath):
        with open(mdFilePath, 'r', encoding='utf-8') as mdFile:
            oldFileText = mdFile.read()
    with open(mdFilePath, 'w+', encoding='utf-8') as mdFile:
        mdFile.seek(0, 0)
        mdFile.write(mdText)
        mdFile.write(oldFileText)

    # 4、更新本地时间线json数据及md文件内容
    for yearName, yearData in timeData.items():
        jsonFilePath = './data/time/%s.json' % yearName
        with open(jsonFilePath, 'w+', encoding='utf-8') as dataFile:
            json.dump(yearData, dataFile, indent=2)

        mdText = ''
        yearData.reverse()
        for indexMonth, monthData in enumerate(yearData):
            monthData.reverse()

            monthText = ''
            for indexDay, dayData in enumerate(monthData):
                dayData.reverse()

                dayText = ''
                if len(dayData) == 0:
                    continue
                for item in dayData:
                    createTime = datetime.fromtimestamp(
                        item['create_time'], tz=timezone(timedelta(hours=8)))

                    if dayText == '':
                        dayText += '### %s  \n' % (
                            createTime.strftime('%Y-%m-%d'))
                    dayText += '%s %s [%s](%s)  \n' % (item['from'], createTime.strftime(
                        '%Y-%m-%d %H:%M:%S'), item['title'], item['link'])

                if monthText == '' and dayText != '':
                    monthText += '## %i月  \n' % (12-indexMonth)
                monthText += dayText

            if monthText != '':
                mdText += monthText

        mdFilePath = './dist/time/%s.md' % yearName
        with open(mdFilePath, 'w+', encoding='utf-8') as mdFile:
            mdFile.write(mdText)


if __name__ == '__main__':
    try:
        print('开始抓取数据。。。')
        # findWeChatInfo('字节前端')
        # findAllWeChatInfo(['阿里巴巴终端技术', '支付宝体验科技', '前端之神', '前端新世界', '前端开发爱好者', '前端早读课', '字节前端 ByteFE',
        #                   '大淘宝技术', '前端之巅', 'InfoQ', 'Oasis 引擎爱好者', '前端试炼', '大淘宝前端技术', '前端真好玩', '前端大全'])
        # getAllWeChatArticle({'name': '抖音前端技术团队', 'fakeid': 'Mzg3MDY2NTEyNg=='})
        # getAllWeChatArticle({"name": "支付宝体验科技", "fakeid": "Mzg2OTYyODU0NQ=="})
        # getAllWeChatArticle(
        #     {"name": "字节前端 ByteFE", "fakeid": "Mzg2ODQ1OTExOA=="})
        # getLastWeChatArticle(
        #     {"name": "前端早读课","fakeid": "MjM5MTA1MjAxMQ=="})
        # for infoItem in weChatConfig:
        #     getLastWeChatArticle(infoItem)
        print('数据抓取完成')
    except Exception as e:
        log('error:', str(e))
