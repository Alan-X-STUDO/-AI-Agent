import requests
import os
import urllib.parse

# --- 1. 基础配置 (从 GitHub Secrets 读取) ---
DINGTALK_TOKEN = os.getenv("DINGTALK_TOKEN")
WEATHER_KEY = os.getenv("WEATHER_KEY")
NEWS_KEY = os.getenv("NEWS_KEY")

# 在这里明确定义北京的城市 ID
CITY_ID = "101010100" 

def get_weather():
    """获取天气信息 - 兼容域名版"""
    if not WEATHER_KEY: return "❌ 缺少 WEATHER_KEY"
    
    # 自动尝试标准版域名(api)和开发版域名(devapi)
    urls = [
        f"https://api.qweather.com/v7/weather/now?location={CITY_ID}&key={WEATHER_KEY}",
        f"https://devapi.qweather.com/v7/weather/now?location={CITY_ID}&key={WEATHER_KEY}"
    ]
    
    last_res = {}
    try:
        for url in urls:
            response = requests.get(url, timeout=10)
            res = response.json()
            last_res = res
            if res.get('code') == '200':
                now = res['now']
                return f"{now['text']} | 🌡️ {now['temp']}°C | 💧 湿度 {now['humidity']}%"
        
        # 如果都失败了，抓取具体的报错码
        err_code = last_res.get('code', 'Unknown')
        if 'error' in last_res:
            err_code = f"{last_res['error'].get('title')} ({last_res['error'].get('status')})"
        return f"❌ 天气报错: {err_code}"
    except:
        return "❌ 天气连接异常"

def get_news():
    """获取抖音热搜 - 保持你现有的完美逻辑不变"""
    if not NEWS_KEY: return "❌ 缺少 NEWS_KEY"
    url = f"https://apis.tianapi.com/douyinhot/index?key={NEWS_KEY}"
    try:
        res = requests.get(url, timeout=10).json()
        if res.get('code') == 200:
            news_list = res.get('result', {}).get('list', [])
            formatted_lines = []
            for i, item in enumerate(news_list[:10], 1):
                word = item['word']
                encoded_word = urllib.parse.quote(word)
                link = f"https://www.douyin.com/search/{encoded_word}"
                formatted_lines.append(f"{i}. **[{word}]({link})**")
            return "\n\n".join(formatted_lines)
        return f"❌ 新闻报错: {res.get('msg')}"
    except:
        return "❌ 新闻连接异常"

def send_dingtalk(w_info, n_info):
    """发送格式化的钉钉消息"""
    if not DINGTALK_TOKEN: return
    # 自动处理 Token 格式
    token = DINGTALK_TOKEN.split('=')[-1] if 'access_token=' in DINGTALK_TOKEN else DINGTALK_TOKEN
    url = f"https://oapi.dingtalk.com/robot/send?access_token={token}"
    
    content = (
        f"### 📅 提醒：每日早报已送达\n\n"
        f"--- \n\n"
        f"🌡️ **今日天气** \n\n > {w_info} \n\n"
        f"--- \n\n"
        f"🔥 **抖音热搜 (点击标题直达)** \n\n {n_info} \n\n"
        f"--- \n\n"
        f"💡 *提示：点击上方蓝色文字可直接跳转抖音查看详情*"
    )
    
    data = {
        "msgtype": "markdown",
        "markdown": {"title": "提醒：每日汇报", "text": content}
    }
    requests.post(url, json=data)

if __name__ == "__main__":
    # 依次获取数据并发送
    weather_data = get_weather()
    news_data = get_news()
    send_dingtalk(weather_data, news_data)
