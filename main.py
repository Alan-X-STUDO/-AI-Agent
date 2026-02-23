import requests
import os
import json

# 从环境变量中读取密钥
DINGTALK_TOKEN = os.getenv("DINGTALK_TOKEN")
WEATHER_KEY = os.getenv("WEATHER_KEY")
NEWS_KEY = os.getenv("NEWS_KEY")
CITY_ID = os.getenv("CITY_ID", "101010100") # 默认北京，建议在 Secrets 里也配一个 CITY_ID

def get_weather():
    if not WEATHER_KEY:
        return "❌ 错误：未配置 WEATHER_KEY"
    
    # 免费版域名：devapi.qweather.com
    url = f"https://devapi.qweather.com/v7/weather/now?location={CITY_ID}&key={WEATHER_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        res = response.json()
        
        # --- 关键调试：打印完整返回内容 ---
        print(f"DEBUG - 天气接口原始返回: {json.dumps(res, ensure_ascii=False)}")
        
        # 安全读取 code 字段
        code = res.get('code')
        if code == '200':
            now = res['now']
            return f"🌡️ **今日天气**：{now['text']}，气温 {now['temp']}°C，体感 {now['feelsLike']}°C"
        else:
            return f"❌ 天气接口报错，代码：{code} (请查阅和风天气文档)"
            
    except Exception as e:
        return f"❌ 天气请求发生异常: {str(e)}"

def get_news():
    if not NEWS_KEY:
        return "❌ 错误：未配置 NEWS_KEY"
        
    url = f"https://apis.tianapi.com/bulletin/index?key={NEWS_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        res = response.json()
        
        # --- 关键调试：打印完整返回内容 ---
        print(f"DEBUG - 新闻接口原始返回: {json.dumps(res, ensure_ascii=False)}")
        
        if res.get('code') == 200:
            list_news = res.get('result', {}).get('list', [])
            news_str = "\n".join([f"· {item['title']}" for item in list_news[:10]])
            return f"🔥 **今日热点**：\n\n{news_str}"
        else:
            return f"❌ 新闻接口报错，代码：{res.get('code')}，信息：{res.get('msg')}"
            
    except Exception as e:
        return f"❌ 新闻请求发生异常: {str(e)}"

def send_dingtalk(content):
    if not DINGTALK_TOKEN:
        print("❌ 错误：未配置 DINGTALK_TOKEN")
        return
        
    url = f"https://oapi.dingtalk.com/robot/send?access_token={DINGTALK_TOKEN}"
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "每日早报",
            "text": f"## 📅 每日速报 \n\n {content} \n\n > 自定义关键词：热点" 
        }
    }
    try:
        res = requests.post(url, json=data, timeout=10)
        print(f"DEBUG - 钉钉推送结果: {res.text}")
    except Exception as e:
        print(f"❌ 钉钉推送异常: {str(e)}")

if __name__ == "__main__":
    print("--- 任务开始 ---")
    weather_info = get_weather()
    news_info = get_news()
    
    full_content = f"{weather_info}\n\n---\n\n{news_info}"
    send_dingtalk(full_content)
    print("--- 任务结束 ---")
