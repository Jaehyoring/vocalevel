"""
VocaLevel — Flask 백엔드
  POST /api/analyze  → 형태소 분석 + 레벨 매핑
  GET  /             → 프론트엔드 index.html
  GET  /api/health   → 헬스 체크
"""
import os, sys

# 프로젝트 루트를 Python 경로에 추가
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'src', 'backend'))

from flask import Flask, request, jsonify, send_from_directory
from analyzer import detect_language, analyze_ja, analyze_ko

FRONTEND = os.path.join(ROOT, 'src', 'frontend')

app = Flask(__name__, static_folder=FRONTEND)

# ── 레벨 정렬 순서 ────────────────────────────────────────────────
JP_ORDER = ['N5', 'N4', 'N3', 'N2', 'N1']
KR_ORDER = ['1급', '2급', '3급', '4급', '5급', '6급']

def _stats(tokens: list[dict], lang: str) -> dict:
    """토큰 목록으로 통계 생성"""
    order  = JP_ORDER if lang == 'ja' else KR_ORDER
    counts: dict[str, int] = {}
    for t in tokens:
        lv = t['level']
        counts[lv] = counts.get(lv, 0) + 1

    content  = [t for t in tokens if not t['is_grammar']]
    in_list  = [t for t in content  if t['in_list']]
    lv_found = [t['level'] for t in in_list if t['level'] in order]
    max_lv   = max(lv_found, key=lambda lv: order.index(lv)) if lv_found else '—'

    return {
        'total':        len(tokens),
        'content_words': len(content),
        'in_list':      len(in_list),
        'by_level':     counts,
        'max_level':    max_lv,
    }

# ── 라우트 ────────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory(FRONTEND, 'index.html')

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'version': '1.0.0'})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json(force=True, silent=True) or {}
    text = (data.get('text') or '').strip()
    lang = (data.get('lang') or 'auto').strip()

    if not text:
        return jsonify({'error': '텍스트를 입력해주세요.'}), 400

    # 언어 결정
    if lang == 'auto':
        detected = detect_language(text)
    elif lang in ('ja', 'jp'):
        detected = 'ja'
    elif lang in ('ko', 'kr'):
        detected = 'ko'
    else:
        detected = detect_language(text)

    if detected not in ('ja', 'ko'):
        return jsonify({'error': '일본어 또는 한국어 텍스트를 입력해주세요.'}), 400

    # 형태소 분석
    tokens = analyze_ja(text) if detected == 'ja' else analyze_ko(text)

    return jsonify({
        'detected_lang': detected,
        'tokens':        tokens,
        'stats':         _stats(tokens, detected),
    })

# ── 실행 ──────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f'\n🚀 VocaLevel 서버 시작 → http://localhost:{port}\n')
    app.run(host='0.0.0.0', port=port, debug=False)
