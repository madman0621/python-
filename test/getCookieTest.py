
# 方法1:使用 selenium 进行模拟登录
# # 只能够本地安装了webdriver才能够运行
# from selenium import webdriver
# import time
# browser = webdriver.Chrome(executable_path='./chromedriver')

# browser.get('https://mp.weixin.qq.com/')
# time.sleep(20)
# # 获取当前网页链接
# url = browser.current_url
# cookies = browser.get_cookies()
# for item in cookies:
#     print('item:',item)
# print('url:',url)


# 方法2:使用browser_cookie3库
# import browser_cookie3
# import requests
# # firefox可以替换为browser_cookie3.firefox()
# cookies = browser_cookie3.chrome(domain_name='mp.weixin.qq.com')
# print('cookies:', cookies)
# # response = requests.get(url, cookies=cookies)
