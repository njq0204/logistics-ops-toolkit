#!/usr/bin/env python3
"""
一键启动数据大屏

用法:
  python scripts/start_bigscreen.py          # 启动服务并打开浏览器
  python scripts/start_bigscreen.py --port 9090
"""

import argparse
import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


def main():
    parser = argparse.ArgumentParser(description="启动数据大屏")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}"

    if not args.no_browser:
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()

    from web_server import main as serve
    serve(args.host, args.port)


if __name__ == "__main__":
    main()
