"""
================================================================================
TASK 2: SERVICE TRUY VẤN VÀ XỬ LÝ DỮ LIỆU LỊCH SỬ (EVENT SERVICE)
================================================================================
Cung cấp các API nghiệp vụ để lấy dữ liệu sự kiện kèm nguồn:
- Lấy toàn bộ sự kiện theo dòng thời gian (mốc).
- Xem chi tiết 1 sự kiện kèm trích dẫn khoa học chính thống.
- Tìm kiếm sự kiện theo từ khóa (tên, năm, nhân vật, tài liệu trích dẫn).
- Lọc theo thời kỳ lịch sử.
- Cơ chế Hybrid: Tự động truy vấn MySQL nếu online, fallback sang JSON cache.
"""

import os
import sys
import json
from typing import List, Optional, Dict, Any

# Đảm bảo in tiếng Việt trên console Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from task2.schema import SuKienLichSu, MocThoiGian, NguonLichSu, NhanVatLichSu
from task2.dataset_30_events import DATASET_30_SU_KIEN
from task2.seeder import get_db_connection, JSON_CACHE_PATH


class HistoricalEventService:
    """Service xử lý dữ liệu lịch sử kèm nguồn tài liệu"""

    def __init__(self):
        self._cache_events: List[SuKienLichSu] = []
        self._load_all_events()

    def _load_all_events(self):
        """Tải toàn bộ sự kiện từ MySQL hoặc file JSON cache"""
        events = []
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    # Truy vấn kết hợp sự kiện, mốc và nguồn
                    sql = """
                        SELECT sk.ma_su_kien, sk.ten_su_kien, sk.nam_dien_ra, sk.ngay_thang_chi_tiet,
                               sk.thoi_ky, sk.tom_tat_dien_bien, sk.y_nghia_lich_su, sk.nhan_vat_chinh,
                               sk.nguon_trich_dan,
                               m.ma_moc, m.nam AS moc_nam, m.ngay_thang AS moc_ngay, m.thoi_ky AS moc_thoi_ky, m.y_nghia_giai_doan,
                               ng.ma_nguon, ng.ten_tai_lieu, ng.loai_nguon, ng.tac_gia_co_quan, ng.nha_xuat_ban,
                               ng.nam_xuat_ban, ng.trich_dan_chi_tiet, ng.muc_do_xac_thuc
                        FROM su_kien_lich_su sk
                        LEFT JOIN moc_lich_su m ON sk.ma_moc = m.ma_moc
                        LEFT JOIN nguon_lich_su ng ON sk.ma_nguon = ng.ma_nguon
                        ORDER BY sk.nam_dien_ra ASC, sk.ma_su_kien ASC;
                    """
                    cursor.execute(sql)
                    rows = cursor.fetchall()
                    
                    # Truy vấn nhân vật cho từng sự kiện
                    for row in rows:
                        moc_obj = None
                        if row.get("ma_moc"):
                            moc_obj = MocThoiGian(
                                ma_moc=row["ma_moc"],
                                nam=row["moc_nam"],
                                ngay_thang=row.get("moc_ngay", ""),
                                thoi_ky=row.get("moc_thoi_ky", ""),
                                y_nghia_giai_doan=row.get("y_nghia_giai_doan", "")
                            )
                        
                        nguon_obj = None
                        if row.get("ma_nguon") or row.get("ten_tai_lieu"):
                            nguon_obj = NguonLichSu(
                                ma_nguon=row.get("ma_nguon", 0),
                                ten_tai_lieu=row.get("ten_tai_lieu", ""),
                                loai_nguon=row.get("loai_nguon", "Sách"),
                                tac_gia_co_quan=row.get("tac_gia_co_quan", ""),
                                nha_xuat_ban=row.get("nha_xuat_ban", ""),
                                nam_xuat_ban=row.get("nam_xuat_ban"),
                                trich_dan_chi_tiet=row.get("trich_dan_chi_tiet", ""),
                                muc_do_xac_thuc=row.get("muc_do_xac_thuc", "Chính thống - Cấp Quốc gia")
                            )

                        sk = SuKienLichSu(
                            ma_su_kien=row["ma_su_kien"],
                            ten_su_kien=row["ten_su_kien"],
                            nam_dien_ra=row["nam_dien_ra"],
                            ngay_thang_chi_tiet=row.get("ngay_thang_chi_tiet", ""),
                            thoi_ky=row.get("thoi_ky", ""),
                            tom_tat_dien_bien=row.get("tom_tat_dien_bien", ""),
                            y_nghia_lich_su=row.get("y_nghia_lich_su", ""),
                            nhan_vat_chinh=row.get("nhan_vat_chinh", ""),
                            nguon_trich_dan_text=row.get("nguon_trich_dan", ""),
                            moc=moc_obj,
                            nguon=nguon_obj
                        )
                        events.append(sk)
                conn.close()
            except Exception as e:
                events = []

        # Nếu không lấy được từ MySQL, lấy từ JSON Cache hoặc Dataset 30 sự kiện
        if not events:
            if os.path.exists(JSON_CACHE_PATH):
                try:
                    with open(JSON_CACHE_PATH, "r", encoding="utf-8") as f:
                        raw_data = json.load(f)
                        events = [SuKienLichSu.from_dict(item) for item in raw_data]
                except Exception:
                    events = []
            
            if not events:
                events = [SuKienLichSu.from_dict(item) for item in DATASET_30_SU_KIEN]

        self._cache_events = events

    def get_all_events(self) -> List[SuKienLichSu]:
        """Lấy toàn bộ danh sách sự kiện xếp theo dòng thời gian"""
        return sorted(self._cache_events, key=lambda x: (x.nam_dien_ra, x.ma_su_kien))

    def get_event_by_id(self, ma_su_kien: int) -> Optional[SuKienLichSu]:
        """Lấy chi tiết 1 sự kiện theo ID"""
        for sk in self._cache_events:
            if sk.ma_su_kien == ma_su_kien:
                return sk
        return None

    def search_events(self, keyword: str) -> List[SuKienLichSu]:
        """Tìm kiếm sự kiện theo từ khóa đa tiêu chí"""
        kw = keyword.strip().lower()
        if not kw:
            return self.get_all_events()

        ket_qua = []
        for sk in self._cache_events:
            match = False
            if kw in sk.ten_su_kien.lower():
                match = True
            elif kw in str(sk.nam_dien_ra):
                match = True
            elif kw in sk.ngay_thang_chi_tiet.lower():
                match = True
            elif kw in sk.thoi_ky.lower():
                match = True
            elif kw in sk.nhan_vat_chinh.lower():
                match = True
            elif kw in sk.tom_tat_dien_bien.lower():
                match = True
            elif sk.nguon and (kw in sk.nguon.ten_tai_lieu.lower() or kw in sk.nguon.tac_gia_co_quan.lower()):
                match = True
            elif kw in sk.nguon_trich_dan_text.lower():
                match = True

            if match:
                ket_qua.append(sk)

        return ket_qua

    def filter_by_period(self, thoi_ky: str) -> List[SuKienLichSu]:
        """Lọc sự kiện theo thời kỳ lịch sử"""
        tk_lower = thoi_ky.strip().lower()
        return [sk for sk in self._cache_events if tk_lower in sk.thoi_ky.lower()]

    def get_all_periods(self) -> List[str]:
        """Lấy danh sách các thời kỳ duy nhất"""
        periods = []
        for sk in self._cache_events:
            if sk.thoi_ky and sk.thoi_ky not in periods:
                periods.append(sk.thoi_ky)
        return periods


# Instance mặc định dùng cho toàn ứng dụng
event_service = HistoricalEventService()
