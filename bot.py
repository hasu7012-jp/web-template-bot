import datetime
import json
import urllib.request
import xml.etree.ElementTree as ET


def get_weather():
  # 横浜市の緯度・経度（必要に応じて変更可能）
  lat, lon = 35.4437, 139.6380
  url = f"https://open-meteo.com{lat}&longitude={lon}&current=temperature_2m,weather_code&daily=temperature_2m_max,temperature_2m_min&timezone=Asia%2FTokyo"
  try:
    req = urllib.request.urlopen(url, timeout=10)
    data = json.loads(req.read().decode("utf-8"))
    current_temp = round(data["current"]["temperature_2m"], 1)
    max_temp = round(data["daily"]["temperature_2m_max"], 1)
    min_temp = round(data["daily"]["temperature_2m_min"], 1)
    code = data["current"]["weather_code"]

    # 天気コードの変換
    if code == 0:
      weather_text, icon = "快晴", "☀️"
    elif code in:
      weather_text, icon = "晴れ / くもり", "⛅"
    elif code in:
      weather_text, icon = "霧", "🌫️"
    elif code in:
      weather_text, icon = "雨", "☔"
    elif code in:
      weather_text, icon = "雪", "❄️"
    elif code in:
      weather_text, icon = "雷雨", "⚡"
    else:
      weather_text, icon = "くもり", "☁️"

    return {
        "temp": current_temp,
        "max": max_temp,
        "min": min_temp,
        "text": weather_text,
        "icon": icon,
    }
  except Exception as e:
    print(f"天気取得エラー: {e}")
    return {"temp": "--", "max": "--", "min": "--", "text": "取得中", "icon": "🌤️"}


def get_news():
  # NHKニュース（主要）のRSSから最新トピックを取得
  rss_url = "https://nhk.or.jp"
  news_list = []
  try:
    req = urllib.request.urlopen(rss_url, timeout=10)
    xml_data = req.read()
    root = ET.fromstring(xml_data)
    for item in root.findall(".//item")[:4]:
      title = item.find("title").text
      news_list.append(title)
  except Exception as e:
    print(f"ニュース取得エラー: {e}")
    news_list = ["最新ニュースの取得待機中です。"]
  return news_list


