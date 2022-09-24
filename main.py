import math
import os
import random
from datetime import date, datetime

import requests
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage


# 自己的app_id 和 app_secret
app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

work_start = os.environ['WORK_START']
school_start = os.environ['SCHOOL_START']
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']
next_meet_day = os.environ['NEXT_MEET_DAY']

template_id = os.environ["TEMPLATE_ID"]
user_id = os.environ["USER_ID"]
users = user_id.split(",")


# 所在地天气
def get_weather():
    url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city="+city
    res = requests.get(url).json()
    weather = res['data']['list'][0]
    return weather['weather'], math.floor(weather['temp'])


# 每日一句
def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']


# 字体随机颜色
def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


# next_time - now_time的时间
def get_sub_days(now_time, next_time):
    if next_time < now_time:
        next_time = next_time.replace(year=next.year + 1)
    return (next_time - now_time).days


# 准备客户端进行发送
client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)
weather, temperature = get_weather()
# 获取当前时间，日期和周几
now = datetime.now()
time = now.strftime("%Y-%m-%d %H:%M:%S")
weeks = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日", ]
day_Week = datetime.now().weekday()  # 返回从0开始的数字，比如今天是星期5，那么返回的就是4
time_week = time + weeks[day_Week]
# print(time, weeks[day_Week])

work_start_time = datetime.strptime(work_start, "%Y-%m-%d")
school_start_time = datetime.strptime(school_start, "%Y-%m-%d")
start_time = datetime.strptime(start_date, "%Y-%m-%d")
next_birth = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
next_meet = datetime.strptime(next_meet_day, "%Y-%m-%d")
data = {"date": {"value": time_week},
        "city": {"value": city},
        "weather": {"value": weather},
        "temperature": {"value": temperature},
        "work_days": {"value": get_sub_days(work_start_time, now)},
        "school_days": {"value": get_sub_days(school_start_time, now)},
        # "love_days": {"value": get_sub_days(start_time, now)},  # get_count()
        "next_meet": {"value": next_meet_day},  # 这里是字符串
        "next_meet_left": {"value": get_sub_days(now, next_meet)},
        # "birthday_left": {"value": get_sub_days(next_birth, now)},  # get_birthday()
        "words": {"value": get_words(), "color": get_random_color()}}

for user in users:
    print(user)
    res = wm.send_template(user, template_id, data)
    print(res)
