#!/usr/bin/python3
import sys
import json
import requests
import time
import os
import subprocess

BUFFER_TIME = 30
API_KEY = "**********"
TELEGRAM_BOT_TOKEN = "**********"
TELEGRAM_CHAT_ID = "**********"

# đường dẫn các file xử lý
BUFFER_FILE = "/var/ossec/logs/gemini_buffer.txt"
LOCK_FILE = "/var/ossec/logs/gemini_time.lock"
ERR_FILE = "/var/ossec/logs/gemini_error.log"
LOG_FILE = "/var/ossec/logs/gemini_alerts.log"

def log_error(msg):
    with open(ERR_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{time.ctime()}] {msg}\n")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        log_error(f"Lỗi gửi Telegram: {e}")

# hàm chạy ngầm
def process_and_send_background():
    # ngủ đúng 30 giây để hứng thêm các log khác nếu có
    time.sleep(BUFFER_TIME)
    
    current_time = int(time.time())
    processing_file = f"/var/ossec/logs/gemini_processing_{current_time}.txt"
    
    # tráo túi và xóa đồng hồ
    try:
        if os.path.exists(BUFFER_FILE):
            os.rename(BUFFER_FILE, processing_file)
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except Exception as e:
        log_error(f"Lỗi tráo file: {e}")
        return

    # gọi AI phân tích và báo cáo
    try:
        # nếu không có file processing thì thoát
        if not os.path.exists(processing_file):
            return
            
        with open(processing_file, "r", encoding="utf-8") as pf:
            batched_logs = pf.read()

        if not batched_logs.strip():
            return

        prompt_text = f"""Bạn là một chuyên gia phân tích an toàn thông tin (SOC Analyst) cấp cao. Dưới đây là khối sự kiện bảo mật được gom trong {BUFFER_TIME} giây qua:
{batched_logs}

Hãy phân tích khối dữ liệu này và trả về 1 báo cáo duy nhất theo định dạng dưới đây:

[Biểu tượng] **BÁO CÁO SỰ KIỆN HỆ THỐNG** [Biểu tượng]
- **Tên sự kiện:** [Xác định loại hành vi. 
  * LƯU Ý CHUYÊN MÔN ĐỂ PHÂN LOẠI:
    1. Bình thường/Lỗi thao tác: Nếu tổng số log liên quan đến "Failed password", "authentication failed" hoặc "PAM: User login failed" TRONG CÙNG 1 TÚI LÀ DƯỚI 10 LẦN -> TUYỆT ĐỐI CHỈ dán nhãn: "Lỗi gõ sai mật khẩu / Cảnh báo nhẹ". (Dùng biểu tượng 🟢). Giải thích là do cơ chế sshd/PAM của Linux tự nhân bản log.
    2. Dò quét mạng (Port Scan): Nếu log xuất hiện dồn dập các từ "Connection closed by...", "Did not receive identification string", "preauth" mà KHÔNG CÓ nỗ lực nhập sai mật khẩu -> Nhãn: "Dò quét dịch vụ mạng (Nmap/Scan)". (Dùng biểu tượng ⚠️ cho tiêu đề).
    3. Tấn công vét cạn (Brute Force): CHỈ KHI NÀO tổng số log "Failed password", "authentication failed" XUẤT HIỆN TỪ DỒN DẬP KHÁC THƯỜNG SO VỚI LỖI Ở CON NGƯỜI hoặc cảnh báo "brute force trying to get access" -> Nhãn: "Tấn công dò mật khẩu (Brute Force/Hydra)". (Dùng biểu tượng 🚨 cho tiêu đề).
]
- **Mức độ:** [Thấp / Trung bình / Cao / Nghiêm trọng]
- **Mục tiêu & Kẻ xâm nhập:** [IP nguồn là gì? Nhắm vào tài khoản nào (ví dụ: root)?]
- **Đánh giá ngữ cảnh:** [Tóm tắt ngắn gọn chuyện gì đang xảy ra trong {BUFFER_TIME}s qua. Trả lời rõ: Kẻ gian/Người dùng đã đăng nhập thành công vào hệ thống chưa?]
- **Đề xuất xử lý:** [Nếu bình thường: "Tiếp tục theo dõi / Bỏ qua". Nếu tấn công: Đề xuất lệnh Firewall để chặn IP].

Lưu ý: Trình bày Markdown sạch sẽ, đi thẳng vào vấn đề, không giải thích dài dòng.
"""
        url_ai = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={API_KEY}"
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": prompt_text}]}]}

        response = requests.post(url_ai, headers=headers, json=data, timeout=15)

        if response.status_code == 200:
            result_ai = response.json()
            if 'candidates' in result_ai:
                ai_text = result_ai['candidates'][0]['content']['parts'][0]['text']
                send_telegram(ai_text)

                with open(LOG_FILE, "a", encoding="utf-8") as logf:
                    logf.write(f"\n[+] BATCH {BUFFER_TIME}s\n{ai_text}\n{'='*50}\n")
        else:
            log_error(f"Lỗi Gemini: {response.text}")
            # Fallback: nếu hết quota, báo thẳng lên tele
            send_telegram(f"⚠️ **Wazuh Cảnh Báo  (AI Hết Quota)**\nĐang có đợt tấn công (Nhiều Alert trong {BUFFER_TIME}s). Vui lòng kiểm tra Dashboard Wazuh!")
            
    except Exception as e:
        log_error(f"Lỗi xử lý AI/Tele: {e}")
        send_telegram(f"⚠️ **Wazuh Cảnh Báo (Mất kết nối AI)**\nKhông thể gọi Gemini (Timeout/Lỗi mạng). Đang có tấn công trong {BUFFER_TIME}s qua. Vui lòng check Dashboard Wazuh khẩn cấp!")
    finally:
        # xóa cái túi đã phân tích xong cho sạch server
        if os.path.exists(processing_file):
            os.remove(processing_file)
            
