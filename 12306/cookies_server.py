import time
from init.cookieservices.checklogincookie import CookieSVClient

def cookieSVC():
    while True:
        try:
            f = open('init/cookie_bgs/cookiezt.txt', encoding='utf-8')
            line = f.readlines()[0].replace('\n', '')
            print(line)
            if line == 'False':
                print('-' * 25, '本地cookiezt.txt加载成功', '-' * 25)
                csvc = CookieSVClient()
                csvc.run()
                time.sleep(30)
            if line == 'True':
                with open('init/cookie_bgs/cookiezt.txt', 'w') as f:
                    f.write('False\n')
                    f.close()
                break
        except:
            print('-' * 25, '本地cookiezt.txt加载成功', '-' * 25)
            csvc = CookieSVClient()
            csvc.run()
            time.sleep(30)


if __name__ == '__main__':
    cookieSVC()