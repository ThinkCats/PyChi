#! /usr/bin/env python3

from apscheduler.schedulers.background import BackgroundScheduler
from bs4 import BeautifulSoup as bsp
from bottle import route, run
from datetime import date
import time
import json
import requests
import logging

# 创建一个logger
logger = logging.getLogger('mylogger')
logger.setLevel(logging.DEBUG)

# 创建一个handler，用于写入日志文件
fh = logging.FileHandler('logger.log')
fh.setLevel(logging.DEBUG)

# 再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# 定义handler的输出格式
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# 给logger添加handler
logger.addHandler(fh)
logger.addHandler(ch)

food_wanted_list = ['15868', '15394', '16731']
defult_food = ['16642', '15614']


@route('/')
def index():
    return 'hello world'


def get_now():
    return time.strftime('%Y-%m-%d', time.localtime(time.time()))


def myJob():
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    logger.info('begin check out job')
    s = login()
    menus = get_menu(s)
    food_id = get_food_id(menus)
    if food_id is not None:
        check_out(food_id, s)


def scheduler():
    sched = BackgroundScheduler()
    sched.add_job(myJob, 'cron', day="*", hour='10', minute='1', second='1')
    sched.start()


def login():
    s = requests.session()
    login_data = {
        'LoginForm[username]': '18357118527',
        'LoginForm[password]': '74dc7108dc671dc5b3b38c493cbcc4df',
        'LoginForm[autoLogin]': '1',
        'yt0': '登录'}
    s.post('http://wos.chijidun.com/login.html', login_data)
    return s


def get_menu(s):
    now = get_now()
    menu_url = (
        'http://wos.chijidun.com/order/getMenu.html?mid=15003&date=%s&type=3' %
        now)
    r = s.get(menu_url)
    r.encoding = 'utf8'
    return r.text


def get_food_id(text):
    json_str = json.loads(text)
    data = json_str['data']
    soup = bsp(data, "html.parser")
    li_data = soup.find_all('li', class_='grid-row')
    logger.info(li_data)
    if len(li_data) > 0:
        for food in li_data:
            food_id = food['data-id']
            if str(food_id) in str(food_wanted_list):
                return food_id
    else:
        logger.info('No HeiErShe, Check Default Food')
        idx = (date.today().day) % 2
        return defult_food[idx]


def check_out(food_id, session):
    idx = (date.today().day) % 2
    if food_id is None:
        food_id = defult_food[idx]

    check_out_url = 'http://wos.chijidun.com/order/saveOrder.html'
    now = get_now()
    check_out_data = {
        'items': str(food_id) +
        ':1',
        'addrId': '30',
        'mealType': '3',
        'date': now
    }
    result = session.post(check_out_url, check_out_data)
    result.encoding = 'utf8'
    logger.info('check out result:', result.text)

if __name__ == '__main__':
    logger.info('----- begin run ----------')
    scheduler()
    logger.info('------ run web ----------')
    run(host='0.0.0.0', port=8000)
