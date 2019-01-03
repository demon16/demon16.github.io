

from selenium import webdriver

driver_path = "/home/simon/下载/chromedriver_linux64/chromedriver"


class Grabber:

    """Not a good idea."""

    def __init__(self, d, f, t, p):
        self.date = d
        self.from_ = f
        self.to = t
        self.purpose_code = p

        self.uuid = ''
        self.ticket = {}

        self.driver = webdriver.Chrome(executable_path=driver_path)

    def login(self):
        url = 'https://kyfw.12306.cn/otn/resources/login.html'
        self.driver.get(url)
        self.driver.implicitly_wait(10)


if __name__ == "__main__":
    g = Grabber('2019-01-15', 'SZQ', 'WHN', 'ADULT')
    g.login()
