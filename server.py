#!/usr/bin/env python3
"""VocaLevel 개발 서버 — src/frontend 폴더를 포트 7654로 서비스"""
import os, sys

# src/frontend 로 이동
base = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(base, "src", "frontend"))

from http.server import HTTPServer, SimpleHTTPRequestHandler

port = 7654
print(f"VocaLevel 서버 시작: http://localhost:{port}/")
HTTPServer(("", port), SimpleHTTPRequestHandler).serve_forever()
