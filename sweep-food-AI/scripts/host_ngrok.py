"""Host SweepFood Web Mockup & Smart Input OCR API via ngrok tunnel.

Usage:
------
1. Ensure the web server is running on port 8000:
   C:/Users/HUYPNG/miniconda3/envs/ocr_env/python.exe -m uvicorn web.app:app --port 8000

2. Run this script:
   C:/Users/HUYPNG/miniconda3/envs/ocr_env/python.exe scripts/host_ngrok.py

If you haven't set your ngrok authtoken yet:
- Get your free token at: https://dashboard.ngrok.com/get-started/your-authtoken
- Add it to .env: NGROK_AUTHTOKEN="your_token_here"
  OR run: ngrok config add-authtoken your_token_here
"""

from __future__ import annotations

import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

PORT = int(os.environ.get("PORT", 8000))
NGROK_TOKEN = os.environ.get("NGROK_AUTHTOKEN")


def check_local_server(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/system/status", timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def main():
    print("=" * 70)
    print("      SWEEPFOOD AI — NGROK PUBLIC HOSTING CONTROLLER")
    print("=" * 70)

    # 1. Verify local server is running
    print(f"\n[1/3] Checking local SweepFood server on port {PORT}...")
    if not check_local_server(PORT):
        print(f"  [!] WARNING: Local server on http://127.0.0.1:{PORT} is not responding!")
        print(f"      Please start it in another terminal first:")
        print(f"      C:/Users/HUYPNG/miniconda3/envs/ocr_env/python.exe -m uvicorn web.app:app --host 127.0.0.1 --port {PORT}")
        print("      Continuing anyway (tunnel will connect once server starts)...")
    else:
        print(f"  [OK] Local server is healthy and responding on http://127.0.0.1:{PORT}")

    # 2. Setup ngrok
    from pyngrok import ngrok, conf

    if NGROK_TOKEN:
        print(f"\n[2/3] Configuring ngrok authtoken from .env ({NGROK_TOKEN[:8]}...)...")
        ngrok.set_auth_token(NGROK_TOKEN)
    else:
        # Check if authtoken already exists in default ngrok config
        config_path = conf.get_default().config_path or os.path.expanduser(r"~\AppData\Local\ngrok\ngrok.yml")
        has_token_in_config = False
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "authtoken:" in content and not content.strip().endswith("authtoken:"):
                        has_token_in_config = True
            except Exception:
                has_token_in_config = False
        if not has_token_in_config:
            print("\n[!] CHƯA CẤU HÌNH NGROK AUTHTOKEN:")
            print("    Ngrok yêu cầu authtoken (miễn phí 100%) để mở đường hầm công khai.")
            print("    1. Đăng ký/đăng nhập miễn phí tại: https://dashboard.ngrok.com/signup")
            print("    2. Lấy token tại: https://dashboard.ngrok.com/get-started/your-authtoken")
            print("    3. Thêm vào file .env:")
            try:
                token_input = input("Nhập NGROK_AUTHTOKEN của bạn ngay tại đây (hoặc nhấn Enter để thử tiếp): ").strip()
            except (EOFError, KeyboardInterrupt):
                token_input = ""
            if token_input:
                ngrok.set_auth_token(token_input)
                # save to .env
                env_file = ROOT / ".env"
                with open(env_file, "a", encoding="utf-8") as f:
                    f.write(f'\nNGROK_AUTHTOKEN="{token_input}"\n')
                print("  [OK] Đã lưu NGROK_AUTHTOKEN vào file .env!")

    # 3. Establish public tunnel
    print(f"\n[3/3] Opening public HTTPS tunnel to http://127.0.0.1:{PORT}...")
    try:
        tunnel = ngrok.connect(PORT, "http")
        public_url = tunnel.public_url.replace("http://", "https://")

        print("\n" + "=" * 70)
        print("   🎉 NGROK TUNNEL ONLINE! CÁC ENDPOINT CÔNG KHAI:")
        print("=" * 70)
        print(f"  🌐 Web Mockup UI         : {public_url}/")
        print(f"  🧾 Smart Input OCR API   : {public_url}/api/smart-input/ocr-upload")
        print(f"  🎙️ Smart Input ASR API   : {public_url}/api/smart-input/asr-upload")
        print(f"  🥗 Recommendation API    : {public_url}/api/recommend")
        print(f"  ⚡ System & GPU Status   : {public_url}/api/system/status")
        print("=" * 70)
        print("\nVí dụ test OCR bằng cURL (upload ảnh hóa đơn/tem cân):")
        print(f'curl -X POST "{public_url}/api/smart-input/ocr-upload" -F "file=@scratch/hoadon.webp"')
        print("\nNhấn CTRL+C để dừng tunnel...")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nĐang đóng ngrok tunnel...")
        ngrok.kill()
        print("Ngrok tunnel đã dừng an toàn.")
    except Exception as e:
        print(f"\n[!] Lỗi khởi động ngrok: {e}")
        if "ERR_NGROK_4018" in str(e) or "authentication failed" in str(e).lower():
            print("Nguyên nhân: Authtoken chưa được khai báo hoặc không hợp lệ.")
            print("Vui lòng lấy token tại: https://dashboard.ngrok.com/get-started/your-authtoken")


if __name__ == "__main__":
    main()
