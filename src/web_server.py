"""Flask Web 服务 — 大屏展示 + API + 自动触发分析"""

import json
import re
import sys
import threading
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from flask import Flask, jsonify, send_from_directory

from data_loader import load_config
from pipeline import run_analysis, result_to_api_dict

app = Flask(__name__)

CONFIG_PATH = ROOT / "config" / "settings.yaml"
_config = load_config(CONFIG_PATH) if CONFIG_PATH.exists() else {}
OUTPUT_DIR = ROOT / _config.get("output", {}).get("dir", "output")
DASHBOARD_DIR = OUTPUT_DIR / "dashboard"
DATA_PATH = ROOT / _config.get("data", {}).get("default_input", "data/sample/orders.csv")

_last_result = None
_is_running = False


def _load_json_file(path: Path) -> dict:
    """读取 JSON 文件，兼容旧版 NaN 写法"""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"\bNaN\b", "null", text)
    text = re.sub(r"\bInfinity\b", "null", text)
    text = re.sub(r"-Infinity", "null", text)
    return json.loads(text)


def _run_pipeline():
    global _last_result, _is_running
    if _is_running:
        return False
    _is_running = True
    try:
        _last_result = run_analysis(
            DATA_PATH, _config, OUTPUT_DIR,
            generate_charts=True,
            generate_html=True,
            generate_excel=True,
            generate_dashboard=True,
        )
        return True
    finally:
        _is_running = False


@app.route("/")
def index():
    return send_from_directory(DASHBOARD_DIR, "index.html")


@app.route("/data.json")
def data_json():
    json_path = DASHBOARD_DIR / "data.json"
    if json_path.exists():
        from dashboard_generator import _sanitize_for_json
        data = _sanitize_for_json(_load_json_file(json_path))
        return jsonify(data)
    return jsonify({"error": "no data, run analysis first"}), 404


@app.route("/api/data")
def api_data():
    json_path = DASHBOARD_DIR / "data.json"
    if json_path.exists():
        from dashboard_generator import _sanitize_for_json
        return jsonify(_sanitize_for_json(_load_json_file(json_path)))
    if _last_result:
        from dashboard_generator import _sanitize_for_json
        return jsonify(_sanitize_for_json(result_to_api_dict(_last_result)))
    return jsonify({"error": "no data"}), 404


@app.route("/api/status")
def api_status():
    return jsonify({
        "status": "running" if _is_running else "idle",
        "last_run": _last_result.run_at if _last_result else None,
        "data_path": str(DATA_PATH),
        "dashboard_ready": (DASHBOARD_DIR / "index.html").exists(),
    })


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    if _is_running:
        return jsonify({"status": "busy"}), 409
    thread = threading.Thread(target=_run_pipeline, daemon=True)
    thread.start()
    return jsonify({"status": "started", "time": datetime.now().isoformat()})


@app.route("/charts/<path:filename>")
def serve_chart(filename):
    return send_from_directory(OUTPUT_DIR / "charts", filename)


def create_app():
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    if not (DASHBOARD_DIR / "data.json").exists() and DATA_PATH.exists():
        _run_pipeline()
    return app


def main(host="127.0.0.1", port=8080):
    create_app()
    print(f"[*] 数据大屏服务启动: http://{host}:{port}")
    print(f"[*] API 状态: http://{host}:{port}/api/status")
    print(f"[*] 手动刷新: POST http://{host}:{port}/api/refresh")
    print("[*] 按 Ctrl+C 停止")
    app.run(host=host, port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    main(args.host, args.port)
