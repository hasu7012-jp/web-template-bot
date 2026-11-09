from collections import Counter
import datetime
import time
from playwright.sync_api import sync_playwright

# 分析したいサイトのURLリスト（好きなデザインサイトのURLを増やせます）
TARGET_URLS = [
    "https://gsap.com",
]


def analyze_and_generate():
  detected_libs = set()
  all_colors = []

  with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for url in TARGET_URLS:
      try:
        print(f"分析中: {url}")
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(2)

        # 1. アニメーション系ライブラリの検出
        scripts = page.evaluate(
            "() => Array.from(document.scripts).map(s => s.src).filter(src =>"
            " src)"
        )
        keywords = {
            "gsap": "GSAP",
            "three": "Three.js",
            "lenis": "Lenis",
            "aos": "AOS",
            "swiper": "Swiper",
        }
        for src in scripts:
          for k, v in keywords.items():
            if k in src.lower():
              detected_libs.add(v)

        # 2. 使われている色の抽出
        colors = page.evaluate("""() => {
                    const elements = document.querySelectorAll('*');
                    const list = [];
                    for (let i = 0; i < Math.min(elements.length, 200); i++) {
                        const style = window.getComputedStyle(elements[i]);
                        list.push(style.backgroundColor);
                        list.push(style.color);
                    }
                    return list;
                }""")
        valid = [
            c
            for c in colors
            if c
            not in (
                "rgba(0, 0, 0, 0)",
                "",
                "rgb(255, 255, 255)",
                "rgb(0, 0, 0)",
            )
        ]
        all_colors.extend(valid)

      except Exception as e:
        print(f"スキップ ({url}): {e}")

    browser.close()

  # 一番多く使われていた色を抽出（見つからない場合はデフォルトのネオンカラー）
  top_colors = Counter(all_colors).most_common(3)
  primary_color = top_colors[0][0] if len(top_colors) > 0 else "#00f2fe"
  accent_color = top_colors[1][0] if len(top_colors) > 1 else "#4facfe"
  now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  # 3. アニメーション付きHTMLテンプレートの生成
  html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto Generated Animated Template</title>
    <script src="https://cloudflare.com"></script>
    <script src="https://cloudflare.com"></script>
    <style>
        :root {{
            --primary: {primary_color};
            --accent: {accent_color};
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: sans-serif; }}
        body {{
            background-color: #0d0d12;
            color: #ffffff;
            overflow-x: hidden;
        }}
        .hero {{
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            background: radial-gradient(circle at center, var(--primary) 0%, #0d0d12 70%);
        }}
        .hero h1 {{
            font-size: 4rem;
            letter-spacing: 0.1em;
            opacity: 0;
            transform: translateY(40px);
        }}
        .hero p {{
            margin-top: 20px;
            font-size: 1.2rem;
            color: #cccccc;
            opacity: 0;
        }}
        .section {{
            padding: 100px 20px;
            max-width: 1000px;
            margin: 0 auto;
        }}
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 30px;
            margin-top: 50px;
        }}
        .card {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--accent);
            border-radius: 16px;
            padding: 40px 25px;
            backdrop-filter: blur(10px);
            opacity: 0;
            transform: translateY(50px);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .card:hover {{
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.5);
        }}
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            background: var(--accent);
            color: #000;
            font-weight: bold;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>

    <section class="hero">
        <h1 class="hero-title">NEXT GEN DESIGN</h1>
        <p class="hero-sub">Auto-generated at {now_str} | Detected: {', '.join(detected_libs) if detected_libs else 'GSAP'}</p>
    </section>

    <section class="section">
        <h2>Interactive Features</h2>
        <div class="card-grid">
            <div class="card">
                <span class="badge">ANIMATION 01</span>
                <h3>Smooth Entrance</h3>
                <p>GSAPを使った滑らかなフェードイン＆スライドアニメーションを実装しています。</p>
            </div>
            <div class="card">
                <span class="badge">ANIMATION 02</span>
                <h3>Scroll Trigger</h3>
                <p>スクロール位置に合わせて要素が順番に浮かび上がるモダンな演出です。</p>
            </div>
            <div class="card">
                <span class="badge">STYLE</span>
                <h3>Dynamic Palette</h3>
                <p>収集したトレンドカラー（{primary_color}）を自動でテーマに反映しました。</p>
            </div>
        </div>
    </section>

    <script>
        gsap.registerPlugin(ScrollTrigger);

        gsap.to(".hero-title", {{ opacity: 1, y: 0, duration: 1.2, ease: "power4.out" }});
        gsap.to(".hero-sub", {{ opacity: 1, duration: 1, delay: 0.5 }});

        gsap.to(".card", {{
            scrollTrigger: {{
                trigger: ".card-grid",
                start: "top 80%",
            }},
            opacity: 1,
            y: 0,
            duration: 0.8,
            stagger: 0.2,
            ease: "back.out(1.7)"
        }});
    </script>
</body>
</html>
"""
  with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
  print("index.html の生成が完了しました！")


if __name__ == "__main__":
  analyze_and_generate()
