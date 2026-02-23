import requests
import os
import urllib.parse # 用于处理搜索词中的特殊字符

# ... 之前的配置读取保持不变 ...

def get_news():
    if not NEWS_KEY: return "❌ 缺少 NEWS_KEY"
    url = f"https://apis.tianapi.com/douyinhot/index?key={NEWS_KEY}"
    try:
        res = requests.get(url, timeout=10).json()
        if res.get('code') == 200:
            news_list = res.get('result', {}).get('list', [])
            formatted_list = []
            for i, item in enumerate(news_list[:10], 1):
                word = item['word']
                # 编码关键词，生成抖音搜索链接
                encoded_word = urllib.parse.quote(word)
                link = f"https://www.douyin.com/search/{encoded_word}"
                
                # 格式化：序号. [关键词](链接) [热度]
                hot_index = item.get('hotindex', '')
                line = f"{i}. **[{word}]({link})** 📈 {hot_index}"
                formatted_list.append(line)
            
            return "\n\n".join(formatted_list)
        return f"❌ 新闻报错：{res.get('msg')}"
    except:
        return "❌ 新闻请求异常"

def send_dingtalk(weather_text, news_text):
    if not DINGTALK_TOKEN: return
    token = DINGTALK_TOKEN.split('=')[-1]
    url = f"https://oapi.dingtalk.com/robot/send?access_token={token}"
    
    # 使用更精美的 Markdown 排版
    markdown_content = (
        f"### 📅 提醒：每日早报已送达\n\n"
        f"--- \n\n"
        f"🌡️ **今日天气** \n\n {weather_text} \n\n"
        f"--- \n\n"
        f"🔥 **抖音热搜 (点击标题跳转)** \n\n {news_text} \n\n"
        f"--- \n\n"
        f"> 💡 *提示：点击热搜词可直接在浏览器或抖音 App 中查看详情*"
    )
    
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "提醒：每日汇报",
            "text": markdown_content
        }
    }
    requests.post(url, json=data)

if __name__ == "__main__":
    w = get_weather()
    n = get_news()
    send_dingtalk(w, n)
