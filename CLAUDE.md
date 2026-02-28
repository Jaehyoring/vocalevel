# CLAUDE.md — VocaLevel プロジェクト

> 일본어·한국어 어휘 레벨 분석기 (JLPT & TOPIK 기준)
> Claude Code가 이 프로젝트를 이해하고 작업하기 위한 가이드

---

## 프로젝트 개요

일본어 또는 한국어 텍스트를 입력하면 **MeCab 형태소 분석**으로 단어를 분해하고,
JLPT(N5~N1) / TOPIK(1~6급) 어휘 목록과 대조해 각 단어의 레벨을 색상으로 시각화하는 앱.

- **웹 버전**: Flask 서버 → 브라우저 접속 (`http://localhost:5001`)
- **데스크톱 버전**: `desktop/launcher.py` — Flask 서버 시작 후 기본 브라우저 자동 오픈

---

## 현재 상태 (2026-02-28)

| 항목 | 상태 |
|------|------|
| PRD 문서 | ✅ `PRD.md` 완성 |
| JLPT 어휘 CSV | ✅ `JLPT_level/JLPT-level_naver.csv` (6,822어) |
| TOPIK 어휘 CSV | ✅ `TOPIC_level/topik_vocabulary_all_levels.csv` (10,636어) |
| MeCab 일본어 사전 | ✅ `unidic-cwj-202302/` (컴파일 완료) |
| MeCab 한국어 사전 | ✅ `mecab-ko-dic/` (컴파일 완료) |
| Flask 백엔드 API | ✅ `src/backend/app.py` — `POST /api/analyze` 구현 완료 |
| 일본어 분석기 | ✅ `src/backend/analyzer/japanese.py` — MeCab + unidic-cwj-202302 |
| 한국어 분석기 | ✅ `src/backend/analyzer/korean.py` — MeCab + mecab-ko-dic |
| 언어 자동 감지 | ✅ `src/backend/analyzer/detector.py` |
| 프론트엔드 → API 연동 | ✅ `src/frontend/index.html` — fetch API 완전 연동 |
| 데스크톱 런처 | ✅ `desktop/launcher.py` — 브라우저 자동 오픈 |
| Docker 배포 | 🔧 진행 중 |
| PyInstaller 패키징 | ❌ 미구현 |

---

## 디렉토리 구조

```
Japanese-Korean Vocabulary Learning Level Determiner/
│
├── CLAUDE.md                        ← 이 파일
├── PRD.md                           ← 제품 요구사항 문서
├── README.md                        ← 프로젝트 소개 및 실행 가이드
├── server.py                        ← 정적 파일 개발 서버 (포트 7654, 레거시)
│
├── src/
│   ├── frontend/
│   │   └── index.html               ← 메인 UI (Flask API 완전 연동)
│   └── backend/
│       ├── app.py                   ← Flask 앱 진입점 (포트 5001)
│       └── analyzer/
│           ├── __init__.py          ← detect_language, analyze_ja, analyze_ko 익스포트
│           ├── detector.py          ← 언어 자동 감지 (히라가나/한글 문자 비율)
│           ├── japanese.py          ← MeCab + unidic-cwj-202302 + JLPT 매핑
│           └── korean.py            ← MeCab + mecab-ko-dic + TOPIK 매핑
│
├── desktop/
│   └── launcher.py                  ← 데스크톱 런처 (Flask + 브라우저 자동 오픈)
│
├── JLPT_level/
│   └── JLPT-level_naver.csv         ← JLPT 어휘 DB (6,822어)
│
├── TOPIC_level/
│   └── topik_vocabulary_all_levels.csv  ← TOPIK 어휘 DB (10,636어)
│
├── unidic-cwj-202302/               ← 일본어 MeCab 사전 (컴파일됨, ~1GB)
├── mecab-ko-dic/                    ← 한국어 MeCab 사전 (컴파일됨, ~107MB)
├── handic/                          ← 한국어 대안 사전 (컴파일됨, 미사용)
├── mecab-ko-dic-2.1.1-20180720_abj/ ← mecab-ko-dic 소스 (Docker 빌드용)
├── handic-mecab-20210116_src/       ← handic 소스 (참고용)
│
└── .claude/
    └── launch.json                  ← 프리뷰 서버 설정 (포트 5001)
```

