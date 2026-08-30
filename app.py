import os
import requests
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SANAP - Tải TikTok Không Logo VIP</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .container { background: #1e293b; padding: 30px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); width: 100%; max-width: 450px; text-align: center; border: 1px solid #334155; }
        h1 { font-size: 24px; margin-bottom: 8px; color: #38bdf8; font-weight: 700; }
        p.subtitle { font-size: 13px; color: #94a3b8; margin-bottom: 24px; }
        .input-group { margin-bottom: 16px; text-align: left; }
        label { display: block; font-size: 13px; margin-bottom: 6px; color: #cbd5e1; }
        input[type="text"], select { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: #fff; font-size: 14px; outline: none; transition: 0.2s; }
        input[type="text"]:focus, select:focus { border-color: #38bdf8; box-shadow: 0 0 5px rgba(56, 189, 248, 0.3); }
        button { width: 100%; padding: 12px; background: linear-gradient(135deg, #0ea5e9, #2563eb); border: none; border-radius: 8px; color: white; font-size: 15px; font-weight: 600; cursor: pointer; transition: 0.2s; margin-top: 10px; }
        button:hover { opacity: 0.9; transform: translateY(-1px); }
        .result { margin-top: 20px; text-align: left; background: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #334155; display: none; }
        .result h3 { font-size: 14px; color: #4ade80; margin-bottom: 8px; }
        .result p { font-size: 12px; color: #cbd5e1; margin-bottom: 6px; word-break: break-all; }
        .btn-download { display: inline-block; padding: 8px 16px; background: #22c55e; color: white; text-decoration: none; border-radius: 6px; font-size: 13px; font-weight: 600; margin-top: 10px; text-align: center; width: 100%; }
        .loading { display: none; margin-top: 15px; color: #38bdf8; font-size: 13px; }
        .footer { margin-top: 20px; font-size: 11px; color: #64748b; }
    </style>
</head>
<body>
    <div class="container">
        <h1>✨ SANAP WEB ✨</h1>
        <p class="subtitle">Bóc tách video TikTok không logo & MP3 siêu tốc</p>
        
        <div class="input-group">
            <label>👉 Dán Link TikTok:</label>
            <input type="text" id="url" placeholder="https://www.tiktok.com/@...">
        </div>

        <div class="input-group">
            <label>👉 Chọn định dạng:</label>
            <select id="type">
                <option value="mp4">🎬 Tải Video MP4 (Không Logo)</option>
                <option value="mp3">🎵 Tải Nhạc Nền MP3 (Audio)</option>
            </select>
        </div>

        <button onclick="processSanap()">🚀 TẢI NGAY</button>
        
        <div class="loading" id="loading">⏳ Sanap đang xử lý, chờ chút nha đại boss...</div>

        <div class="result" id="resultBox">
            <h3 id="resAuthor"></h3>
            <p><b>Tiêu đề:</b> <span id="resTitle"></span></p>
            <a id="resLink" href="#" target="_blank" class="btn-download">📥 Bấm vào đây để tải file</a>
        </div>

        <div class="footer">Created by ThienVN • Sanap Pro v6.0</div>
    </div>

    <script>
        async function processSanap() {
            let url = document.getElementById('url').value.trim();
            let type = document.getElementById('type').value;
            let loading = document.getElementById('loading');
            let resultBox = document.getElementById('resultBox');

            if (!url) {
                alert("Chưa nhập link kìa ông ơi!");
                return;
            }

            loading.style.display = 'block';
            resultBox.style.display = 'none';

            try {
                let response = await fetch('/api/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url, type: type })
                });
                let data = await response.json();
                
                loading.style.display = 'none';

                if (data.success) {
                    document.getElementById('resAuthor').innerText = "✔ Tác giả: " + data.author;
                    document.getElementById('resTitle').innerText = data.title;
                    let downloadBtn = document.getElementById('resLink');
                    downloadBtn.href = data.download_url;
                    downloadBtn.innerText = type === 'mp4' ? "📥 Tải Video MP4 Về Máy" : "📥 Tải Nhạc MP3 Về Máy";
                    resultBox.style.display = 'block';
                } else {
                    alert("❌ Lỗi: " + data.message);
                }
            } catch (err) {
                loading.style.display = 'none';
                alert("❌ Lỗi kết nối máy chủ!");
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/download', methods=['POST'])
def api_download():
    req_data = request.json
    url = req_data.get('url')
    file_type = req_data.get('type')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://tikwm.com/'
    }

    try:
        api_url = f"https://tikwm.com/api/?url={url}&hd=1"
        response = requests.get(api_url, headers=headers, timeout=12)
        data = response.json()

        if data.get("code") == 0:
            video_info = data.get("data", {})
            author = video_info.get("author", {}).get("nickname", "Unknown")
            title = video_info.get("title", "tiktok_media")
            
            if file_type == 'mp4':
                download_url = video_info.get("hdplay") or video_info.get("play")
            else:
                download_url = video_info.get("music")

            if not download_url:
                return jsonify({'success': False, 'message': 'Không tìm thấy link tải từ máy chủ!'})

            return jsonify({
                'success': True,
                'author': author,
                'title': title,
                'download_url': download_url
            })
        else:
            return jsonify({'success': False, 'message': 'Link TikTok không hợp lệ hoặc đã bị xoá!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
  
