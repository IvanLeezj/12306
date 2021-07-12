import time

from pro_function.ticket_models import MonestFunctionSeleniumSpider


if __name__ == '__main__':
    """
    使用selenium进行抢购
    """
    model = MonestFunctionSeleniumSpider()
    model.login2()
    time.sleep(3)
    model.search_city()