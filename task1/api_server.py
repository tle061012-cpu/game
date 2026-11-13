"""Task 1: API Server lưu trữ tiến độ chơi và đồng bộ điểm người chơi.

Hỗ trợ 2 chế độ:
1. FastAPI + Uvicorn (khi môi trường đã cài đặt).
2. Built-in Python HTTP Server (chuẩn zero-dependency, chạy mượt mà ngay lập tức).
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any

HOST = "0.0.0.0"
PORT = 8000
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "api_progress_db.json")


def load_db() -> Dict[str, Any]:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"users": {}, "progress": {}, "leaderboard": []}


def save_db(data: Dict[str, Any]):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class SimpleAPIServer(BaseHTTPRequestHandler):
    """Zero-dependency HTTP Handler triển khai đầy đủ các REST endpoint cho Game."""

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        db = load_db()
        path = self.path

        if path == "/api/health" or path == "/":
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "status": "healthy",
                "service": "Game Lich Su Viet Nam - Progress API",
                "version": "1.0.0"
            }).encode("utf-8"))

        elif path.startswith("/api/progress/"):
            user_id = path.replace("/api/progress/", "").strip("/")
            user_data = db["progress"].get(user_id, {
                "user_id": user_id,
                "score": 0,
                "completed": [],
                "max_year": 1914,
                "task4": {}
            })
            self._set_headers(200)
            self.wfile.write(json.dumps({"success": True, "data": user_data}).encode("utf-8"))

        elif path == "/api/leaderboard":
            leaderboard = db.get("leaderboard", [])
            # Sắp xếp theo điểm giảm dần
            leaderboard.sort(key=lambda x: x.get("score", 0), reverse=True)
            self._set_headers(200)
            self.wfile.write(json.dumps({"success": True, "leaderboard": leaderboard[:10]}).encode("utf-8"))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode("utf-8"))
            return

        db = load_db()

        if self.path == "/api/progress/save":
            user_id = str(payload.get("user_id", "guest"))
            score = payload.get("score", 0)
            completed = payload.get("completed", [])
            user_name = payload.get("user_name", f"Học giả #{user_id}")

            # Lưu tiến độ
            db["progress"][user_id] = {
                "user_id": user_id,
                "user_name": user_name,
                "score": score,
                "completed": completed,
                "max_year": payload.get("max_year", 1914),
                "task4": payload.get("task4", {}),
            }

            # Cập nhật Bảng xếp hạng (Leaderboard)
            existing = [u for u in db["leaderboard"] if str(u.get("user_id")) == user_id]
            if existing:
                existing[0]["score"] = max(existing[0]["score"], score)
                existing[0]["user_name"] = user_name
            else:
                db["leaderboard"].append({
                    "user_id": user_id,
                    "user_name": user_name,
                    "score": score
                })

            save_db(db)
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "success": True,
                "message": "Đã lưu tiến độ thành công vào máy chủ",
                "saved_score": score
            }).encode("utf-8"))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))


def start_server(port=PORT):
    server = HTTPServer((HOST, port), SimpleAPIServer)
    print(f">> [Task 1] API Server dang chay tai: http://localhost:{port}")
    print(">> Endpoints ho tro:")
    print("   - GET  /api/health")
    print("   - GET  /api/progress/{user_id}")
    print("   - POST /api/progress/save")
    print("   - GET  /api/leaderboard")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n>> Dong server thanh cong.")
        server.server_close()


if __name__ == "__main__":
    start_server()