---

## 어휘 데이터 파일 상세

### JLPT: `JLPT_level/JLPT-level_naver.csv`

```
컬럼: 한자표기, 읽기(히라가나), 품사, JLPT레벨
인코딩: UTF-8 BOM
구분자: 쉼표 (CSV)
```

| 레벨 | 어휘 수 |
|------|---------|
| N5 | 447 |
| N4 | 752 |
| N3 | 1,169 |
| N2 | 2,018 |
| N1 | 2,436 |

**조회 키**: `읽기(히라가나)` 또는 `한자표기`로 매핑.
MeCab feature의 `[7]` 語彙素(기본형)과 `[6]` 語彙素読み(읽기 카타카나→히라가나 변환) 둘 다 시도.

### TOPIK: `TOPIC_level/topik_vocabulary_all_levels.csv`

```
컬럼: 어휘, 품사, 레벨
인코딩: UTF-8 BOM
구분자: 쉼표 (CSV)
```

| 레벨 | 어휘 수 |
|------|---------|
| 1급 | 734 |
| 2급 | 1,100 |
| 3급 | 1,656 |
| 4급 | 2,200 |
| 5급 | 2,365 |
| 6급 | 2,580 |

**조회 키**: `어휘` 컬럼. 일부 어휘 끝에 `02`, `03` 동형이의어 번호 포함 → strip 후 fallback 조회.
동사·형용사는 어간에 `다` 붙인 형태(`있` → `있다`)도 추가 시도.

---

## MeCab 사전 경로 (실제 사용)

```python
# 일본어 — unidic-cwj-202302
# japanese.py 에서 경로 자동 계산 (프로젝트 루트 기준)
DIC_PATH = os.path.join(BASE, 'unidic-cwj-202302')
MECABRC  = '/opt/homebrew/etc/mecabrc'   # macOS Homebrew 기본값

# 한국어 — mecab-ko-dic
# korean.py 에서 경로 자동 계산
DIC_PATH = os.path.join(BASE, 'mecab-ko-dic')
MECABRC  = '/opt/homebrew/etc/mecabrc'
```

> **심볼릭 링크 우회**: 프로젝트 경로에 공백이 포함되어 있어 MeCab이 경로를 파싱하지 못하는 문제를 `/tmp/vocalevel` 심볼릭 링크로 우회함. Docker 환경(`/app`)에서는 불필요.

---

## unidic-cwj-202302 출력 포맷

MeCab + unidic-cwj feature 필드 (0-based, `\t` 이후 쉼표 분리):

| 인덱스 | 내용 | 비고 |
|--------|------|------|
| `[0]` | 品詞 | 名詞, 動詞, 助詞, 助動詞 등 |
| `[6]` | 語彙素読み | 읽기 (카타카나) |
| `[7]` | 語彙素 | 기본형/레마 |
| `[10]` | 書字形出現形 | 표층형 한자 |

---

## mecab-ko-dic 출력 포맷

MeCab + mecab-ko-dic feature 필드 (0-based):

| 인덱스 | 내용 | 비고 |
|--------|------|------|
| `[0]` | 품사 태그 | NNG, VV, JX, EC 등 |
| `[3]` | 기본형 | 원형 |

**품사 태그 분류** (`_GRAMMAR_TAGS`에 정의):
- 격조사: JKS, JKC, JKG, JKO, JKB, JKV, JKQ
- 보조사·접속조사: JX, JC
- 어미: EC, EF, EP, ETM, ETN
- 접사: XPN, XSN, XSV, XSA, XR
- 기호: SF, SP, SS, SE, SO, SW, SY

---

## 개발 서버 실행