def generate_dashboard():
  weather = get_weather()
  news_list = get_news()

  # 日本時間の取得
  jst = datetime.timezone(datetime.timedelta(hours=9))
  now_jst = datetime.datetime.now(jst)
  updated_str = now_jst.strftime("%H:%M 更新")

  news_html = "".join(
      [f'<div class="news-item">• {title}</div>' for title in news_list]
  )

  html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- 30分ごとに自動で最新情報へリロード -->
    <meta http-equiv="refresh" content="1800">
    <title>Smart Echo Dashboard</title>
    <link href="https://googleapis.com" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
        }}
        body {{
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            background: #0b0f19;
            color: #ffffff;
            font-family: 'Inter', 'Noto Sans JP', sans-serif;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 4vh 5vw;
            position: relative;
        }}
        /* 背景のゆっくり動く光のオーブ */
        .bg-orb {{
            position: absolute;
            border-radius: 50%;
            filter: blur(90px);
            z-index: 0;
            opacity: 0.45;
            animation: floatOrb 18s infinite alternate ease-in-out;
        }}
        .orb-1 {{
            width: 45vw;
            height: 45vw;
            background: #1d4ed8;
            top: -10%;
            left: -10%;
        }}
        .orb-2 {{
            width: 40vw;
            height: 40vw;
            background: #0f766e;
            bottom: -15%;
            right: -5%;
            animation-delay: -6s;
        }}
        @keyframes floatOrb {{
            0% {{ transform: translate(0, 0) scale(1); }}
            100% {{ transform: translate(5vw, 4vh) scale(1.1); }}
        }}

        /* メインレイアウト（Echo Show横画面最適化） */
        .main-grid {{
            position: relative;
            z-index: 1;
            display: grid;
            grid-template-columns: 1.3fr 1fr;
            gap: 4vw;
            align-items: center;
            height: 68%;
        }}

        /* 左側：時計＆日付 */
        .clock-area {{
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .date-display {{
            font-size: clamp(1.2rem, 2.5vw, 2.2rem);
            color: #94a3b8;
            font-weight: 500;
            letter-spacing: 0.05em;
            margin-bottom: 1vh;
        }}
        .time-display {{
            font-size: clamp(4.5rem, 11vw, 9.5rem);
            font-weight: 700;
            line-height: 1;
            letter-spacing: -0.03em;
            display: flex;
            align-items: baseline;
        }}
        .seconds {{
            font-size: clamp(1.8rem, 4vw, 3.5rem);
            color: #38bdf8;
            margin-left: 1vw;
            font-weight: 500;
        }}

        /* 右側：天気カード（グラスモーフィズム） */
        .weather-card {{
            background: rgba(255, 255, 255, 0.07);
            border: 1px solid rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(20px);
            border-radius: 28px;
            padding: 3.5vh 3vw;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }}
        .weather-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #cbd5e1;
            font-size: clamp(0.9rem, 1.5vw, 1.2rem);
        }}
        .weather-main {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 1vh 0;
        }}
        .weather-icon {{
            font-size: clamp(3.5rem, 7vw, 6rem);
        }}
        .weather-temp {{
            font-size: clamp(3rem, 6.5vw, 5.5rem);
            font-weight: 700;
        }}
        .weather-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding-top: 1.5vh;
            font-size: clamp(0.9rem, 1.6vw, 1.3rem);
        }}
        .temp-high {{ color: #f87171; font-weight: 700; }}
        .temp-low {{ color: #60a5fa; font-weight: 700; margin-left: 1vw; }}

        /* 下部：ニュースティッカー */
        .news-bar {{
            position: relative;
            z-index: 1;
            height: 24%;
            background: rgba(15, 23, 42, 0.65);
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 2vh 2.5vw;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .news-label {{
            font-size: 0.8rem;
            color: #38bdf8;
            font-weight: 700;
            letter-spacing: 0.15em;
            margin-bottom: 0.8vh;
            display: flex;
            justify-content: space-between;
        }}
        .news-list {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.8vh 2vw;
        }}
        .news-item {{
            font-size: clamp(0.85rem, 1.4vw, 1.15rem);
            color: #e2e8f0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
    </style>
</head>
<body>

    <div class="bg-orb orb-1"></div>
    <div class="bg-orb orb-2"></div>

    <div class="main-grid">
        <div class="clock-area">
            <div class="date-display" id="date">----年--月--日 (---)</div>
            <div class="time-display">
                <span id="hm">--:--</span>
                <span class="seconds" id="sec">--</span>
            </div>
        </div>

        <div class="weather-card">
            <div class="weather-header">
                <span>YOKOHAMA / WEATHER</span>
                <span>{updated_str}</span>
            </div>
            <div class="weather-main">
                <div class="weather-icon">{weather['icon']}</div>
                <div class="weather-temp">{weather['temp']}°</div>
            </div>
            <div class="weather-footer">
                <span>{weather['text']}</span>
                <div>
                    <span class="temp-high">H: {weather['max']}°</span>
                    <span class="temp-low">L: {weather['min']}°</span>
                </div>
            </div>
        </div>
    </div>

    <div class="news-bar">
        <div class="news-label">
            <span>LATEST HEADLINES</span>
            <span>AUTO SYNCED</span>
        </div>
        <div class="news-list">
            {news_html}
        </div>
    </div>

    <script>
        function updateClock() {{
            const now = new Date();
            const days = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'];
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const date = String(now.getDate()).padStart(2, '0');
            const day = days[now.getDay()];

            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');

            document.getElementById('date').textContent = `${{year}}.${{month}}.${{date}} [${{day}}]`;
            document.getElementById('hm').textContent = `${{hours}}:${{minutes}}`;
            document.getElementById('sec').textContent = seconds;

            // 時間帯によって背景オーブの色を自動変化
            const h = now.getHours();
            const orb1 = document.querySelector('.orb-1');
            const orb2 = document.querySelector('.orb-2');
if (h >= 5 && h < 11) {{
// 朝：爽やかなシアン・ブルー
orb1.style.background = '#0284c7';
orb2.style.background = '#10b981';
}} else if (h >= 11 && h < 16) {{
// 昼：明るいブルー・インディゴ
orb1.style.background = '#2563eb';
orb2.style.background = '#06b6d4';
}} else if (h >= 16 && h < 19) {{
// 夕方：サンセットオレンジ・パープル
orb1.style.background = '#ea580c';
orb2.style.background = '#7c3aed';
}} else {{
// 夜：落ち着いたディープブルー・ティール
orb1.style.background = '#1e3a8a';
orb2.style.background = '#0f766e';
}}
}}
setInterval(updateClock, 1000);
updateClock();



"""
with open("index.html", "w", encoding="utf-8") as f:
f.write(html_content)
print("スマートダッシュボードの生成が完了しました！")
if name == "main":
generate_dashboard()
