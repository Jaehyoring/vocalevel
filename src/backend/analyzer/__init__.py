from .detector import detect_language
from .japanese import analyze as analyze_ja
from .korean  import analyze as analyze_ko

__all__ = ['detect_language', 'analyze_ja', 'analyze_ko']