```bash
# Flask 백엔드 서버 (메인)
python3 src/backend/app.py
# → http://localhost:5001

# 또는 Claude Code 프리뷰로 실행
# .claude/launch.json 참조 (VocaLevel App → 포트 5001)

# 데스크톱 런처 (브라우저 자동 오픈)
python3 desktop/launcher.py
```

---

## API 명세 (구현 완료)

### `GET /api/health`

```json
{"status": "ok", "version": "1.0.0"}
```

### `POST /api/analyze`

**Request:**
```json
{
  "text": "私は東京の大学で日本語を勉強しています。",
  "lang": "auto"
}
```
`lang`: `"auto"` | `"ja"` | `"jp"` | `"ko"` | `"kr"`

**Response:**
```json
{
  "detected_lang": "ja",
  "tokens": [
    {
      "surface": "東京",
      "reading": "とうきょう",
      "base_form": "東京",
      "pos": "명사",
      "level": "未登録",
      "in_list": false,
      "is_grammar": false
    }
  ],
  "stats": {
    "total": 15,
    "content_words": 8,
    "in_list": 7,
    "by_level": {"N5": 5, "N4": 1, "조사": 5, "未登録": 1, "기호": 1},
    "max_level": "N4"
  }
}
```

---

## UI 주요 기능 (구현 완료)

| 기능 | 설명 |
|------|------|
| 언어 탭 | 자동 / 일본어 / 한국어 수동 선택 |
| 샘플 버튼 | JP·KR 예문 자동 입력 |
| 문장 뷰 | 토큰 카드: [표층형 → 읽기 → 레벨 → 품사] 4행 일관 구조 |
| 표 뷰 | 토큰 테이블 (토큰·읽기·품사·기본형·레벨) |
| 툴팁 | 토큰 hover 시 상세 정보 (읽기·기본형·품사·레벨) |
| 레벨 분포 | 수평 막대 그래프 (어휘 레벨 → 문법·기타 순) |
| 다크 모드 | 헤더 버튼으로 토글 |

---

## 레벨 색상 코드 (UI 일관성)

| 레벨 | 텍스트 색 | 배경 색 |
|------|-----------|---------|
| N5 / 1급 | `#16A34A` | `#F0FDF4` |
| N4 / 2급 | `#65A30D` | `#F7FEE7` |
| N3 / 3급 | `#D97706` | `#FFFBEB` |
| N2 / 4급 | `#EA580C` | `#FFF7ED` |
| N1 / 5급 | `#DC2626` | `#FEF2F2` |
| 6급 | `#9333EA` | `#FAF5FF` |
| 문법어 (조사 등) | `#6B7280` | `#F9FAFB` |
| 미등재 | `#9CA3AF` | `#F9FAFB` |

---

## 남은 작업 (TODO)

- **Docker 배포**: Dockerfile 작성 → Railway/Render 배포
  - 경로 환경변수화 (`JP_DIC_PATH`, `KR_DIC_PATH`, `MECABRC`)
  - mecab-ko-dic 소스 빌드 스크립트 (`mecab-ko-dic-2.1.1-20180720_abj/`)
  - unidic pip 패키지 활용 (`python -m unidic download`)
- **PyInstaller 패키징**: macOS `.app` / Windows `.exe` 빌드

---

## 주의사항

- 실제 사용 사전은 `mecab-ko-dic/` (한국어), `unidic-cwj-202302/` (일본어). `handic/`은 컴파일되어 있으나 현재 미사용
- 프로젝트 경로에 공백이 있어 MeCab 초기화 시 `/tmp/vocalevel` 심볼릭 링크로 우회함 (자동 처리)
- JLPT CSV의 일부 어휘는 `한자표기` 없이 히라가나만 있는 경우 있음 (예: `ある`)
- TOPIK CSV의 어휘 일부에 동형이의어 번호(`02`, `03`) 포함 → 매핑 시 자동 strip
- MeCab Python 바인딩: `pip install mecab-python3`
