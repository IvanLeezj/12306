import pickle
import time
import random
import requests
import re
from lxml import etree

from PIL import Image
from io import BytesIO

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

import smtplib
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from chaojiying import Chaojiying_Client

from utils.setting_models.setting_class import setting, variable, USER_AGENTS



class MonestFunctionSeleniumSpider(object):

    def __init__(self):
        self.lourl = setting.login_url
        self.driver_path = setting.driver_path
        self.username = setting.username
        self.password = setting.password
        self.c_type = setting.cat_type[variable.ctype]

        # 反检查设置
        self.chrome_options = Options()
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_argument('user-agent={}'.format(random.choice(USER_AGENTS)))

        self.driver = webdriver.Chrome(executable_path=self.driver_path, options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 15, 0.3)
        self.driver.maximize_window()

    def getztid(self):
        """
        获取城市站台对应ID代号
        :return: dict
        """
        try:
            f = open('utils/citytilss/city.txt', encoding='utf-8')
            line = json.loads(re.sub(r"'", '"', f.readlines()[0]))
            city_id_dict = line
        except:
            url = "https://www.12306.cn/index/script/core/common/station_name_v10113.js"
            response = requests.get(url=url).text
            # print(response)
            find_city = re.findall(r'@.*?\|(.*?)\|', response)
            print(find_city)
            find_city_id = re.findall(r'@.*?\|.*?\|(.*?)\|', response)
            print(find_city_id)

            city_id_dict = dict(zip(find_city, find_city_id))
            print(city_id_dict)
            with open('utils/citytilss/city.txt', 'w', encoding='utf-8') as f:
                f.write(str(city_id_dict))

        return city_id_dict


    def getinfo1(self, response):
        html = etree.HTML(response)
        global content
        piaoinfo1 = html.xpath('//div[@id="check_ticket_tit_id"]')
        for page in piaoinfo1:
            date = page.xpath('./strong[1]/text()')[0]
            checi = page.xpath('./strong[2]/text()')[0] + '次'
            qishizhan = page.xpath('./strong[3]/text()')[0] + '站'
            mudidi = page.xpath('./strong[4]/text()')[0] + re.sub(r'\s','', html.xpath('//div[@id="check_ticket_tit_id"]//text()')[-1])
            content = [date, checi, qishizhan+mudidi]
        return '  '.join(content)

    def getinfo2(self, response):
        html = etree.HTML(response)
        piaoinfo2 = html.xpath('//div[@class="table-list-body"]//text()')
        # piaoinfo2 = ['\n', '\n\t', '1', '\n    \n\t\t\t\t\n\t\t\t\t  \t', '\n                  \n                   二等座', '\n\t\t\t\t\n\t\t\t\n\t', '成人票', '\n\t', '李子健', '\n\t', ' 中国居民身份证 ', '\n\t', '4420***********018', '\n\t', '131****0007', '\n', '\n', '\n', '\n']
        content1 = []
        a = re.sub(r'\s', '', piaoinfo2[4])
        b = piaoinfo2[6]
        c = piaoinfo2[8]
        d = piaoinfo2[10]
        e = piaoinfo2[12]
        f = piaoinfo2[14]
        content1.append([a, b, c, d, e, f])
        return ' '.join(content1[0]), content1[0][2]


    def getclickxpath(self, html):
        click_xpath = '//*[@id="t-list"]/table/tbody/tr[contains(@id, "ticket_")][{}]/td[last()]'
        start_time_list = []
        tr_list = html.xpath('//*[@id="t-list"]/table/tbody/tr[contains(@id, "ticket_")]')
        print('共查询到{}从{}到{}的列车共有{}次：'.format(variable.date, variable.cfc, variable.ddc, len(tr_list)))
        i = 0
        for tr in tr_list:
            i += 1
            start_time = tr.xpath('./td[1]/div[1]/div[3]/strong[1]/text()')[0]
            stop_time = tr.xpath('./td[1]/div[1]/div[3]/strong[2]/text()')[0]
            checi = tr.xpath('./td[1]/div[1]/div[1]/div[1]/a/text()')[0]
            if variable.ctype == "高铁":
                try:
                    shangwu = tr.xpath('./td[2]/div/text()')[0]  # 商务座
                except IndexError as e:
                    shangwu = tr.xpath('./td[2]/text()')[0]
                try:
                    yideng = tr.xpath('./td[3]/div/text()')[0]  # 一等座
                except IndexError as e:
                    yideng = tr.xpath('./td[3]/text()')[0]
                try:
                    erdengs = tr.xpath('./td[4]/div/text()')[0]  # 二等座
                except IndexError as e:
                    erdengs = tr.xpath('./td[4]/text()')[0]
                if variable.time == start_time:
                    start_time_list.append(click_xpath.format(i))
                    if variable.zwtype == "二等座":
                        zuowei = erdengs
                    if variable.zwtype == "一等座":
                        zuowei = yideng
                    if variable.zwtype == "商务座":
                        zuowei = shangwu
                print(variable.cfc, '到', variable.ddc, checi, start_time + '——' + stop_time,
                      '商务座:', shangwu, '一等座:', yideng, '二等座:', erdengs)
            else:
                try:
                    ruanwo = tr.xpath('./td[6]/div/text()')[0]  # 软卧
                except IndexError as e:
                    ruanwo = tr.xpath('./td[6]/text()')[0]
                try:
                    yingwo = tr.xpath('./td[8]/div/text()')[0]  # 硬卧
                except IndexError as e:
                    yingwo = tr.xpath('./td[8]/text()')[0]
                try:
                    ruanzuo = tr.xpath('./td[9]/div/text()')[0]  # 软座
                except IndexError as e:
                    ruanzuo = tr.xpath('./td[9]/text()')[0]
                try:
                    yingzuo = tr.xpath('./td[10]/div/text()')[0]  # 硬座
                except IndexError as e:
                    yingzuo = tr.xpath('./td[10]/text()')[0]
                if variable.time == start_time:
                    start_time_list.append(click_xpath.format(i))
                    if variable.zwtype == "软卧":
                        zuowei = ruanwo
                    if variable.zwtype == "硬卧":
                        zuowei = yingwo
                    if variable.zwtype == "软座":
                        zuowei = ruanzuo
                    if variable.zwtype == "硬座":
                        zuowei = yingzuo
                print(variable.cfc, '到', variable.ddc, checi, start_time + '——' + stop_time,
                      '软卧:', ruanwo, '硬卧:', yingwo, '软座:', ruanzuo, '硬座:', yingzuo)
        if len(start_time_list) < 1:
            return False
        else:
            return [start_time_list[0], zuowei]


    def login1(self):
        time.sleep(1)
        print("正在登录12306平台 请稍后...")
        self.wait.until(EC.visibility_of_element_located((By.LINK_TEXT, '账号登录'))).click()
        time.sleep(0.5)
        self.wait.until(EC.visibility_of_element_located((By.ID, 'J-userName'))).send_keys(self.username)
        self.wait.until(EC.visibility_of_element_located((By.ID, 'J-password'))).send_keys(self.password)

        while True:
            try:
                code_img_ele = self.driver.find_element_by_id('J-loginImgArea')
                code_img = code_img_ele.screenshot_as_png

                chaojiying = Chaojiying_Client('ivan97', 'ivan1997', '915344')  # 用户中心>>软件ID 生成一个替换 96001
                result = chaojiying.PostPic(code_img, 9004)['pic_str']  # 1902 验证码类型  官方网站>>价格体系 3.4+版 print 后要加()
                print("点选图片坐标点：", result)
                result_list = result.split('|')
                for li in result_list:
                    tmp = li.split(',')
                    x = int(tmp[0])
                    y = int(tmp[1])
                    ActionChains(self.driver).move_to_element_with_offset(code_img_ele, x, y).click().perform()
                    time.sleep(0.2)

                self.driver.find_element_by_xpath('//*[@id="J-login"]').click()
                time.sleep(2)
                print("正在进行滑块验证 请稍后...")
                slip_btn = self.driver.find_element_by_xpath('//*[@id="nc_1_n1z"]')
                ActionChains(self.driver).drag_and_drop_by_offset(slip_btn, 300, 0).perform()
                break
            except:
                print("点选图片验证或滑块验证未通过 正在进行重试验证...")
                self.driver.close()
                time.sleep(1)
        return True


    def login2(self):
        self.driver.get(self.lourl)
        time.sleep(2)
        print("正在登录12306平台 请稍后...")
        self.wait.until(EC.visibility_of_element_located((By.LINK_TEXT, '账号登录'))).click()
        time.sleep(0.5)
        self.wait.until(EC.visibility_of_element_located((By.ID, 'J-userName'))).send_keys(self.username)
        self.wait.until(EC.visibility_of_element_located((By.ID, 'J-password'))).send_keys(self.password)

        while True:
            try:
                code_img_ele = self.driver.find_element_by_id('J-loginImgArea')
                code_img = code_img_ele.screenshot_as_png

                chaojiying = Chaojiying_Client('ivan97', 'ivan1997', '915344')  # 用户中心>>软件ID 生成一个替换 96001
                result = chaojiying.PostPic(code_img, 9004)['pic_str']  # 1902 验证码类型  官方网站>>价格体系 3.4+版 print 后要加()
                print("点选图片坐标点：", result)
                result_list = result.split('|')
                for li in result_list:
                    tmp = li.split(',')
                    x = int(tmp[0])
                    y = int(tmp[1])
                    ActionChains(self.driver).move_to_element_with_offset(code_img_ele, x, y).click().perform()
                    time.sleep(0.2)

                self.driver.find_element_by_xpath('//*[@id="J-login"]').click()
                time.sleep(2)
                print("正在进行滑块验证 请稍后...")
                slip_btn = self.driver.find_element_by_xpath('//*[@id="nc_1_n1z"]')
                ActionChains(self.driver).drag_and_drop_by_offset(slip_btn, 300, 0).perform()

                # 保存cookie
                time.sleep(2)
                cookies = self.driver.get_cookies()
                pickle.dump(cookies, open("cookied/{}_cookie".format(setting.username), 'wb'))

                cookie_dict = {}

                for cookie in cookies:
                    cookie_dict[cookie["name"]] = cookie["value"]
                print(cookie_dict)
                break
            except:
                print("点选图片验证或滑块验证未通过 正在进行重试验证...")
                self.driver.close()
                time.sleep(1)

        print("点选图片验证及滑块验证已通过，程序将为您查询车票信息，请稍后... ")
        return True

    def email(self,file_path):
        smtpserver = 'smtp.163.com'
        # 发送邮箱用户名密码
        users = 'lzjname19971@163.com'
        password = 'VUPOOTWKWOVCODKL'
        # 发送和接收邮箱
        receives = ['lzjname1997@163.com', users]

        msg = MIMEMultipart()  # 创建一个带附件的实例
        subject = Header('您的12306购票信息', 'utf-8').encode()
        msg["Subject"] = subject  # 指定邮件主题
        msg["From"] = users  # 邮件发送人l
        msg["To"] = ','.join(receives)
        msg.attach(MIMEText('购票二维码,请查收!本次订单在30分钟内有效，请注意付款时间！', _subtype='html', _charset='utf-8'))

        try:
            part = MIMEApplication(open(file_path, 'rb').read())
            part.add_header('Content-Disposition', 'attachment', filename=file_path)
            msg.attach(part)

            s = smtplib.SMTP(smtpserver, timeout=30)  # 连接smtp邮件服务器,端口默认是25
            s.login(users, password)  # 登陆服务器
            s.sendmail(users, receives, msg.as_string())  # 发送邮件
            s.close()
            print('------->邮件发送成功', '已发送购票二维码！')
            print('------->success')
        except Exception as e:
            print("------->send email error:" + str(e))
            print('------->错误', '请检查邮箱地址是否正确！并重新查询后再次发送邮件。')


    def search_city(self):
        city_id_dict = self.getztid()
        self.search_url = setting.search_url.format(
            variable.cfc, city_id_dict[variable.cfc],
            variable.ddc, city_id_dict[variable.ddc], variable.date)
        self.driver.get(self.search_url)
        time.sleep(1)
        if "网络可能存在问题，请您重试一下！" in self.driver.page_source:
            self.driver.close()
        if self.c_type == '高铁':
            self.wait.until(EC.visibility_of_element_located((
                By.XPATH, '//*[@id="_ul_station_train_code"]/li[1]/input'))).click()  # 勾选高铁/城际选项
            self.wait.until(EC.visibility_of_element_located((
                By.XPATH, '//*[@id="_ul_station_train_code"]/li[2]/input'))).click()  # 勾选动车选项
            self.wait.until(EC.visibility_of_element_located((By.ID, 't-list')))
            time.sleep(0.1)
        else:
            time.sleep(0.2)
            self.wait.until(EC.visibility_of_element_located((
                By.XPATH, '//*[@id="_ul_station_train_code"]/li[3]/input'))).click()
            self.wait.until(EC.visibility_of_element_located((
                By.XPATH, '//*[@id="_ul_station_train_code"]/li[4]/input'))).click()
            self.wait.until(EC.visibility_of_element_located((By.ID, 't-list')))
            self.wait.until(EC.visibility_of_element_located((
                By.XPATH, '//*[@id="_ul_station_train_code"]/li[5]/input'))).click()
            self.wait.until(EC.visibility_of_element_located((
                By.XPATH, '//*[@id="_ul_station_train_code"]/li[6]/input'))).click()
            self.wait.until(EC.visibility_of_element_located((By.ID, 't-list')))
            time.sleep(0.1)

        html = etree.HTML(self.driver.page_source)
        click_xpath = self.getclickxpath(html)  # 返回符合时间的车票抢票按钮和符合座位的信息
        if not click_xpath:  # 没有找到对应车票
            bgs.append('1')
            print(
                "本次查询从【{}】到【{}】【{}】出发的车次无票，正在进行第【{}】次查询...".format(variable.cfc, variable.ddc, variable.time, len(bgs)))
            print('-' * 75)
            if len(bgs) % 30 == 0:
                time.sleep(12)
            self.search_city()  # 重新调用函数继续查询是否有余票

        if click_xpath[1] == '无':  # 车票无票
            bg.append('0')
            print("本次查询从【{}】到【{}】 【{}】出发的车次{}无票，正在进行第【{}】次查询...".format(variable.cfc, variable.ddc, variable.time,
                                                                        variable.zwtype, len(bg)))
            print('-' * 75)
            if len(bg) % 30 == 0:
                time.sleep(12)
            self.search_city()
        print("------->恭喜，有票了！！！！正在为您抢票请稍后...")
        self.driver.find_element_by_xpath(click_xpath[0]).click()  # 点击购票、预定

        if setting.ts_info not in self.driver.page_source:
            print('------->已登录，正在提交订单信息。')
            print("------->恭喜，抢到票了！！！！正在为您购票请稍后...")
            try:
                self.driver.find_element_by_id('normalPassenger_0').click()
                self.driver.find_element_by_id('submitOrder_id').click()
            except:
                self.wait.until(EC.presence_of_element_located((By.ID, 'normalPassenger_0'))).click()
                self.wait.until(EC.presence_of_element_located((By.ID, 'submitOrder_id'))).click()
            time.sleep(3)
            resposne = self.driver.page_source
            piaoinfo1 = self.getinfo1(response=resposne)
            piaoinfo2, name = self.getinfo2(response=resposne)
            print("------->本次购票信息: ", piaoinfo1)
            print("------->本次购票信息: ", piaoinfo2)
            try:
                self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '确认'))).click()
            except:
                self.search_city()
            time.sleep(5)
            print("------->正在提交信息请稍后...")
            play = self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '网上支付')))
            self.driver.execute_script("arguments[0].click();", play)
            time.sleep(2)
            print("------->订单已提交，请稍后...")
            self.driver.switch_to.window(self.driver.window_handles[1])
            time.sleep(2)
            self.wait.until(EC.presence_of_element_located((
                By.XPATH, '/html/body/div[2]/div[2]/div/form/div[9]/div/img'))).click()
            time.sleep(1)
            print("------->正在生成二维码，请稍后...")
            pay_img_ele = self.wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "#J_qrPayArea > div:nth-child(1) > div:nth-child(3) > div:nth-child(2) > "
                                 "canvas")))
            img = pay_img_ele.screenshot_as_png
            img = Image.open(BytesIO(img))
            file_path = 'pro_function/images/pay.png'
            img.save(file_path)
            self.email(file_path)
            print("已为您完成抢票！程序将自动关闭。")
            self.driver.close()

        else:
            if self.login1():    # 重新在本页面登陆
                print("------->恭喜，抢到票了！！！！正在为您购票请稍后...")
                try:
                    self.driver.find_element_by_id('normalPassenger_0').click()
                    self.driver.find_element_by_id('submitOrder_id').click()
                except:
                    self.wait.until(EC.presence_of_element_located((By.ID, 'normalPassenger_0'))).click()
                    self.wait.until(EC.presence_of_element_located((By.ID, 'submitOrder_id'))).click()
                time.sleep(1)
                resposne = self.driver.page_source
                piaoinfo1 = self.getinfo1(response=resposne)
                piaoinfo2, name = self.getinfo2(response=resposne)
                print("------->本次购票信息: ", piaoinfo1)
                print("------->本次购票信息: ", piaoinfo2)
                time.sleep(2)
                try:
                    self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '确认'))).click()
                except:
                    self.search_city()
                time.sleep(5)
                print("------->正在提交信息请稍后...")
                play = self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, '网上支付')))
                self.driver.execute_script("arguments[0].click();", play)  # 执行js进行点击
                time.sleep(2)
                print("------->订单已提交，请稍后...")
                self.driver.switch_to.window(self.driver.window_handles[1])
                time.sleep(2)
                self.wait.until(EC.presence_of_element_located((
                    By.XPATH, '/html/body/div[2]/div[2]/div/form/div[9]/div/img'))).click()
                time.sleep(1)
                print("------->正在生成二维码，请稍后...")
                pay_img_ele = self.wait.until(EC.presence_of_element_located((
                    By.CSS_SELECTOR, "#J_qrPayArea > div:nth-child(1) > div:nth-child(3) > div:nth-child(2) > "
                                     "canvas")))
                img = pay_img_ele.screenshot_as_png
                img = Image.open(BytesIO(img))
                file_path = 'pro_function/image/pay.png'
                img.save(file_path)
                self.email(file_path)
                print("已为您完成抢票！程序将自动关闭。")
                self.driver.close()



    def requests_function_login(self):
        if self.login2():
            cookies = pickle.load(open("cookied/{}_cookie".format(setting.username), 'rb'))
            cookie_dict = {}
            for cookie in cookies:
                cookie_dict[cookie["name"]] = cookie["value"]
            self.driver.close()
            return cookie_dict
        else:
            self.login2()  # 重新执行本函数登录

