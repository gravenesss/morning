from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

# 自己的app_id 和 app_secret
app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]

today = datetime.now()
start_date = os.environ['START_DATE']
city = os.environ['CITY']
birthday = os.environ['BIRTHDAY']

user_id = os.environ["USER_ID"]
users = user_id.split(",")
template_id = os.environ["TEMPLATE_ID"]


def get_weather():
  url = "http://autodev.openspeech.cn/csp/api/v2.1/weather?openId=aiuicus&clientType=android&sign=android&city=" + city
  res = requests.get(url).json()
  weather = res['data']['list'][0]
  return weather['weather'], math.floor(weather['temp'])

def get_count():
  delta = today - datetime.strptime(start_date, "%Y-%m-%d")
  return delta.days

def get_birthday():
  next = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
  if next < datetime.now():
    next = next.replace(year=next.year + 1)
  return (next - today).days

def get_words():
  words = requests.get("https://api.shadiao.pro/chp")
  if words.status_code != 200:
    return get_words()
  return words.json()['data']['text']

def get_random_color():
  return "#%06x" % random.randint(0, 0xFFFFFF)


client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)
weather, temperature = get_weather()

# 获取时间
now = datetime.now()
time = now.strftime("%Y-%m-%d") #  %H:%M:%S 相差8个小时，可以自行设置时区
weeks = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日", ]
day_Week = datetime.now().weekday()  ### 返回从0开始的数字，比如今天是星期5，那么返回的就是4
time_week = time + weeks[day_Week]
# print(time, weeks[day_Week])

data = {"date": {"value": time_week},
        "city": {"value": city},
        "weather": {"value": weather},
        "temperature": {"value": temperature},
        "love_days": {"value": get_count()},
        "birthday_left": {"value": get_birthday()},
        "words": {"value": get_words(), "color": get_random_color()}}

for user in users:
    print(user)
    res = wm.send_template(user, template_id, data)
    print(res)
