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
    """获取天气信息 - 使用你截图中的专属域名"""
    if not WEATHER_KEY: return "❌ 缺少 WEATHER_KEY"
    
    # ✅ 这里必须是你截图 image_c6bcc0 中的这个专属地址
    custom_host = "nk6apxex5g.re.qweatherapi.com" 
    url = f"https://{custom_host}/v7/weather/now?location={CITY_ID}&key={WEATHER_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        res = response.json()
        
        # 如果返回 200，说明“专属域名”和“长密钥”都对上了
        if res.get('code') == '200':
            now = res['now']
            return f"{now['text']} | 🌡️ {now['temp']}°C | 💧 湿度 {now['humidity']}%"
        
        # 如果还是报错，这里会显示具体的错误码，帮你定位
        return f"❌ 天气报错码: {res.get('code')}"
    except Exception as e:
        return f"❌ 天气连接异常: {str(e)}"
        
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
