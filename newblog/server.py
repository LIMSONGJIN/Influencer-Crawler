#!/usr/bin/env python3
"""
BlogCraft Pro Local Server
간단한 Python HTTP 서버 for 로컬 테스트
"""

import http.server
import socketserver
import os
import webbrowser
from datetime import datetime

PORT = 8000
HOST = "localhost"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # CORS 헤더 추가 (API 테스트용)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()
    
    def log_message(self, format, *args):
        """로그 메시지 커스터마이징"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def start_server():
    """서버 시작"""
    # 현재 디렉토리 확인
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    print(f"""
    ╔════════════════════════════════════════════════╗
    ║         BlogCraft Pro - Local Server           ║
    ╠════════════════════════════════════════════════╣
    ║  서버 시작됨: http://{HOST}:{PORT}             ║
    ║  종료하려면: Ctrl+C를 누르세요                 ║
    ╚════════════════════════════════════════════════╝
    
    📁 서빙 디렉토리: {current_dir}
    
    🔗 주요 페이지:
    ├── http://{HOST}:{PORT}/index-saas.html     (메인 홈)
    ├── http://{HOST}:{PORT}/saas-login.html     (로그인)
    ├── http://{HOST}:{PORT}/index.html          (블로그 작성)
    ├── http://{HOST}:{PORT}/saas-dashboard.html (대시보드)
    └── http://{HOST}:{PORT}/saas-pricing.html   (요금제)
    
    🌟 브라우저가 자동으로 열립니다...
    """)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        try:
            # 브라우저 자동 열기
            webbrowser.open(f'http://{HOST}:{PORT}/index-saas.html')
            print(f"✅ 서버가 포트 {PORT}에서 실행 중입니다...")
            print("─" * 50)
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 서버를 종료합니다...")
            httpd.shutdown()
            print("👋 안녕히 가세요!")

if __name__ == "__main__":
    try:
        start_server()
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"""
    ❌ 오류: 포트 {PORT}가 이미 사용 중입니다.
    
    해결 방법:
    1. 다른 프로그램이 포트를 사용 중인지 확인
    2. 또는 아래 명령어로 기존 프로세스 종료:
       Windows: netstat -ano | findstr :{PORT}
                taskkill /PID [PID번호] /F
    """)
        else:
            print(f"❌ 서버 시작 실패: {e}")
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")