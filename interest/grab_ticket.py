import requests
from requests.cookies import RequestsCookieJar
from PIL import Image
from io import BytesIO
import base64
import threading
import time


class Grabber:
  
    def __init__(self, d, f, t, p):
        self.date = d
        self.from_ = f
        self.to = t
        self.purpose_code = p

        self.s = requests.Session()
        self.s.cookies = self.init_cookie()
        self.uuid = ''
        self.ticket = {}

    def init_cookie(self):
        cookie_jar = RequestsCookieJar()
        cookie_jar.set("route", "495c805987d0f5c8c84b14f60212447d", domain="/")
        cookie_jar.set("JSESSIONID", "A01D810FE9FF47ED376A51996A47A9AE", domain="/otn")
        cookie_jar.set("BIGipServerotn", "468713994.24610.0000", domain="/")
        return cookie_jar

    def check_tickect_info(self):

        def crawl_ticket_info():
            url = (f'https://kyfw.12306.cn/otn/leftTicket/queryZ?'
                f'leftTicketDTO.train_date={self.d}'
                f'&leftTicketDTO.from_station={self.f}'
                f'&leftTicketDTO.to_station={self.t}&purpose_codes={self.p}')
            r = self.s.get(url)
            tickets = []
            for line in r.json()['data']['result']:
                ls = line.split('|')
                if ls[0]:
                    tickets.append({
                        'train_num': ls[3], 'date': ls[13], 'start_at': ls[8], 'arrive_at': ls[9],
                        'seat_level_0': ls[32], 'seat_level_1': ls[31], 'seat_level_2': ls[30],
                        'sleeper_level_0': ls[21], 'sleeper_level_1': ls[23],
                        'motor_sleeper': ls[33], 'sleeper_level_2': ls[28],
                        'soft_seat': ls[27], 'hard_seat': ls[29], 'no_seat': ls[26]})
            return tickets

        tickets = crawl_ticket_info()
        if not tickets:
            return
        for ticket in tickets:
            if ticket['train_num'] == 'G1010':
                print(ticket)
                # TODO: get the aim train_num for ordering.

    def show_qr_code(self):
        """Show qrcode for login."""
        url = 'https://kyfw.12306.cn/otn/resources/login.html'
        self.s.get(url)
        rjs = self.s.post('https://kyfw.12306.cn/passport/web/create-qr64', data={'appid': 'otn'}).json()
        self.uuid = rjs['uuid']
        b64img = rjs['image']
        img = Image.open(BytesIO(base64.b64decode(b64img)))
        img.show()

    def check_qr_code(self):
        print(self.s.post('https://kyfw.12306.cn/passport/web/checkqr', data={'appid': 'otn', 'uuid': self.uuid}).json())


    def login(self):
        threading.Thread(target=self.show_qr_code).start()
        while True:
            self.check_qr_code()
            time.sleep(2)
            # TODO: check the output.


if __name__ == "__main__":
    g = Grabber('2019-01-25', 'SZQ', 'WHN', 'ADULT')
    # g.check_tickect_info()
    g.login()