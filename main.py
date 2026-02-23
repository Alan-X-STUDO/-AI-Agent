import requests
import os
import urllib.parse

# --- 1. 配置读取 (从 GitHub Secrets 获取) ---
DINGTALK_TOKEN = os.getenv("DINGTALK_TOKEN")
WEATHER_KEY = os.getenv("WEATHER_KEY")
NEWS_KEY = os.getenv("NEWS_KEY")

# 修改为：成都龙泉驿 城市代码
CITY_ID = "101270107" 

def get_weather():
    """获取天气信息 - 简约排版"""
    if not WEATHER_KEY: return "❌ 缺少 WEATHER_KEY"
    
    # 你的专属域名
    custom_host = "nk6apxex5g.re.qweatherapi.com" 
    url = f"https://{custom_host}/v7/weather/now?location={CITY_ID}&key={WEATHER_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        res = response.json()
        
        if res.get('code') == '200':
            now = res['now']
            # 简约排版格式：[图标] 天气 | 温度 | 湿度 | 风向
            return f"✨ {now['text']} | 🌡️ {now['temp']}°C | 💧 湿度 {now['humidity']}% | 🌬️ {now['windDir']}"
        
        return f"❌ 天气报错码: {res.get('code')}"
    except Exception as e:
        return f"❌ 天气连接异常: {str(e)}"

def get_news():
    """获取抖音热搜 - 保持完美逻辑"""
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
    token = DINGTALK_TOKEN.split('=')[-1] if 'access_token=' in DINGTALK_TOKEN else DINGTALK_TOKEN
    url = f"https://oapi.dingtalk.com/robot/send?access_token={token}"
    
    # 采用更加精致简约的 Markdown 布局
    content = (
        f"### 📅 提醒：早安！您的每日简报\n\n"
        f"--- \n\n"
        f"📍 **成都·龙泉驿** \n\n > {w_info} \n\n"
        f"--- \n\n"
        f"🔥 **抖音热搜 (点击标题直达)** \n\n {n_info} \n\n"
        f"--- \n\n"
        f"💡 *点击蓝色文字直接跳转抖音查看详情*"
    )
    
    data = {
        "msgtype": "markdown",
        "markdown": {"title": "提醒：每日汇报", "text": content}
    }
    requests.post(url, json=data)

if __name__ == "__main__":
    weather_data = get_weather()
    news_data = get_news()
    send_dingtalk(weather_data, news_data)
    weather_data = get_weather()
    news_data = get_news()
    send_dingtalk(weather_data, news_data)
