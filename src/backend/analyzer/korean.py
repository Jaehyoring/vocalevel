"""
한국어 형태소 분석기
  - kiwipiepy (MeCab 의존성 없음, Docker 친화적)
  - TOPIK 레벨 매핑: TOPIC_level/topik_vocabulary_all_levels.csv
"""
import os
import csv
import re
from kiwipiepy import Kiwi

# ── 경로 설정 ──────────────────────────────────────────────────────
BASE      = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
TOPIK_CSV = os.path.join(BASE, 'TOPIC_level', 'topik_vocabulary_all_levels.csv')

# ── TOPIK 어휘 사전 로드 ───────────────────────────────────────────
_topik: dict[str, str] = {}

def _load_topik() -> None:
    with open(TOPIK_CSV, encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            word  = row.get('어휘', '').strip()
            level = row.get('레벨', '').strip()
            if not word or not level:
                continue
            _topik[word] = level
            # 동형이의어 번호 제거한 기본형도 등록 (가격02 → 가격)
            stripped = re.sub(r'\d+$', '', word)
            if stripped != word and stripped not in _topik:
                _topik[stripped] = level

_load_topik()

# ── Kiwi 초기화 ───────────────────────────────────────────────────
_kiwi = Kiwi()

# ── 품사 태그 분류 ────────────────────────────────────────────────
_GRAMMAR_TAGS = {
    'JKS', 'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ',
    'JX', 'JC',
    'EC', 'EF', 'EP', 'ETM', 'ETN',
    'XPN', 'XSN', 'XSV', 'XSA', 'XR',
    'SF', 'SP', 'SS', 'SE', 'SO', 'SW', 'SY', 'SB',
    'NF', 'NV', 'NA',
    'W_URL', 'W_EMAIL', 'W_HASHTAG', 'W_MENTION',
}

_POS_LABEL = {
    'NNG': '명사', 'NNP': '고유명사', 'NNB': '의존명사',
    'NP':  '대명사', 'NR': '수사',
    'VV':  '동사', 'VA': '형용사', 'VX': '보조용언',
    'VCP': '지정사', 'VCN': '지정사',
    'MAG': '부사', 'MAJ': '접속부사', 'MM': '관형사',
    'IC':  '감탄사',
    'JKS': '조사', 'JKC': '조사', 'JKG': '조사',
    'JKO': '조사', 'JKB': '조사', 'JKV': '조사',
    'JKQ': '조사', 'JX': '조사', 'JC': '조사',
    'EC': '어미', 'EF': '어미', 'EP': '어미',
    'ETM': '어미', 'ETN': '어미',
    'XPN': '접두사', 'XSN': '접미사', 'XSV': '접미사', 'XSA': '접미사',
    'SF': '기호', 'SP': '기호', 'SS': '기호',
    'SW': '기호', 'SY': '기호', 'SE': '기호',
    'SL': '외국어', 'SH': '한자', 'SN': '숫자',
}

_VERB_TAGS = {'VV', 'VA', 'VX', 'VCP', 'VCN'}

# ── 레벨 조회 ─────────────────────────────────────────────────────
def _lookup(surface: str, tag: str = '') -> tuple[str, bool]:
    candidates = [surface]
    if tag in _VERB_TAGS and not surface.endswith('다'):
        candidates.append(surface + '다')

    for key in candidates:
        if not key:
            continue
        if key in _topik:
            return _topik[key], True
        stripped = re.sub(r'\d+$', '', key)
        if stripped != key and stripped in _topik:
            return _topik[stripped], True
    return '미등재', False

# ── 메인 분석 함수 ────────────────────────────────────────────────
def analyze(text: str) -> list[dict]:
    tokens = []
    result = _kiwi.tokenize(text)

    for token in result:
        sf = token.form
        if not sf:
            continue

        # Tag enum → 문자열 변환
        tag_raw = token.tag
        tag = tag_raw.name if hasattr(tag_raw, 'name') else str(tag_raw)
        if '.' in tag:
            tag = tag.split('.')[-1]

        primary_tag = tag.split('+')[0]
        is_grammar  = primary_tag in _GRAMMAR_TAGS
        pos_label   = _POS_LABEL.get(primary_tag, primary_tag)

        # 기본형: 동사·형용사 어간에 '다' 추가
        if primary_tag in _VERB_TAGS and not sf.endswith('다'):
            base = sf + '다'
        else:
            base = sf

        if is_grammar:
            level, in_list = pos_label, False
        else:
            level, in_list = _lookup(sf, primary_tag)

        tokens.append({
            'surface':    sf,
            'reading':    '',
            'base_form':  base,
            'pos':        pos_label,
            'level':      level,
            'in_list':    in_list,
            'is_grammar': is_grammar,
        })

    return tokens
