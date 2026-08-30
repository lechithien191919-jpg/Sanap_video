import os
import re
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
        body { background: #090d16; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 15px; }
        .container { background: #131c2e; padding: 25px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.6); width: 100%; max-width: 450px; text-align: center; border: 1px solid #1e293b; }
        
        .logo-area h1 { font-size: 24px; color: #38bdf8; font-weight: 800; letter-spacing: 0.5px; margin-bottom: 4px; }
        .logo-area p { font-size: 12px; color: #94a3b8; margin-bottom: 20px; }

        /* Menu chọn định dạng VIP */
        .menu-grid { display: flex; gap: 10px; margin-bottom: 15px; }
        .menu-btn { flex: 1; padding: 12px 10px; background: #1e293b; border: 2px solid #334155; border-radius: 12px; color: #94a3b8; font-size: 13px; font-weight: 600; cursor: pointer; transition: 0.2s; text-align: center; }
        .menu-btn.active { background: rgba(56, 189, 248, 0.1); border-color: #38bdf8; color: #38bdf8; box-shadow: 0 0 12px rgba(56, 189, 248, 0.2); }

        .input-group { margin-bottom: 15px; text-align: left; }
        label { display: block; font-size: 12px; margin-bottom: 6px; color: #cbd5e1; font-weight: 500; }
        input[type="text"] { width: 100%; padding: 13px; border-radius: 10px; border: 1px solid #334155; background: #090d16; color: #fff; font-size: 14px; outline: none; transition: 0.2s; }
        input[type="text"]:focus { border-color: #38bdf8; box-shadow: 0 0 8px rgba(56, 189, 248, 0.3); }
        
        .btn-submit { width: 100%; padding: 14px; background: linear-gradient(135deg, #0ea5e9, #2563eb); border: none; border-radius: 10px; color: white; font-size: 15px; font-weight: 700; cursor: pointer; transition: 0.2s; box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4); margin-top: 5px; }
        .btn-submit:hover { opacity: 0.95; transform: translateY(-1px); }

        /* Khung hiển thị tiến trình chi tiết */
        .progress-box { margin-top: 20px; background: #090d16; padding: 15px; border-radius: 12px; border: 1px solid #1e293b; text-align: left; display: none; }
        .progress-step { font-size: 12px; color: #38bdf8; margin-bottom: 8px; font-weight: 600; display: flex; align-items: center; gap: 8px; }
        .media-info { font-size: 11px; color: #cbd5e1; margin-top: 6px; word-break: break-all; border-top: 1px dashed #1e293b; padding-top: 8px; }
        
        .footer { margin-top: 20px; font-size: 11px; color: #64748b; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo-area">
            <h1>✨ SANAP VIP ✨</h1>
            <p>Bóc tách video TikTok không logo & tên chuẩn nội dung</p>
        </div>

        <div class="input-group">
            <label>👉 Dán Link TikTok vào đây:</label>
            <input type="text" id="url" placeholder="https://www.tiktok.com/@...">
        </div>

        <div class="input-group">
            <label>👉 Chọn định dạng muốn tải:</label>
            <div class="menu-grid">
                <div class="menu-btn active" id="btn-mp4" onclick="selectType('mp4')">🎬 Video MP4<br><span style="font-size:10px; opacity:0.7;">Không logo id</span></div>
                <div class="menu-btn" id="btn-mp3" onclick="selectType('mp3')">🎵 Nhạc MP3<br><span style="font-size:10px; opacity:0.7;">Audio gốc</span></div>
            </div>
        </div>

        <button class="btn-submit" onclick="processSanap()">🚀 BẮT ĐẦU TẢI NGAY</button>
        
        <!-- Khung hiển thị tiến trình -->
        <div class="progress-box" id="progressBox">
            <div class="progress-step" id="stepText">⏳ Đang khởi tạo hệ thống...</div>
            <div class="media-info" id="mediaDetails"></div>
        </div>

        <div class="footer">Created by ThienVN • Sanap Pro Ultimate Edition</div>
    </div>

    <script>
        let currentType = 'mp4';

        function selectType(type) {
            currentType = type;
            if (type === 'mp4') {
                document.getElementById('btn-mp4').classList.add('active');
                document.getElementById('btn-mp3').classList.remove('active');
            } else {
                document.getElementById('btn-mp3').classList.add('active');
                document.getElementById('btn-mp4').classList.remove('active');
            }
        }

        async function processSanap() {
            let url = document.getElementById('url').value.trim();
            let progressBox = document.getElementById('progressBox');
            let stepText = document.getElementById('stepText');
            let mediaDetails = document.getElementById('mediaDetails');

            if (!url) {
                alert("Chưa nhập link kìa ông ơi!");
                return;
            }

            progressBox.style.display = 'block';
            
            // Bước 1: Đang kết nối
            stepText.innerHTML = "🔗 Bước 1/3: Đang kết nối trạm trung chuyển...";
            mediaDetails.innerHTML = "Đang xác thực đường dẫn TikTok...";

            try {
                let response = await fetch('/api/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url, type: currentType })
                });
                let data = await response.json();

                if (data.success) {
                    // Bước 2: Bóc tách thành công
                    stepText.innerHTML = "🔍 Bước 2/3: Đã bóc tách sạch logo ID!";
                    mediaDetails.innerHTML = `<b>Tác giả:</b> ${data.author}<br><b>Tên nội dung:</b> ${data.title}`;

                    setTimeout(() => {
                        // Bước 3: Tải file về máy với tên chuẩn theo nội dung
                        stepText.innerHTML = `📥 Bước 3/3: Đang tự động tải file "${data.filename}" về máy...`;
                        
                        let a = document.createElement('a');
                        a.href = data.download_url;
                        a.download = data.filename;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);

                        setTimeout(() => {
                            stepText.innerHTML = "🎉 Hoàn tất! Tên file đã được đặt theo tiêu đề video nhé ông ơi.";
                        }, 1500);

                    }, 1000);

                } else {
                    stepText.innerHTML = "❌ Lỗi xử lý!";
                    mediaDetails.innerHTML = data.message;
                }
            } catch (err) {
                stepText.innerHTML = "❌ Lỗi kết nối mạng!";
                mediaDetails.innerHTML = "Không thể kết nối đến máy chủ xử lý.";
            }
        }
    </script>
</body>
</html>
"""

def clean_filename(text):
    # Loại bỏ các ký tự hệ thống không cho phép đặt tên file
    cleaned = re.sub(r'[\\/*?:"<>|]', "", text)
    cleaned = cleaned.strip()
    if len(cleaned) > 60:
        cleaned = cleaned[:60]
    return cleaned if cleaned else "Sanap_Media"

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
            raw_title = video_info.get("title", "tiktok_media")
            
            # Xử lý làm sạch tiêu đề để làm tên file chuẩn nội dung
            safe_title = clean_filename(raw_title)

            # Phân tách chính xác định dạng MP4 hay MP3 theo yêu cầu người dùng bấm
            if file_type == 'mp3':
                download_url = video_info.get("music")
                filename = f"{safe_title}.mp3"
            else:
                download_url = video_info.get("hdplay") or video_info.get("play")
                filename = f"{safe_title}.mp4"

            if not download_url:
                return jsonify({'success': False, 'message': 'Không tìm thấy link tải từ máy chủ!'})

            return jsonify({
                'success': True,
                'author': author,
                'title': raw_title,
                'filename': filename,
                'download_url': download_url
            })
        else:
            return jsonify({'success': False, 'message': 'Link TikTok không hợp lệ hoặc đã bị xoá!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
            
