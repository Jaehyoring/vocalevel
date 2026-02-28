"""언어 자동 감지 모듈"""


def detect_language(text: str) -> str:
    """
    히라가나·가타카나 vs 한글 문자 수로 언어를 판별.
    Returns: 'ja' | 'ko' | 'unknown'
    """
    jp_count = sum(1 for c in text if '\u3040' <= c <= '\u30FF' or '\u4E00' <= c <= '\u9FFF')
    kr_count = sum(1 for c in text if '\uAC00' <= c <= '\uD7A3' or '\u3130' <= c <= '\u318F')

    if jp_count == 0 and kr_count == 0:
        return 'unknown'
    return 'ja' if jp_count >= kr_count else 'ko'
