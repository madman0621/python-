# 只能够本地安装了webdriver才能够运行
from selenium import webdriver
browser = webdriver.Chrome(executable_path='./chromedriver')
# browser.get('https://www.baidu.com')

# browser.quit()
