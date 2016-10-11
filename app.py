from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup as bsp
import time
import json
import requests
import logging

logging.basicConfig(filename='logger.log',format='%(asctime)s %(name)-4s %(levelname)-4s: %(message)s',level=logging.INFO)


def get_now():
    return time.strftime('%Y-%m-%d', time.localtime(time.time()))


def myJob():
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    logging.info('begin check out job')
    s = login()
    menus = get_menu(s)
    food_id = get_food_id(menus)
    if food_id is not None:
        check_out(food_id, s)


def scheduler():
    sched = BlockingScheduler()
    sched.add_job(myJob, 'cron', day="*", hour='9', minute='32', second='1')
    sched.start()


def login():
    s = requests.session()
    login_data = {
        'LoginForm[username]': 'yourusername',
        'LoginForm[password]': 'yourpassword md5',
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
    if len(li_data) > 0:
        food_id = li_data[0]['data-id']
        logging.info('food id:', food_id)
        return food_id
    else:
        logging.info('无可选菜品')
        return None


def check_out(food_id, session):
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
    logging.info('check out result:', result.text)

if __name__ == '__main__':
    scheduler()
