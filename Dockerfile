# ── Stage 1: 한국어 MeCab 사전 빌드 ─────────────────────────────
FROM python:3.12-slim AS ko-dic-builder

RUN apt-get update && apt-get install -y --no-install-recommends \
        mecab \
        libmecab-dev \
        build-essential \
        automake \
        autoconf \
        libtool \
        pkg-config \
        wget \
        xz-utils \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O /tmp/mecab-ko-dic.tar.gz \
        https://bitbucket.org/eunjeon/mecab-ko-dic/downloads/mecab-ko-dic-2.1.1-20180720.tar.gz \
    && tar -xf /tmp/mecab-ko-dic.tar.gz -C /tmp \
    && rm /tmp/mecab-ko-dic.tar.gz

RUN cd /tmp/mecab-ko-dic-2.1.1-20180720 \
    && ./configure --with-charset=UTF-8 \
    && make \
    && make install

# ── Stage 2: 런타임 이미지 ───────────────────────────────────────
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
        mecab \
        libmecab-dev \
        mecab-ipadic-utf8 \
    && rm -rf /var/lib/apt/lists/*

# 빌드된 한국어 사전 복사
COPY --from=ko-dic-builder /var/lib/mecab/dic/mecab-ko-dic /var/lib/mecab/dic/mecab-ko-dic

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
    KR_DIC_PATH=/var/lib/mecab/dic/mecab-ko-dic \
    PORT=5001

EXPOSE 5001

CMD ["python", "src/backend/app.py"]
