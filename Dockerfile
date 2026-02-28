# ── 런타임 이미지 ─────────────────────────────────────────────────
FROM python:3.12-slim

# 일본어 MeCab (시스템 바이너리)
RUN apt-get update && apt-get install -y --no-install-recommends \
        mecab \
        libmecab-dev \
        mecab-ipadic-utf8 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python 의존성 설치 + 일본어 unidic 사전 다운로드
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m unidic download

# 앱 코드 및 어휘 데이터 복사
COPY src/ src/
COPY JLPT_level/ JLPT_level/
COPY TOPIC_level/ TOPIC_level/

# 환경변수
ENV MECABRC=/etc/mecabrc \
    PORT=5001

EXPOSE 5001

CMD ["python", "src/backend/app.py"]
