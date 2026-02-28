"""
VocaLevel 데스크톱 런처
  - Flask 서버를 백그라운드 스레드로 시작
  - 서버가 준비되면 기본 브라우저를 자동으로 엽니다
  - macOS / Windows 모두 지원
"""
import os
import sys
import time
import threading
import webbrowser
import urllib.request

PORT = 5000
URL  = f'http://localhost:{PORT}'

# 프로젝트 루트
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'src', 'backend'))


def _wait_and_open() -> None:
    """서버가 응답할 때까지 기다렸다가 브라우저를 엽니다."""
    for _ in range(30):  # 최대 15초 대기
        time.sleep(0.5)
        try:
            urllib.request.urlopen(f'{URL}/api/health', timeout=1)
            break
        except Exception:
            pass
    webbrowser.open(URL)


def main() -> None:
    print('─' * 48)
    print('  📚 VocaLevel 시작 중...')
    print(f'  접속 주소: {URL}')
    print('  브라우저가 자동으로 열립니다.')
    print('  종료하려면 Ctrl+C 를 누르세요.')
    print('─' * 48)

    # 브라우저 오픈을 별도 스레드에서 실행
    t = threading.Thread(target=_wait_and_open, daemon=True)
    t.start()

    # Flask 서버 시작 (메인 스레드)
    from app import app
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)


if __name__ == '__main__':
    main()
