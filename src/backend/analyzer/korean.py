"""
한국어 형태소 분석기
  - MeCab + mecab-ko-dic
  - TOPIK 레벨 매핑: TOPIC_level/topik_vocabulary_all_levels.csv

환경변수:
  KR_DIC_PATH : 한국어 사전 경로 (기본값: 로컬 mecab-ko-dic/)
  KR_MECABRC  : 한국어 mecabrc 경로 (기본값: MECABRC 환경변수 사용)
  MECABRC     : 공용 mecabrc 경로 (기본값: 자동 탐지)
"""
import os
import csv
import re
import MeCab

# ── 경로 설정 ──────────────────────────────────────────────────────
BASE      = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
TOPIK_CSV = os.path.join(BASE, 'TOPIC_level', 'topik_vocabulary_all_levels.csv')

# 한국어 사전: 환경변수 → 로컬 경로
_kr_dic_env = os.environ.get('KR_DIC_PATH', '')
DIC_PATH = _kr_dic_env if _kr_dic_env else os.path.join(BASE, 'mecab-ko-dic')

# mecabrc: KR_MECABRC → MECABRC → 자동 탐지
_mecabrc_env = os.environ.get('KR_MECABRC', os.environ.get('MECABRC', ''))
if _mecabrc_env:
    MECABRC = _mecabrc_env
elif os.path.exists('/opt/homebrew/etc/mecabrc'):
    MECABRC = '/opt/homebrew/etc/mecabrc'
elif os.path.exists('/etc/mecabrc'):
    MECABRC = '/etc/mecabrc'
else:
    MECABRC = ''

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

# ── MeCab Tagger 초기화 ───────────────────────────────────────────
def _init_tagger() -> MeCab.Tagger:
    dic = DIC_PATH
    # 경로에 공백이 있으면 심볼릭 링크로 우회 (macOS 개발환경)
    if ' ' in dic:
        symlink = '/tmp/vocalevel_kr'
        if not os.path.lexists(symlink):
            os.symlink(os.path.dirname(dic), symlink)
        dic = f'{symlink}/{os.path.basename(dic)}'
    args = f'-d {dic}'
    if MECABRC:
        args = f'-r {MECABRC} ' + args
    return MeCab.Tagger(args)

_tagger = _init_tagger()

# ── 품사 태그 분류 ────────────────────────────────────────────────
_GRAMMAR_TAGS = {
    'JKS', 'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ',
    'JX', 'JC',
    'EC', 'EF', 'EP', 'ETM', 'ETN',
    'XPN', 'XSN', 'XSV', 'XSA', 'XR',
    'SF', 'SP', 'SS', 'SE', 'SO', 'SW', 'SY',
    'NF', 'NV', 'NA',
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

# ── 레벨 조회 ─────────────────────────────────────────────────────
def _lookup(surface: str, base: str, tag: str = '') -> tuple[str, bool]:
    verb_tags = {'VV', 'VA', 'VX', 'VCP', 'VCN'}
    candidates = [base, surface]
    if tag in verb_tags and base and not base.endswith('다'):
        candidates.append(base + '다')
    if tag in verb_tags and surface and not surface.endswith('다'):
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
    node = _tagger.parseToNode(text)
    while node:
        sf = node.surface
        if not sf:
            node = node.next
            continue

        feats = node.feature.split(',')
        tag  = feats[0]
        base = feats[3] if len(feats) > 3 else sf

        primary_tag = tag.split('+')[0]
        is_grammar  = primary_tag in _GRAMMAR_TAGS
        pos_label   = _POS_LABEL.get(primary_tag, primary_tag)

        if is_grammar:
            level, in_list = pos_label, False
        else:
            level, in_list = _lookup(sf, base, primary_tag)

        tokens.append({
            'surface':    sf,
            'reading':    '',
            'base_form':  base if base not in ('*', '') else sf,
            'pos':        pos_label,
            'level':      level,
            'in_list':    in_list,
            'is_grammar': is_grammar,
        })
        node = node.next

    return tokens
