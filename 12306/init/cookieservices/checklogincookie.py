import requests
import pickle
import random

from utils.setting_models.setting_class import setting, USER_AGENTS
from pro_function.ticket_models import MonestFunctionSeleniumSpider

class CookieSVClient(object):

    def __init__(self):
        self.cookie_file = "cookied/{}_cookie".format(setting.username)


    def checkcookie(self):
        """
        cookie服务
        :return:
        """
        try:
            cookies = pickle.load(open(self.cookie_file, 'rb'))
            print('本地cookies加载成功', cookies, '\n', '-' * 25+'cookies输出完成'+'-' * 25)
            cookie_dict = {}
            for cookie in cookies:
                cookie_dict[cookie["name"]] = cookie["value"]
        except:
            print('本地cookies加载失败')
            print('正在重新登陆')
            model = MonestFunctionSeleniumSpider()
            cookie_dict = model.requests_function_login()
        return cookie_dict

    def checklogin(self, cookies):
        """
        验证cookies是否登录
        :param cookies:
        :return:
        """
        print("[init-cookieservices-checklogincookie.py]-[checklogin]-本地cookie：", cookies)
        url = 'https://kyfw.12306.cn/otn/index/initMy12306Api'
        url1 = 'https://kyfw.12306.cn/otn/modifyUser/initQueryUserInfoApi'
        url2 = 'https://kyfw.12306.cn/otn/passengers/query'
        data2 = {
            'pageIndex': '1',
            'pageSize': '10'
        }
        headers = {}
        headers['User-Agent'] = random.choice(USER_AGENTS)
        response = requests.post(url, cookies=cookies, headers=headers).text
        response1 = requests.post(url1, cookies=cookies, headers=headers).text
        response2 = requests.post(url2, cookies=cookies, data=data2, headers=headers).text
        if '_validatorMessage' in response and '_validatorMessage' in response1 and '_validatorMessage' in response2:
            print(response, '\n', '-' * 25+'response输出完成'+'-' * 25)
            print(response1, '\n', '-' * 25+'response输出完成'+'-' * 25)
            print(response2, '\n', '-' * 25+'response输出完成'+'-' * 25)
            print("本地登录验证成功")
            return True
        else:
            print('本地登录验证失败')
            return False

    def run(self):
        cookies = self.checkcookie()
        if self.checklogin(cookies=cookies):        # 验证cookies是否登录有效
            pass
        else:                                       # 失效 重新登录获取cookies
            print("正在调用本地登录服务")
            model = MonestFunctionSeleniumSpider()
            cookie_dict = model.requests_function_login()
            self.run()
