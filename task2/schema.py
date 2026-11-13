"""
================================================================================
TASK 2: SCHEMA DỮ LIỆU LỊCH SỬ CÓ NGUỒN (HISTORICAL DATA SCHEMA)
================================================================================
File này định nghĩa mô hình dữ liệu quan hệ (Data Model / Entities):
1. MocThoiGian: Mốc thời gian, năm, ngày tháng, thời kỳ lịch sử.
2. NguonLichSu: Nguồn trích dẫn, tác giả, nhà xuất bản, tài liệu chính thống.
3. NhanVatLichSu: Nhân vật lịch sử, vai trò, đóng góp.
4. SuKienLichSu: Sự kiện lịch sử liên kết với Mốc, Nguồn và Nhân vật.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any


@dataclass
class MocThoiGian:
    """Thực thể Mốc thời gian / Giai đoạn lịch sử"""
    ma_moc: int
    nam: int
    ngay_thang: str = ""
    thoi_ky: str = ""
    y_nghia_giai_doan: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MocThoiGian":
        return cls(
            ma_moc=int(data.get("ma_moc", 0)),
            nam=int(data.get("nam", 0)),
            ngay_thang=str(data.get("ngay_thang", "")),
            thoi_ky=str(data.get("thoi_ky", "")),
            y_nghia_giai_doan=str(data.get("y_nghia_giai_doan", ""))
        )


@dataclass
class NguonLichSu:
    """Thực thể Nguồn tài liệu / Trích dẫn lịch sử chính thống"""
    ma_nguon: int
    ten_tai_lieu: str
    loai_nguon: str = "Sách"               # Sách, Văn kiện Đảng, Hồi ký, Hồ sơ bảo tàng, v.v.
    tac_gia_co_quan: str = ""             # Viện Sử học, Ban Tuyên giáo, NXB Giáo dục, v.v.
    nha_xuat_ban: str = ""                # NXB Chính trị quốc gia Sự thật, NXB QĐND, v.v.
    nam_xuat_ban: Optional[int] = None
    trich_dan_chi_tiet: str = ""          # Số tập, trang, lời trích dẫn
    muc_do_xac_thuc: str = "Chính thống - Cấp Quốc gia"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NguonLichSu":
        return cls(
            ma_nguon=int(data.get("ma_nguon", 0)),
            ten_tai_lieu=str(data.get("ten_tai_lieu", "")),
            loai_nguon=str(data.get("loai_nguon", "Sách")),
            tac_gia_co_quan=str(data.get("tac_gia_co_quan", "")),
            nha_xuat_ban=str(data.get("nha_xuat_ban", "")),
            nam_xuat_ban=int(data["nam_xuat_ban"]) if data.get("nam_xuat_ban") is not None else None,
            trich_dan_chi_tiet=str(data.get("trich_dan_chi_tiet", "")),
            muc_do_xac_thuc=str(data.get("muc_do_xac_thuc", "Chính thống - Cấp Quốc gia"))
        )

    def format_citation(self) -> str:
        """Định dạng chuỗi trích dẫn khoa học chuẩn chuẩn APA/Việt Nam"""
        parts = []
        if self.tac_gia_co_quan:
            parts.append(self.tac_gia_co_quan)
        if self.nam_xuat_ban:
            parts.append(f"({self.nam_xuat_ban})")
        parts.append(f'"{self.ten_tai_lieu}"')
        if self.nha_xuat_ban:
            parts.append(f"NXB {self.nha_xuat_ban}")
        if self.trich_dan_chi_tiet:
            parts.append(self.trich_dan_chi_tiet)
        return ", ".join(parts) + "."


@dataclass
class NhanVatLichSu:
    """Thực thể Nhân vật lịch sử tiêu biểu"""
    ma_nhan_vat: int
    ten_nhan_vat: str
    nam_sinh_mat: str = ""
    vai_tro: str = ""
    tieu_su_dong_gop: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NhanVatLichSu":
        return cls(
            ma_nhan_vat=int(data.get("ma_nhan_vat", 0)),
            ten_nhan_vat=str(data.get("ten_nhan_vat", "")),
            nam_sinh_mat=str(data.get("nam_sinh_mat", "")),
            vai_tro=str(data.get("vai_tro", "")),
            tieu_su_dong_gop=str(data.get("tieu_su_dong_gop", ""))
        )


@dataclass
class SuKienLichSu:
    """Thực thể Sự kiện lịch sử cốt lõi có liên kết Mốc, Nguồn và Nhân vật"""
    ma_su_kien: int
    ten_su_kien: str
    nam_dien_ra: int
    ngay_thang_chi_tiet: str
    thoi_ky: str
    tom_tat_dien_bien: str
    y_nghia_lich_su: str
    dia_diem_lien_quan: str = ""
    nhan_vat_chinh: str = ""
    nguon_trich_dan_text: str = ""       # Chuỗi nguồn tương thích với CSDL hiện tại
    
    # Liên kết với các đối tượng chi tiết
    moc: Optional[MocThoiGian] = None
    nguon: Optional[NguonLichSu] = None
    danh_sach_nhan_vat: List[NhanVatLichSu] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        res = {
            "ma_su_kien": self.ma_su_kien,
            "ten_su_kien": self.ten_su_kien,
            "nam_dien_ra": self.nam_dien_ra,
            "ngay_thang_chi_tiet": self.ngay_thang_chi_tiet,
            "thoi_ky": self.thoi_ky,
            "tom_tat_dien_bien": self.tom_tat_dien_bien,
            "y_nghia_lich_su": self.y_nghia_lich_su,
            "dia_diem_lien_quan": self.dia_diem_lien_quan,
            "nhan_vat_chinh": self.nhan_vat_chinh,
            "nguon_trich_dan": self.nguon_trich_dan_text,
            "moc": self.moc.to_dict() if self.moc else None,
            "nguon_chi_tiet": self.nguon.to_dict() if self.nguon else None,
            "nhan_vat_lien_quan": [nv.to_dict() for nv in self.danh_sach_nhan_vat]
        }
        return res

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SuKienLichSu":
        moc_obj = MocThoiGian.from_dict(data["moc"]) if data.get("moc") else None
        nguon_obj = NguonLichSu.from_dict(data["nguon_chi_tiet"]) if data.get("nguon_chi_tiet") else None
        
        danh_sach_nv = []
        if data.get("nhan_vat_lien_quan"):
            for nv in data["nhan_vat_lien_quan"]:
                danh_sach_nv.append(NhanVatLichSu.from_dict(nv))
                
        return cls(
            ma_su_kien=int(data.get("ma_su_kien", 0)),
            ten_su_kien=str(data.get("ten_su_kien", "")),
            nam_dien_ra=int(data.get("nam_dien_ra", 0)),
            ngay_thang_chi_tiet=str(data.get("ngay_thang_chi_tiet", "")),
            thoi_ky=str(data.get("thoi_ky", "")),
            tom_tat_dien_bien=str(data.get("tom_tat_dien_bien", "")),
            y_nghia_lich_su=str(data.get("y_nghia_lich_su", "")),
            dia_diem_lien_quan=str(data.get("dia_diem_lien_quan", "")),
            nhan_vat_chinh=str(data.get("nhan_vat_chinh", "")),
            nguon_trich_dan_text=str(data.get("nguon_trich_dan", "")),
            moc=moc_obj,
            nguon=nguon_obj,
            danh_sach_nhan_vat=danh_sach_nv
        )
