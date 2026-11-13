"""
================================================================================
TASK 1: FASTAPI REST API SERVER (CHUẨN BACKEND DOANH NGHIỆP HIỆN ĐẠI)
================================================================================
Triển khai REST API chuẩn công nghiệp với:
1. FastAPI framework tốc độ cao.
2. Pydantic BaseModel kiểm soát kiểu dữ liệu và tự động xác thực (Data Validation).
3. CORS Middleware cho phép mọi ứng dụng Web/Game gọi API.
4. Tự động sinh tài liệu Swagger UI tương tác tại: http://localhost:8000/docs
"""

import json
import os
from typing import Any, Dict, List, Optional
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException, status
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
except ImportError:
    raise ImportError("Cần cài đặt fastapi và pydantic: pip install fastapi pydantic uvicorn")

# Đường dẫn file JSON lưu trữ
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "api_progress_db.json"

# --- PYDANTIC SCHEMAS (DATA VALIDATION) ---
class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Trạng thái máy chủ")
    service: str = Field(default="Game Lich Su Viet Nam - Progress API")
    version: str = Field(default="2.0.0")


class Task4ProgressData(BaseModel):
    locations: Dict[str, Any] = Field(default_factory=dict, description="Tiến trình FSM 4 địa danh")


class ProgressSaveRequest(BaseModel):
    user_id: str = Field(..., description="Mã định danh người chơi", example="player1")
    user_name: Optional[str] = Field(default=None, description="Tên hiển thị người chơi", example="Nguyễn Văn A")
    score: int = Field(default=0, ge=0, description="Điểm tri thức tích lũy", example=250)
    completed: List[str] = Field(default_factory=list, description="Danh sách địa danh đã hoàn thành", example=["Pác Bó (Cao Bằng)"])
    max_year: int = Field(default=1911, ge=1911, le=1975, description="Mốc năm cao nhất đã mở khóa", example=1945)
    task4: Dict[str, Any] = Field(default_factory=dict, description="Dữ liệu nhiệm vụ Task 4")


class ProgressResponse(BaseModel):
    success: bool
    data: Dict[str, Any]


class LeaderboardItem(BaseModel):
    user_id: str
    user_name: str
    score: int


class LeaderboardResponse(BaseModel):
    success: bool
    leaderboard: List[LeaderboardItem]


# --- DATABASE HELPER FUNCTIONS ---
def load_db() -> Dict[str, Any]:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"users": {}, "progress": {}, "leaderboard": []}


def save_db(data: Dict[str, Any]):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# --- KHỞI TẠO FASTAPI APP ---
app = FastAPI(
    title="Game Lịch Sử Việt Nam - Backend REST API",
    description="Hệ thống REST API đồng bộ tiến trình, điểm tri thức và bảng vàng xếp hạng người chơi.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Kích hoạt CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse, tags=["Hệ thống"])
async def health_check():
    """Kiểm tra tình trạng hoạt động của máy chủ API."""
    return HealthResponse()


@app.get("/api/progress/{user_id}", response_model=ProgressResponse, tags=["Tiến độ chơi"])
async def get_progress(user_id: str):
    """Lấy dữ liệu tiến độ, điểm số và các mốc lịch sử đã hoàn thành của người chơi."""
    db = load_db()
    progress_data = db.get("progress", {}).get(user_id)
    if not progress_data:
        progress_data = {
            "user_id": user_id,
            "score": 0,
            "completed": [],
            "max_year": 1911,
            "task4": {},
        }
    return ProgressResponse(success=True, data=progress_data)


@app.post("/api/progress/save", tags=["Tiến độ chơi"])
async def save_progress(payload: ProgressSaveRequest):
    """Lưu trữ tiến độ chơi, cập nhật bảng vàng xếp hạng (Leaderboard) theo thời gian thực."""
    db = load_db()
    uid = str(payload.user_id)
    uname = payload.user_name or f"Học giả #{uid}"

    # 1. Cập nhật tiến độ người chơi
    db["progress"][uid] = {
        "user_id": uid,
        "user_name": uname,
        "score": payload.score,
        "completed": payload.completed,
        "max_year": payload.max_year,
        "task4": payload.task4,
    }

    # 2. Cập nhật Bảng xếp hạng
    leaderboard = db.get("leaderboard", [])
    found = False
    for item in leaderboard:
        if str(item.get("user_id")) == uid:
            item["score"] = max(item.get("score", 0), payload.score)
            item["user_name"] = uname
            found = True
            break
    if not found:
        leaderboard.append({"user_id": uid, "user_name": uname, "score": payload.score})

    leaderboard.sort(key=lambda x: x.get("score", 0), reverse=True)
    db["leaderboard"] = leaderboard
    save_db(db)

    return {
        "success": True,
        "message": f"Đã lưu tiến độ của học giả {uname} thành công",
        "saved_score": payload.score,
    }


@app.get("/api/leaderboard", response_model=LeaderboardResponse, tags=["Bảng vàng"])
async def get_leaderboard(limit: int = 10):
    """Truy xuất danh sách Top người chơi có điểm tri thức cao nhất."""
    db = load_db()
    lb = db.get("leaderboard", [])
    lb.sort(key=lambda x: x.get("score", 0), reverse=True)
    items = [
        LeaderboardItem(user_id=str(x["user_id"]), user_name=x["user_name"], score=x["score"])
        for x in lb[:limit]
    ]
    return LeaderboardResponse(success=True, leaderboard=items)


def run():
    """Khởi động máy chủ bằng Uvicorn."""
    import uvicorn
    print("\n" + "=" * 65)
    print(">> [TASK 1] FASTAPI REST SERVER ĐANG KHỞI ĐỘNG...")
    print(">> Swagger UI Tài liệu tương tác: http://127.0.0.1:8000/docs")
    print(">> Redoc:                        http://127.0.0.1:8000/redoc")
    print("=" * 65 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    run()

