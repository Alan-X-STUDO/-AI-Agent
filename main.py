import requests
import os
import urllib.parse

# 1. 配置读取 (从 GitHub Secrets 获取)
DINGTALK_TOKEN = os.getenv("DINGTALK_TOKEN")
WEATHER_KEY = os.getenv("WEATHER_KEY")
NEWS_KEY = os.getenv("NEWS_KEY")
CITY_ID = "101010100"  # 默认北京，可修改

def get_weather():
    """获取天气信息 - 增强诊断版"""
    if not WEATHER_KEY: return "❌ 缺少 WEATHER_KEY"
    
    url = f"https://devapi.qweather.com/v7/weather/now?location={CITY_ID}&key={WEATHER_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        res = response.json()
        
        # 正常返回 200
        if res.get('code') == '200':
            now = res['now']
            return f"{now['text']} | 🌡️ {now['temp']}°C | 💧 湿度 {now['humidity']}%"
        
        # 处理报错信息 (和风天气在 403 等错误时会返回 error 对象)
        if 'error' in res:
            error_data = res['error']
            return f"❌ 接口报错: {error_data.get('title', '未知')} ({error_data.get('status')})"
        
        return f"❌ 错误码: {res.get('code', 'None')}"
    except Exception as e:
        return f"❌ 请求异常: {str(e)}"

def get_news():
    """获取抖音热搜并生成带链接的列表"""
    if not NEWS_KEY: return "❌ 缺少 NEWS_KEY"
    url = f"https://apis.tianapi.com/douyinhot/index?key={NEWS_KEY}"
    try:
        res = requests.get(url, timeout=10).json()
        if res.get('code') == 200:
            news_list = res.get('result', {}).get('list', [])
            formatted_lines = []
            for i, item in enumerate(news_list[:10], 1):
                word = item['word']
                # 编码关键词，生成抖音网页端搜索链接
                encoded_word = urllib.parse.quote(word)
                link = f"https://www.douyin.com/search/{encoded_word}"
                # 格式：1. [热搜词](链接)
                formatted_lines.append(f"{i}. **[{word}]({link})**")
            return "\n\n".join(formatted_lines)
        return f"❌ 新闻报错: {res.get('msg')}"
    except:
        return "❌ 新闻连接异常"

def send_dingtalk(w_info, n_info):
    """发送格式化的钉钉消息"""
    if not DINGTALK_TOKEN: return
    token = DINGTALK_TOKEN.split('=')[-1]
    url = f"https://oapi.dingtalk.com/robot/send?access_token={token}"
    
    # 构建精美的 Markdown 内容
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
    # 按照顺序调用，确保 get_weather 已定义
    weather = get_weather()
    news = get_news()
    send_dingtalk(weather, news)
