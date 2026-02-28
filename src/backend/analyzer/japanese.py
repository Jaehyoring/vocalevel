"""
일본어 형태소 분석기
  - MeCab + unidic-cwj-202302 (로컬) 또는 unidic pip 패키지 (Docker)
  - JLPT 레벨 매핑: JLPT_level/JLPT-level_naver.csv

환경변수:
  JP_DIC_PATH : 일본어 사전 경로 (기본값: unidic pip → 로컬 경로 순으로 탐지)
  MECABRC     : mecabrc 경로 (기본값: 자동 탐지)
"""
import os
import csv
import re
import MeCab

# ── 경로 설정 ──────────────────────────────────────────────────────
BASE     = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
JLPT_CSV = os.path.join(BASE, 'JLPT_level', 'JLPT-level_naver.csv')

# 일본어 사전: 환경변수 → unidic pip 패키지 → 로컬 경로
_jp_dic_env = os.environ.get('JP_DIC_PATH', '')
if _jp_dic_env:
    DIC_PATH = _jp_dic_env
else:
    try:
        import unidic
        DIC_PATH = unidic.DICDIR
    except ImportError:
        DIC_PATH = os.path.join(BASE, 'unidic-cwj-202302')

# mecabrc: 환경변수 → macOS Homebrew → Linux 시스템
_mecabrc_env = os.environ.get('MECABRC', '')
if _mecabrc_env:
    MECABRC = _mecabrc_env
elif os.path.exists('/opt/homebrew/etc/mecabrc'):
    MECABRC = '/opt/homebrew/etc/mecabrc'
elif os.path.exists('/etc/mecabrc'):
    MECABRC = '/etc/mecabrc'
else:
    MECABRC = ''

# ── JLPT 어휘 사전 로드 ────────────────────────────────────────────
_jlpt_kanji: dict[str, str] = {}
_jlpt_hira:  dict[str, str] = {}

def _load_jlpt() -> None:
    with open(JLPT_CSV, encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            kanji = row.get('한자표기', '').strip()
            hira  = row.get('읽기(히라가나)', '').strip()
            level = row.get('JLPT레벨', '').strip()
            if not level or level == '外':
                continue
            if kanji:
                _jlpt_kanji[kanji] = level
            if hira:
                _jlpt_hira[hira] = level

_load_jlpt()

# ── 카타카나 → 히라가나 변환 ──────────────────────────────────────
def _kata2hira(text: str) -> str:
    return ''.join(
        chr(ord(c) - 0x60) if '\u30A1' <= c <= '\u30F6' else c
        for c in text
    )

# ── MeCab Tagger 초기화 ────────────────────────────────────────────
def _init_tagger() -> MeCab.Tagger:
    dic = DIC_PATH
    # 경로에 공백이 있으면 심볼릭 링크로 우회 (macOS 개발환경)
    if ' ' in dic:
        symlink = '/tmp/vocalevel_jp'
        if not os.path.lexists(symlink):
            os.symlink(os.path.dirname(dic), symlink)
        dic = f'{symlink}/{os.path.basename(dic)}'
    args = f'-d {dic}'
    if MECABRC:
        args = f'-r {MECABRC} ' + args
    return MeCab.Tagger(args)

_tagger = _init_tagger()

# ── 문법어 판별 ────────────────────────────────────────────────────
_GRAMMAR_POS = {'助詞', '助動詞', '接続詞', '感動詞', '記号', '補助記号', '空白'}

# ── 레벨 조회 ─────────────────────────────────────────────────────
def _lookup(surface: str, base_kanji: str, lemma_kanji: str, reading_kata: str) -> tuple[str, bool]:
    reading_hira = _kata2hira(reading_kata)
    for key in [base_kanji, lemma_kanji, surface]:
        if key and key in _jlpt_kanji:
            return _jlpt_kanji[key], True
    for key in [reading_hira, _kata2hira(lemma_kanji)]:
        if key and key in _jlpt_hira:
            return _jlpt_hira[key], True
    return '未登録', False

# ── 메인 분석 함수 ─────────────────────────────────────────────────
def analyze(text: str) -> list[dict]:
    tokens = []
    node = _tagger.parseToNode(text)
    while node:
        sf = node.surface
        if not sf:
            node = node.next
            continue

        feats = node.feature.split(',')
        pos          = feats[0]  if len(feats) > 0  else ''
        reading_kata = feats[6]  if len(feats) > 6  else ''
        lemma_kanji  = feats[7]  if len(feats) > 7  else ''
        base_kanji   = feats[10] if len(feats) > 10 else ''

        is_grammar = pos in _GRAMMAR_POS

        pos_label = {
            '名詞': '명사', '動詞': '동사', '形容詞': '형용사',
            '副詞': '부사', '助詞': '조사', '助動詞': '조동사',
            '接続詞': '접속사', '感動詞': '감탄사', '記号': '기호',
            '補助記号': '기호', '接尾辞': '접미사', '接頭辞': '접두사',
        }.get(pos, pos)

        if is_grammar:
            level, in_list = pos_label, False
        else:
            level, in_list = _lookup(sf, base_kanji, lemma_kanji, reading_kata)

        reading_hira = _kata2hira(reading_kata) if reading_kata not in ('*', '') else ''

        tokens.append({
            'surface':    sf,
            'reading':    reading_hira,
            'base_form':  base_kanji if base_kanji not in ('*', '') else sf,
            'pos':        pos_label,
            'level':      level,
            'in_list':    in_list,
            'is_grammar': is_grammar,
        })
        node = node.next

    return tokens