def main():
    # nếu script tự gọi lại chính nó với tham số --send -> chạy ngầm
    if len(sys.argv) > 1 and sys.argv[1] == "--send":
        process_and_send_background()
        return

    # wazuh truyền log vào thông qua tham số sys.argv[1]
    if len(sys.argv) < 2:
        sys.exit(1)

    # đọc alert từ wazuh
    try:
        with open(sys.argv[1], 'r') as f:
            alert = json.load(f)
    except Exception as e:
        log_error(f"Lỗi đọc JSON: {e}")
        return

    rule_level = alert.get('rule', {}).get('level', 0)

    # chỉ gom alert từ lv5
    if rule_level < 5:
        return

    # trích xuất dữ liệu gọn nhẹ để cho vào túi chứa
    agent = alert.get('agent', {}).get('name', 'Unknown')
    srcip = alert.get('data', {}).get('srcip', 'N/A')
    dstuser = alert.get('data', {}).get('dstuser', 'N/A')
    desc = alert.get('rule', {}).get('description', '')

    # lấy giờ thực tế lúc log chui vào túi
    time_str = time.strftime("%H:%M:%S")
    log_line = f"- [{time_str}] [Level {rule_level}] Agent: {agent} | IP Nguồn: {srcip} | Mục tiêu: {dstuser} | Chi tiết: {desc}\n"

    # cho log vào túi chứa
    try:
        with open(BUFFER_FILE, "a", encoding="utf-8") as bf:
            bf.write(log_line)
    except Exception as e:
        log_error(f"Lỗi ghi buffer: {e}")
        return

    # nếu chưa có tiến trình ngầm nào chạy thì đánh dấu và kích hoạt 1 tiến trình ngầm duy nhất
    # kích hoạt 1 tiến trình ngầm duy nhất
    if not os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, "w") as lf:
                lf.write("running")
            subprocess.Popen([sys.executable, sys.argv[0], "--send"], 
                             start_new_session=True, 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
        except Exception as e:
            log_error(f"Lỗi tạo tiến trình ngầm: {e}")

if __name__ == "__main__":
    main()
