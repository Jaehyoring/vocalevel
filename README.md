# VocaLevel 📚

**일본어·한국어 어휘 레벨 분석기** — JLPT & TOPIK 기준으로 텍스트의 어휘 레벨을 색상으로 시각화합니다.

---

## 기능

- 일본어(JLPT N5~N1) / 한국어(TOPIK 1~6급) 어휘 레벨 자동 판별
- MeCab 형태소 분석으로 단어 분해 후 어휘 사전과 대조
- 언어 자동 감지 (히라가나·가타카나 vs 한글 비율)
- 토큰 카드 뷰 (표층형 / 읽기 / 레벨 / 품사) + 표 뷰 전환
- 레벨 분포 수평 막대 그래프
- 툴팁으로 기본형·품사·레벨 상세 확인
- 다크 모드 지원

---

## 요구사항

- Python 3.10 이상
- MeCab (`brew install mecab` on macOS)
- `pip install flask mecab-python3`
- 컴파일된 사전 (프로젝트 내 포함):
  - 일본어: `unidic-cwj-202302/`
  - 한국어: `mecab-ko-dic/`

---

## 실행 방법

### 웹 서버

```bash
python3 src/backend/app.py
# → http://localhost:5001
```

### 데스크톱 런처 (브라우저 자동 오픈)

```bash
python3 desktop/launcher.py
```

---

## API

### `POST /api/analyze`

```bash
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "私は毎日日本語を勉強しています。", "lang": "auto"}'
```

**응답:**
```json
{
  "detected_lang": "ja",
  "tokens": [
    {
      "surface": "勉強",
      "reading": "べんきょう",
      "base_form": "勉強",
      "pos": "명사",
      "level": "N5",
      "in_list": true,
      "is_grammar": false
    }
  ],
  "stats": {
    "total": 12,
    "content_words": 6,
    "in_list": 5,
    "by_level": {"N5": 4, "N4": 1, "조사": 5, "기호": 1},
    "max_level": "N4"
  }
}
```

`lang` 파라미터: `"auto"` (기본값) | `"ja"` / `"jp"` | `"ko"` / `"kr"`

### `GET /api/health`

```json
{"status": "ok", "version": "1.0.0"}
```

---

## 레벨 색상

| 레벨 | 색상 |
|------|------|
| N5 / 1급 | 초록 |
| N4 / 2급 | 연두 |
| N3 / 3급 | 노랑 |
| N2 / 4급 | 주황 |
| N1 / 5급 | 빨강 |
| 6급 | 보라 |
| 조사·어미 등 | 회색 |
| 미등재 | 연회색 |

---

## 어휘 데이터

| 사전 | 파일 | 어휘 수 |
|------|------|---------|
| JLPT | `JLPT_level/JLPT-level_naver.csv` | 6,822어 |
| TOPIK | `TOPIC_level/topik_vocabulary_all_levels.csv` | 10,636어 |

---

## 기술 스택

- **백엔드**: Python 3.12 + Flask
- **형태소 분석**: MeCab + mecab-python3
  - 일본어 사전: UniDic (unidic-cwj-202302)
  - 한국어 사전: mecab-ko-dic 2.1.1
- **프론트엔드**: 순수 HTML/CSS/JS (프레임워크 없음)
