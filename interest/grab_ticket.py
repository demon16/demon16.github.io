import requests


class Grabber:
  
    def __init__(self, d, f, t, p):
        self.date = d
        self.from_ = f
        self.to = t
        self.purpose_code = p
        self.query_url = (f'https://kyfw.12306.cn/otn/leftTicket/queryZ?'
                          f'leftTicketDTO.train_date={d}'
                          f'&leftTicketDTO.from_station={f}'
                          f'&leftTicketDTO.to_station={t}&purpose_codes={p}')
        self.ticket = []
        self.s = requests.Session()

    def crawl_ticket_info(self):
        self.ticket = []
        r = self.s.get(self.query_url)
        for line in r.json()['data']['result']:
            ls = line.split('|')
            if ls[0]:
                self.ticket.append({
                    'train_num': ls[3],
                    'date': ls[13],
                    'start_at': ls[8],
                    'arrive_at': ls[9],
                    'seat_level_0': ls[32],
                    'seat_level_1': ls[31],
                    'seat_level_2': ls[30],
                    'sleeper_level_0': ls[21],
                    'sleeper_level_1': ls[23],
                    'motor_sleeper': ls[33],
                    'sleeper_level_2': ls[28],
                    'soft_seat': ls[27],
                    'hard_seat': ls[29],
                    'no_seat': ls[26],
                })
        import pprint
        pprint.pprint(self.ticket)

    def check_tickect_info(self):
        if not self.ticket:
            return
        for ticket in self.ticket:
            if ticket['train_num'] == 'G1010':
                print(ticket)

if __name__ == "__main__":
    g = Grabber('2019-01-25', 'SZQ', 'WHN', 'ADULT')
    g.crawl_ticket_info()
    g.check_tickect_info()