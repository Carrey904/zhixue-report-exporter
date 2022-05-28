from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sys import path
from os import system
import requests
from random import random


LOGIN_URL = "https://www.zhixue.com/login.html"
V_URL = 'https://www.zhixue.com/login/forgetpwd/getImageCode' # 验证码网址
V_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
  'Referer': 'https://www.zhixue.com/login.html',
}
SAVE_DIR = path[0] + '\\vcode.jpeg'
USERNAME = "zxt2225106" # 用户名
PASSWORD = "mitotti425" # 密码
param_parser = lambda url:{msg.split('=')[0]:msg.split('=')[1] for msg in url.split("?")[-1].split('&')}
vparams_generater = lambda uuid:{'token': str(random()), 'uuid': uuid}


browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10) # 设置等待 10s 超时
browser.get(LOGIN_URL) # 载入登录界面
uid_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtUserName"]'))) # 用户名输入框
pwd_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtPassword"]'))) # 密码输入框
v_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtImageCode"]'))) # 验证码输入框
v_img = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="imageCode"]'))) # 验证码<img>
login_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="signup_button"]'))) # 登录按钮
v_params = vparams_generater(param_parser(v_img.get_attribute('src'))['uuid'])
v_cookies = {msg['name']:msg['value'] for msg in browser.get_cookies()}
v_pic_data = requests.get(V_URL, headers=V_HEADERS, cookies=v_cookies).content
with open(SAVE_DIR, 'wb') as f:
    f.write(v_pic_data)
system(SAVE_DIR)
v_input.send_keys(input("[INPUT] 输入验证码\n"))
uid_input.send_keys(USERNAME)
pwd_input.send_keys(PASSWORD)
login_button.click()
t = input()
