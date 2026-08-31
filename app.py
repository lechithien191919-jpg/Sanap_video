import os
import random
import requests
from flask import Flask, render_template, request, session, redirect, url_for
import psycopg2

app = Flask(__name__)
app.secret_key = 'sanap_secret_key_super_secure'

# Đã gắn kết nối Neon Database chính xác của ông vào đây rồi nhé!
DATABASE_URL = "postgresql://neondb_owner:npg_aVetujfAE0v3@ep-weathered-pine-axxluidk-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print("Lỗi kết nối Neon DB: ", e)
        return None

def get_total_downloads():
    conn = get_db_connection()
    if not conn:
        return 0
    cur = conn.cursor()
    cur.execute("SELECT total_downloads FROM stats WHERE id = 1;")
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else 0

def increment_downloads():
    conn = get_db_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("UPDATE stats SET total_downloads = total_downloads + 1 WHERE id = 1;")
    conn.commit()
    cur.close()
    conn.close()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SANAP VIP - Ultimate Edition</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: #0f0d16; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 15px; }
        .container { background: #131c2d; width: 100%; max-width: 450px; padding: 25px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.5); border: 1px solid #1e293b; text-align: center; }
        .logo-area h1 { font-size: 22px; color: #38bdf8; font-weight: 800; letter-spacing: 0.5px; margin-bottom: 4px; }
        .logo-area p { font-size: 11px; color: #94a3b8; margin-bottom: 15px; }
        .menu-grid { display: flex; gap: 10px; margin-bottom: 15px; }
        .menu-btn { flex: 1; padding: 12px 10px; background: #1e293b; border: 2px solid #334155; border-radius: 10px; color: #94a3b8; font-size: 13px; font-weight: 600; cursor: pointer; transition: 0.2s; text-align: center; }
        .menu-btn.active { background: rgba(56, 189, 248, 0.1); border-color: #38bdf8; color: #38bdf8; box-shadow: 0 0 12px rgba(56, 189, 248, 0.2); }
        .input-group { margin-bottom: 12px; text-align: left; }
        .input-group label { display: block; font-size: 12px; margin-bottom: 5px; color: #cbd5e1; font-weight: 500; }
        .input-group input[type="text"] { width: 100%; padding: 12px; border-radius: 10px; border: 1px solid #334155; background: #090d16; color: #fff; font-size: 14px; outline: none; transition: 0.2s; }
        .input-group input[type="text"]:focus { border-color: #38bdf8; box-shadow: 0 0 8px rgba(56, 189, 248, 0.3); }
        .btn-submit { width: 100%; padding: 14px; background: linear-gradient(135deg, #0ea5e9, #2563eb); border: none; border-radius: 10px; color: white; font-size: 15px; font-weight: 700; cursor: pointer; transition: 0.2s; box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4); margin-top: 5px; }
        .btn-submit:hover { opacity: 0.95; transform: translateY(-1px); }
        .progress-box { margin-top: 20px; background: #090d16; padding: 15px; border-radius: 12px; border: 1px solid #1e293b; text-align: left; display: none; }
        .progress-step { font-size: 12px; color: #38bdf8; margin-bottom: 6px; font-weight: 600; display: flex; align-items: center; gap: 8px; }
        .media-info { font-size: 11px; color: #cbd5e1; margin-top: 6px; word-break: break-all; border-top: 1px dashed #1e293b; padding-top: 6px; }
        .stats-link { display: block; margin-top: 15px; padding: 10px; background: #1e293b; border-radius: 8px; font-size: 12px; color: #38bdf8; font-weight: 600; text-decoration: none; border: 1px dashed #334155; transition: 0.2s; }
        .stats-link:hover { background: #334155; }
        .footer { margin-top: 15px; font-size: 11px; color: #64748b; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo-area">
            <h1>✨ SANAP MULTI VIP ✨</h1>
            <p>Tải đa nền tảng & Đổi tên file tùy ý</p>
        </div>

        <div class="input-group">
            <label>🔗 Dán liên kết video:</label>
            <input type="text" id="url" placeholder="https://...">
        </div>

        <div class="input-group">
            <label>✏️ Tên file muốn lưu:</label>
            <input type="text" id="customName" value="sanap_video" placeholder="Nhập tên tuỳ ý...">
        </div>

        <div class="input-group">
            <label>⭐ Chọn định dạng:</label>
        </div>
        <div class="menu-grid">
            <div class="menu-btn active" id="btn-mp4" onclick="selectType('mp4')">🎬 Video MP4</div>
            <div class="menu-btn" id="btn-mp3" onclick="selectType('mp3')">🎵 Nhạc MP3</div>
        </div>

        <button class="btn-submit" onclick="processSanap()">🚀 BẮT ĐẦU TẢI NGAY</button>

        <div class="progress-box" id="progressBox">
            <div class="progress-step" id="stepText">⏳ Đang khởi tạo...</div>
            <div class="media-info" id="mediaDetails"></div>
        </div>

        <a href="/admin/stats" class="stats-link">📊 Xem Thống Kê Toàn Cầu (Yêu cầu mật khẩu)</a>
        <div class="footer">Created by ThienVN • Sanap Pro Ultimate</div>
    </div>

    <script>
        let currentType = 'mp4';

        function selectType(type) {
            currentType = type;
            document.getElementById('btn-mp4').classList.remove('active');
            document.getElementById('btn-mp3').classList.remove('active');
            document.getElementById('btn-' + type).classList.add('active');
        }

        async function processSanap() {
            let url = document.getElementById('url').value.trim();
            let customName = document.getElementById('customName').value.trim() || 'sanap_file';
            let progressBox = document.getElementById('progressBox');
            let stepText = document.getElementById('stepText');
            let mediaDetails = document.getElementById('mediaDetails');

            if (!url) {
                alert("Ông chưa nhập link kìa!");
                return;
            }

            progressBox.style.display = 'block';
            stepText.innerHTML = "⏳ Bước 1/3: Đang kết nối máy chủ...";
            mediaDetails.innerHTML = "Đang xử lý yêu cầu tải xuống...";

            try {
                let response = await fetch('/api/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url, type: currentType, custom_name: customName })
                });
                let data = await response.json();

                if (data.success) {
                    stepText.innerHTML = "✅ Bước 2/3: Lấy dữ liệu thành công!";
                    mediaDetails.innerHTML = "<b>Nền tảng:</b> " + data.platform + "<br><b>Tiêu đề:</b> " + data.title;

                    setTimeout(() => {
                        stepText.innerHTML = "📥 Bước 3/3: Đang tải file về máy...";
                        let a = document.createElement('a');
                        a.href = data.download_url;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);

                        setTimeout(() => {
                            stepText.innerHTML = "🎉 Hoàn tất thành công!";
                        }, 1500);
                    }, 1000);
                } else {
                    stepText.innerHTML = "❌ Lỗi kết nối!";
                    mediaDetails.innerHTML = "Không thể kết nối đến máy chủ.";
                }
            } catch (err) {
                stepText.innerHTML = "❌ Lỗi kết nối mạng!";
                mediaDetails.innerHTML = "Không thể kết nối đến máy chủ.";
            }
        }
    </script>
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Xác Thực Mật Khẩu - Thống Kê Sanap</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: #0f0d16; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 15px; }
        .login-box { background: #131c2d; width: 100%; max-width: 380px; padding: 25px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.5); border: 1px solid #1e293b; text-align: center; }
        h2 { color: #38bdf8; font-size: 20px; margin-bottom: 15px; }
        input[type="password"] { width: 100%; padding: 12px; border-radius: 10px; border: 1px solid #334155; background: #090d16; color: #fff; font-size: 14px; outline: none; margin-bottom: 15px; }
        button { width: 100%; padding: 12px; background: linear-gradient(135deg, #0ea5e9, #2563eb); border: none; border-radius: 10px; color: white; font-size: 14px; font-weight: 700; cursor: pointer; }
        .error { color: #f87171; font-size: 12px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>🔒 Bảo Mật Quản Trị</h2>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST">
            <input type="password" name="password" placeholder="Nhập mật khẩu quản trị..." required>
            <button type="submit">Xác Nhận</button>
        </form>
    </div>
</body>
</html>
"""

STATS_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Thống Kê Tải Xuống - Sanap</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: #0f0d16; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 15px; }
        .stats-box { background: #131c2d; width: 100%; max-width: 400px; padding: 30px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.5); border: 1px solid #1e293b; text-align: center; }
        h1 { color: #38bdf8; font-size: 22px; margin-bottom: 20px; }
        .number { font-size: 48px; font-weight: 800; color: #34d399; margin: 15px 0; text-shadow: 0 0 20px rgba(52, 211, 153, 0.3); }
        .back-btn { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #1e293b; color: #38bdf8; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 13px; border: 1px solid #334155; }
    </style>
</head>
<body>
    <div class="stats-box">
        <h1>📊 Tổng Lượt Tải Toàn Cầu</h1>
        <div class="number">{{ total_downloads }}</div>
        <p style="color: #94a3b8; font-size: 13px;">Lượt tải thành công qua hệ thống Sanap VIP</p>
        <a href="/" class="back-btn">⬅ Quay lại trang chủ</a>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/admin/stats', methods=['GET', 'POST'])
def admin_stats():
    error = None
    if not session.get('is_admin'):
        if request.method == 'POST':
            if request.form.get('password') == 'Thien191919': # Mật khẩu quản trị của ông
                session['is_admin'] = True
                return redirect(url_for('admin_stats'))
            else:
                error = "Mật khẩu không chính xác!"
        return render_template_string(LOGIN_TEMPLATE, error=error)

    total_downloads = get_total_downloads()
    return render_template_string(STATS_TEMPLATE, total_downloads=total_downloads)

@app.route('/api/download', methods=['POST'])
def api_download():
    req_data = request.json
    url = req_data.get('url')
    file_type = req_data.get('type')

    custom_name = req_data.get('custom_name', 'sanap_file')
    custom_name = "".join(c for c in custom_name if c.isalnum() or c in (' ', '_', '-')).strip()
    if not custom_name:
        custom_name = "sanap_file"

    headers = {
        'Accept': 'application/json',
    }

    # API Tải video ngầm qua Cobalt/Picker (giữ nguyên logic gốc chuẩn của ông)
    try:
        cobalt_res = requests.post('https://co.wuk.sh/api/json', json={
            'url': url,
            'isAudioOnly': True if file_type == 'mp3' else False
        }, headers=headers)
        res_data = cobalt_res.json()

        status = res_data.get('status')
        download_url = ""

        if status == 'redirect' or status == 'tunnel':
            download_url = res_data.get('url')
        elif status == 'picker' and res_data.get('picker'):
            download_url = res_data.get('picker')[0].get('url')

        if not download_url:
            return jsonify({'success': False, 'message': 'Không tìm thấy liên kết tải trực tiếp!'})

        increment_downloads()

        return jsonify({
            'success': True,
            'platform': res_data.get('picker', [{}])[0].get('type', 'Video / Audio'),
            'title': res_data.get('filename', f'{custom_name}'),
            'download_url': download_url
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
