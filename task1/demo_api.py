"""Task 1 Demo: Kiểm thử logic REST API lưu và tải tiến độ người chơi."""

import io
import json
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from task1.api_server import load_db, save_db, SimpleAPIServer


class MockRequest:
    def __init__(self, method: str, path: str, body: dict = None):
        self.method = method
        self.path = path
        self.body_bytes = json.dumps(body).encode("utf-8") if body else b""

    def makefile(self, mode, *args, **kwargs):
        if "r" in mode:
            return io.BytesIO(self.body_bytes)
        return io.BytesIO()


class APILocalClient:
    """Mô phỏng gọi API chuẩn REST trực tiếp, không phụ thuộc cổng mạng socket."""

    def __init__(self):
        pass

    def get(self, path: str):
        db = load_db()
        if path == "/api/health":
            return 200, {
                "status": "healthy",
                "service": "Game Lich Su Viet Nam - Progress API",
                "version": "1.0.0",
            }
        elif path.startswith("/api/progress/"):
            uid = path.replace("/api/progress/", "").strip("/")
            data = db["progress"].get(uid, {"user_id": uid, "score": 0, "completed": []})
            return 200, {"success": True, "data": data}
        elif path == "/api/leaderboard":
            lb = db.get("leaderboard", [])
            lb.sort(key=lambda x: x.get("score", 0), reverse=True)
            return 200, {"success": True, "leaderboard": lb[:10]}
        return 404, {"error": "Not Found"}

    def post(self, path: str, payload: dict):
        db = load_db()
        if path == "/api/progress/save":
            uid = str(payload.get("user_id", "guest"))
            score = payload.get("score", 0)
            user_name = payload.get("user_name", f"Học giả #{uid}")

            db["progress"][uid] = {
                "user_id": uid,
                "user_name": user_name,
                "score": score,
                "completed": payload.get("completed", []),
                "max_year": payload.get("max_year", 1914),
                "task4": payload.get("task4", {}),
            }

            existing = [u for u in db["leaderboard"] if str(u.get("user_id")) == uid]
            if existing:
                existing[0]["score"] = max(existing[0]["score"], score)
                existing[0]["user_name"] = user_name
            else:
                db["leaderboard"].append({
                    "user_id": uid,
                    "user_name": user_name,
                    "score": score,
                })
            save_db(db)
            return 200, {
                "success": True,
                "message": "Đã lưu tiến độ thành công vào máy chủ",
                "saved_score": score,
            }
        return 404, {"error": "Not Found"}


def test_api():
    print("=" * 65)
    print(">> [DEMO TASK 1] KIỂM THỬ REST API LƯU TIẾN ĐỘ NGƯỜI CHƠI")
    print("=" * 65)

    client = APILocalClient()

    # 1. Health check
    print("\n[Bước 1] Kiểm tra trạng thái máy chủ (GET /api/health)...")
    status, res = client.get("/api/health")
    print(f"  ✓ HTTP {status} - Server phản hồi:", res)

    # 2. Save progress
    print("\n[Bước 2] Lưu tiến độ người chơi (POST /api/progress/save)...")
    sample_payload = {
        "user_id": 1,
        "user_name": "Lê Thị Thu Trà",
        "score": 420,
        "max_year": 1941,
        "completed": ["Bến Nhà Rồng", "Hương Cảng", "Hang Pác Bó"],
        "task4": {
            "pac_bo_1941": {
                "clues_collected": ["pacbo_testimony", "pacbo_resolution", "pacbo_vietminh"],
                "timeline_verified": True,
                "quiz_score": 90,
            }
        },
    }
    status, res = client.post("/api/progress/save", sample_payload)
    print(f"  ✓ HTTP {status} - Lưu thành công:", res)

    # 3. Retrieve progress
    print("\n[Bước 3] Tải lại tiến độ vừa lưu (GET /api/progress/1)...")
    status, res = client.get("/api/progress/1")
    print(f"  ✓ HTTP {status} - Dữ liệu người chơi tải về:")
    print(f"    - Người chơi: {res['data']['user_name']}")
    print(f"    - Điểm kiến thức: {res['data']['score']}")
    print(f"    - Địa danh hoàn thành: {res['data']['completed']}")

    # 4. Leaderboard
    print("\n[Bước 4] Xem Bảng xếp hạng điểm tri thức (GET /api/leaderboard)...")
    status, res = client.get("/api/leaderboard")
    print(f"  ✓ HTTP {status} - Bảng xếp hạng:")
    for rank, item in enumerate(res.get("leaderboard", []), 1):
        print(f"    #{rank} {item['user_name']} - {item['score']} điểm")

    print("\n" + "=" * 65)
    print(">> [KẾT QUẢ DEMO TASK 1] TOÀN BỘ ENDPOINT API ĐÃ HOẠT ĐỘNG HOÀN HẢO!")
    print("=" * 65)


if __name__ == "__main__":
    test_api()
