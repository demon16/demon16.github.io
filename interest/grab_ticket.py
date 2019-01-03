from requests.cookies import RequestsCookieJar
from requests_html import HTMLSession
from PIL import Image
from io import BytesIO
import base64
import threading
import time
import urllib.parse
import re
import lxml.etree
import datetime as dt


sd = {
    'SZQ': '深圳',
    'WHN': '武汉',
}


class Grabber:
  
    def __init__(self, d, f, t, p):
        self.date = d
        self.from_ = f
        self.to = t
        self.purpose_code = p
        self.s = HTMLSession()
        self.s.cookies = self.init_cookie()
        self.uuid = ''
        self.ticket = {}

    def init_cookie(self):
        cookie_jar = RequestsCookieJar()
        cookie_jar.set("route", "c5c62a339e7744272a54643b3be5bf64", domain="/")
        cookie_jar.set("JSESSIONID", "772931B953A48C762D39F27832447D2F", domain="/otn")
        cookie_jar.set("BIGipServerotn", "217055754.38945.0000", domain="/")
        return cookie_jar

    def check_tickect_info(self):

        def crawl_ticket_info():
            url = (f'https://kyfw.12306.cn/otn/leftTicket/queryZ?'
                f'leftTicketDTO.train_date={self.date}'
                f'&leftTicketDTO.from_station={self.from_}'
                f'&leftTicketDTO.to_station={self.to}&purpose_codes={self.purpose_code}')
            r = self.s.get(url)
            tickets = []
            for line in r.json()['data']['result']:
                ls = line.split('|')
                if ls[0]:
                    tickets.append({
                        'secretstr': ls[0], 'train_num': ls[3],
                        'train_date': ls[13], 'start_at': ls[8], 'arrive_at': ls[9],
                        'seat_level_0': ls[32], 'seat_level_1': ls[31], 'seat_level_2': ls[30],
                        'sleeper_level_0': ls[21], 'sleeper_level_1': ls[23],
                        'motor_sleeper': ls[33], 'sleeper_level_2': ls[28],
                        'soft_seat': ls[27], 'hard_seat': ls[29], 'no_seat': ls[26]})
            return tickets

        tickets = crawl_ticket_info()
        if not tickets:
            return
        for ticket in tickets:
            if ticket['train_num'] == 'G1002':
                self.order_ticket(ticket)
                return

    def submit_order_request(self, ticket):
        url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        data = {
            'secretStr': urllib.parse.unquote(ticket['secretstr']),
            'train_date': dt.datetime.strptime(ticket['train_date'], '%Y%m%d').strftime('%Y-%m-%d'),
            'back_train_date': dt.datetime.today().strftime('%Y-%m-%d'),
            'tour_flag': 'dc',
            'purpose_codes': self.purpose_code,
            'query_from_station_name': sd[self.from_],
            'query_to_station_name': sd[self.to],
            'undefined': ''
        }
        r = self.s.post(url, data=data)

    def get_data(self):

        def parse_pts(html):
            tds = html.xpath('//tbody[@id="check_ticketInfo_id"]/tr/td')
            return f'0,0,1,{tds[3].text},1,{tds[5].text},{tds[6].text},N', f'{tds[3].text},1,{tds[5].text},1_'

        url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        headers = {
            'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc',
            'Host': 'kyfw.12306.cn',
            'Origin': 'https://kyfw.12306.cn',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = self.s.post(url, data={'_json_att': ''}, headers=headers)
        r.html.render(reload=False, wait=5)
        # print(r.text)
        # TODO: optimized
        html = lxml.etree.HTML(r.text)
        passenger_ticket_str, old_passenger_str = parse_pts(html)

        return {
            'REPEAT_SUBMIT_TOKEN': re.findall(r'var globalRepeatSubmitToken = \'(.*)\';', rt)[0],
            'key_check_isChange': re.findall(r'\'key_check_isChange\':\'(.*)\',', rt)[0],
            'leftTicketStr': re.findall(r'\'leftTicketStr\':\'(.*)\',', rt)[0],
            '_json_att': '',
            'dwAll': 'N',
            'roomType': '00',
            'whatsSelect': '1',
            'seatDetailType': '000',
            'choose_seats': '',# TODO: choose seat.
            'train_location': 'QX', # cant understand.
            'purpose_codes': '00',
            'randCode': '',
            'passengerTicketStr': passenger_ticket_str,
            'oldPassengerStr': old_passenger_str,
        }

    def order_ticket(self, ticket):
        self.submit_order_request(ticket)
        data = self.get_data()
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        r = self.s.post(url, data=data)
        try:
            if r.status_code == 200:
                print('got !')
        except:
            import traceback
            traceback.print_exc()

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
        rjs = self.s.post('https://kyfw.12306.cn/passport/web/checkqr',
                        data={'appid': 'otn', 'uuid': self.uuid}).json()
        return rjs['result_code'] != '2'

    def login(self):
        threading.Thread(target=self.show_qr_code).start()
        while self.check_qr_code():
            time.sleep(2)
        print('login success.')


if __name__ == "__main__":
    g = Grabber('2019-01-15', 'SZQ', 'WHN', 'ADULT')
    g.login()
    g.check_tickect_info()