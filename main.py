import requests
import os

# 从环境变量中读取密钥（安全第一，不要直接写在代码里）
DINGTALK_TOKEN = os.getenv("DINGTALK_TOKEN")
WEATHER_KEY = os.getenv("WEATHER_KEY")
NEWS_KEY = os.getenv("NEWS_KEY")
CITY_ID = "101010100"  # 城市ID，比如北京是101010100

def get_weather():
    # 调用和风天气接口
    url = f"https://devapi.qweather.com/v7/weather/now?location={CITY_ID}&key={WEATHER_KEY}"
    res = requests.get(url).json()
    if res['code'] == '200':
        now = res['now']
        return f"🌡️ **今日天气**：{now['text']}，气温 {now['temp']}°C，体感 {now['feelsLike']}°C"
    return "❌ 天气数据获取失败"

def get_news():
    # 调用天行数据早报接口
    url = f"https://apis.tianapi.com/bulletin/index?key={NEWS_KEY}"
    res = requests.get(url).json()
    if res['code'] == 200:
        list_news = res['result']['list']
        news_str = "\n".join([f"· {item['title']}" for item in list_news[:10]])
        return f"🔥 **今日热点**：\n\n{news_str}"
    return "❌ 新闻数据获取失败"

def send_dingtalk(content):
    url = f"https://oapi.dingtalk.com/robot/send?access_token={DINGTALK_TOKEN}"
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "每日早报",
            "text": f"## 📅 每日速报 \n\n {content} \n\n > 自定义关键词：热点" # 记得包含你的关键词
        }
    }
    requests.post(url, json=data)

if __name__ == "__main__":
    weather_info = get_weather()
    news_info = get_news()
    full_content = f"{weather_info}\n\n---\n\n{news_info}"
    send_dingtalk(full_content)
