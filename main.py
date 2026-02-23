import requests
import os

# 配置读取
DINGTALK_TOKEN = os.getenv("DINGTALK_TOKEN")
WEATHER_KEY = os.getenv("WEATHER_KEY")
NEWS_KEY = os.getenv("NEWS_KEY")
CITY_ID = "101010100"  # 北京

def get_weather():
    if not WEATHER_KEY: return "❌ 缺少 WEATHER_KEY"
    url = f"https://devapi.qweather.com/v7/weather/now?location={CITY_ID}&key={WEATHER_KEY}"
    try:
        res = requests.get(url, timeout=10).json()
        if res.get('code') == '200':
            now = res['now']
            return f"🌡️ **今日天气**：{now['text']}，气温 {now['temp']}°C"
        return f"❌ 天气接口返回码：{res.get('code')} (请检查Key是否有效)"
    except:
        return "❌ 天气请求异常"

def get_news(): # 这里修正了之前的 ddef 拼写错误
    if not NEWS_KEY: return "❌ 缺少 NEWS_KEY"
    url = f"https://apis.tianapi.com/douyinhot/index?key={NEWS_KEY}"
    try:
        res = requests.get(url, timeout=10).json()
        if res.get('code') == 200:
            news_list = res.get('result', {}).get('list', [])
            # 抖音热搜使用的是 'word' 字段
            news_str = "\n".join([f"· {i['word']}" for i in news_list[:10]])
            return f"🔥 **抖音热搜**：\n\n{news_str}"
        return f"❌ 新闻报错：{res.get('msg')}" # 这里的错误信息会告诉你是否申请了API
    except:
        return "❌ 新闻请求异常"

def send_dingtalk(content):
    if not DINGTALK_TOKEN: return
    # 清理 Token 格式，防止误填了整个 URL
    token = DINGTALK_TOKEN.split('=')[-1]
    url = f"https://oapi.dingtalk.com/robot/send?access_token={token}"
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "提醒：每日汇报",
            "text": f"## 提醒：您订阅的早报已送达 \n\n {content}"
        }
    }
    requests.post(url, json=data)

if __name__ == "__main__":
    w = get_weather()
    n = get_news()
    send_dingtalk(f"{w}\n\n---\n\n{n}")
