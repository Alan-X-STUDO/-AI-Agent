import requests
import os
import json

# 配置：从 GitHub Secrets 获取
DINGTALK_TOKEN = os.getenv("DINGTALK_TOKEN")
WEATHER_KEY = os.getenv("WEATHER_KEY")
NEWS_KEY = os.getenv("NEWS_KEY")
CITY_ID = "101010100" # 北京的城市代码

def get_weather():
    if not WEATHER_KEY: return "❌ 缺少 WEATHER_KEY"
    # 强制使用和风天气免费版域名
    url = f"https://devapi.qweather.com/v7/weather/now?location={CITY_ID}&key={WEATHER_KEY}"
    try:
        res = requests.get(url, timeout=10).json()
        print(f"DEBUG - 天气接口返回: {res}")
        if res.get('code') == '200':
            now = res['now']
            return f"🌡️ **今日天气**：{now['text']}，气温 {now['temp']}°C，体感 {now['feelsLike']}°C"
        return f"❌ 天气报错：{res.get('code', '未知')}"
    except Exception as e:
        return f"❌ 天气请求失败: {str(e)}"

ddef get_news():
    if not NEWS_KEY: return "❌ 缺少 NEWS_KEY"
    # 注意：这是抖音热搜的接口地址
    url = f"https://apis.tianapi.com/douyinhot/index?key={NEWS_KEY}"
    try:
        res = requests.get(url, timeout=10).json()
        if res.get('code') == 200:
            news_list = res.get('result', {}).get('list', [])
            # 抖音热搜使用的是 'word' 字段
            news_str = "\n".join([f"· {item['word']}" for item in news_list[:10]])
            return f"🔥 **抖音热搜**：\n\n{news_str}"
        return f"❌ 新闻报错：{res.get('msg', '未知错误')}"
    except Exception as e:
        return f"❌ 新闻请求异常"

def send_dingtalk(content):
    if not DINGTALK_TOKEN:
        print("❌ 缺少 DINGTALK_TOKEN")
        return
    
    # 鲁棒处理：防止 Token 填成了整段 URL
    clean_token = DINGTALK_TOKEN.split("access_token=")[-1]
    url = f"https://oapi.dingtalk.com/robot/send?access_token={clean_token}"
    
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "提醒：每日汇报", # 标题包含关键词
            "text": f"## 提醒：您订阅的早报已送达 \n\n {content}" # 正文包含关键词
        }
    }
    try:
        res = requests.post(url, json=data).json()
        print(f"DEBUG - 钉钉推送结果: {res}")
    except Exception as e:
        print(f"❌ 钉钉推送失败: {str(e)}")

if __name__ == "__main__":
    print("--- 任务开始 ---")
    weather_info = get_weather()
    news_info = get_news()
    full_body = f"{weather_info}\n\n---\n\n{news_info}"
    send_dingtalk(full_body)
    print("--- 任务结束 ---")
