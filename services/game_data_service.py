"""
================================================================================
PHẦN 2: THUẬT TOÁN & PHƯƠNG THỨC XỬ LÝ NGHIỆP VỤ (BUSINESS LOGIC & MAPPING)
================================================================================
File này chịu trách nhiệm:
1. Gọi các hàm truy vấn SQL từ tầng data (data/db_queries.py).
2. Thuật toán chuyển đổi (Transform/Mapping) dữ liệu bảng quan hệ từ CSDL
   sang định dạng dữ liệu cho từng màn hình game (Map, Investigation, Deduction).
3. Cơ chế Fallback / Cache: Tự động dùng dữ liệu dự phòng nếu MySQL chưa bật,
   đảm bảo game luôn chạy ổn định 100% không bao giờ crash.
"""

from data.db_queries import (
    fetch_raw_dia_diem,
    fetch_raw_su_kien,
    fetch_raw_nhan_vat,
    fetch_raw_manh_moi,
    fetch_raw_cau_hoi,
    authenticate_user,
    register_user,
    fetch_user_progress,
    save_user_progress,
    fetch_task4_progress,
    save_task4_progress
)

# ------------------------------------------------------------------------------
# 1. BẢNG CẤU HÌNH BỔ TRỢ TỌA ĐỘ VÀ GIAI ĐOẠN CHO MÀN HÌNH BẢN ĐỒ (MAP METADATA)
# ------------------------------------------------------------------------------
LOCATION_MAP_CONFIG = {
    1: {"key": "Ben Nha Rong", "side": "r", "dy": 0, "start": 1914, "end": 1930, "x": 365, "y": 500},
    2: {"key": "Hong Kong", "side": "l", "dy": 0, "start": 1930, "end": 1931, "x": 525, "y": 203},
    3: {"key": "Vinh - Ben Thuy", "side": "r", "dy": 0, "start": 1930, "end": 1931, "x": 336, "y": 277},
    4: {"key": "Pac Bo", "side": "r", "dy": -8, "start": 1941, "end": 1945, "x": 325, "y": 180},
    5: {"key": "Tan Trao", "side": "l", "dy": -6, "start": 1941, "end": 1945, "x": 300, "y": 201},
    6: {"key": "Ba Dinh", "side": "r", "dy": 8, "start": 1941, "end": 1945, "x": 350, "y": 224},
    7: {"key": "Viet Bac", "side": "r", "dy": -12, "start": 1946, "end": 1950, "x": 329, "y": 207},
    8: {"key": "Dien Bien Phu", "side": "l", "dy": 0, "start": 1953, "end": 1954, "x": 273, "y": 217},
    9: {"key": "Dinh Doc Lap", "side": "r", "dy": 0, "start": 1975, "end": 1975, "x": 380, "y": 505},
    10: {"key": "Hien Luong - Quang Tri", "side": "r", "dy": 0, "start": 1954, "end": 1975, "x": 355, "y": 320},
    11: {"key": "Ha Noi 1972", "side": "l", "dy": 0, "start": 1972, "end": 1975, "x": 345, "y": 218},
}

# ------------------------------------------------------------------------------
# 2. DỮ LIỆU DỰ PHÒNG (FALLBACK OFFLINE CACHE - ĐẢM BẢO GAME LUÔN CHẠY ĐƯỢC)
# ------------------------------------------------------------------------------
FALLBACK_LOCATIONS = [
    {
        "id": 1,
        "name": "Ben Nha Rong",
        "display_name": "Bến Nhà Rồng (Sài Gòn)",
        "x": 365, "y": 500, "side": "r", "dy": 0,
        "start": 1914, "end": 1930,
        "event_time": "05/06/1911",
        "description": "Ngày 5/6/1911 tại Bến Nhà Rồng (Sài Gòn), người thanh niên yêu nước Nguyễn Tất Thành ra đi tìm đường cứu nước."
    },
    {
        "id": 2,
        "name": "Hong Kong",
        "display_name": "Hương Cảng (Hong Kong)",
        "x": 525, "y": 203, "side": "l", "dy": 0,
        "start": 1930, "end": 1931,
        "event_time": "03/02/1930",
        "description": "Ngày 3/2/1930 tại Hương Cảng (Hong Kong), Nguyễn Ái Quốc chủ trì Hội nghị thành lập Đảng Cộng sản Việt Nam."
    },
    {
        "id": 3,
        "name": "Vinh - Ben Thuy",
        "display_name": "Vinh - Bến Thủy (Nghệ An)",
        "x": 336, "y": 277, "side": "r", "dy": 0,
        "start": 1930, "end": 1931,
        "event_time": "1930 - 1931",
        "description": "Đỉnh cao phong trào cách mạng 1930-1931 với sự ra đời của chính quyền Xô viết Nghệ - Tĩnh anh dũng."
    },
    {
        "id": 4,
        "name": "Pac Bo",
        "display_name": "Hang Pác Bó (Cao Bằng)",
        "x": 325, "y": 180, "side": "r", "dy": -8,
        "start": 1941, "end": 1945,
        "event_time": "28/01/1941",
        "description": "Ngày 28/1/1941, lãnh tụ Nguyễn Ái Quốc trở về Tổ quốc trực tiếp lãnh đạo cách mạng tại Pác Bó (Cao Bằng)."
    },
    {
        "id": 5,
        "name": "Tan Trao",
        "display_name": "Tân Trào (Tuyên Quang)",
        "x": 300, "y": 201, "side": "l", "dy": -6,
        "start": 1941, "end": 1945,
        "event_time": "16/08/1945",
        "description": "Ngày 16/8/1945 tại Tuyên Quang, Đại hội Quốc dân Tân Trào phát lệnh Tổng khởi nghĩa giành chính quyền."
    },
    {
        "id": 6,
        "name": "Ba Dinh",
        "display_name": "Quảng trường Ba Đình (Hà Nội)",
        "x": 350, "y": 224, "side": "r", "dy": 8,
        "start": 1941, "end": 1945,
        "event_time": "02/09/1945",
        "description": "Ngày 2/9/1945 tại Quảng trường Ba Đình (Hà Nội), Bác Hồ đọc Tuyên ngôn Độc lập khai sinh nước VNDCCH."
    },
    {
        "id": 7,
        "name": "Viet Bac",
        "display_name": "Căn cứ địa Việt Bắc",
        "x": 329, "y": 207, "side": "r", "dy": -12,
        "start": 1946, "end": 1950,
        "event_time": "1947 - 1950",
        "description": "Căn cứ địa Việt Bắc, nơi bảo vệ đầu não kháng chiến và làm nên chiến thắng Chiến dịch Việt Bắc 1947, Biên giới 1950."
    },
    {
        "id": 8,
        "name": "Dien Bien Phu",
        "display_name": "Lòng chảo Điện Biên Phủ",
        "x": 273, "y": 217, "side": "l", "dy": 0,
        "start": 1953, "end": 1954,
        "event_time": "07/05/1954",
        "description": "Ngày 7/5/1954, chiến dịch Điện Biên Phủ toàn thắng, 'lừng lẫy năm châu, chấn động địa cầu', chấm dứt ách đô hộ Pháp."
    },
    {
        "id": 9,
        "name": "Dinh Doc Lap",
        "display_name": "Dinh Độc Lập (Sài Gòn)",
        "x": 380, "y": 505, "side": "r", "dy": 0,
        "start": 1975, "end": 1975,
        "event_time": "30/04/1975",
        "description": "11h30 ngày 30/4/1975, xe tăng giải phóng húc đổ cổng Dinh Độc Lập, cắm cờ chiến thắng, kết thúc toàn thắng Chiến dịch Hồ Chí Minh, non sông thu về một mối."
    },
    {
        "id": 10,
        "name": "Hien Luong - Quang Tri",
        "display_name": "Cầu Hiền Lương - Vĩ tuyến 17",
        "x": 355, "y": 320, "side": "r", "dy": 0,
        "start": 1954, "end": 1975,
        "event_time": "1954 - 1975",
        "description": "Giới tuyến quân sự tạm thời theo Hiệp định Genève 1954, nơi ghi dấu hơn 20 năm chia cắt và ý chí sắt đá 'Nước Việt Nam là một, dân tộc Việt Nam là một'."
    },
    {
        "id": 11,
        "name": "Ha Noi 1972",
        "display_name": "Hà Nội - Điện Biên Phủ trên không",
        "x": 345, "y": 218, "side": "l", "dy": 0,
        "start": 1972, "end": 1975,
        "event_time": "18/12/1972 - 30/12/1972",
        "description": "Trận quyết chiến 12 ngày đêm cuối năm 1972 đập tan pháo đài bay B-52, buộc Mỹ phải ký Hiệp định Paris 1973 rút toàn bộ quân viễn chinh về nước."
    }
]

FALLBACK_INVESTIGATION_DATA = {
    "Ben Nha Rong": {
        "event": "Hành trình tìm đường cứu nước",
        "year": "1911",
        "witness": "Người dân bến cảng",
        "dialogue": "Tôi còn nhớ chiếc tàu buôn Amiral Latouche-Tréville rời cảng Sài Gòn mang theo người thanh niên Văn Ba giàu lòng yêu nước năm 1911.",
        "clues": [
            {"id": "ben_1", "name": "Thẻ thủy thủ tàu Latouche-Tréville", "detail": "Tên đăng ký Văn Ba, lên tàu ngày 5/6/1911 bắt đầu hành trình sang phương Tây."},
            {"id": "ben_2", "name": "Lòng yêu nước thương dân sâu sắc", "detail": "Động lực quyết định thôi thúc người thanh niên yêu nước ra đi tìm con đường cứu nước mới."}
        ]
    },
    "Hong Kong": {
        "event": "Thành lập Đảng Cộng sản Việt Nam",
        "year": "1930",
        "witness": "Cán bộ liên lạc quốc tế",
        "dialogue": "Nhiều tổ chức cộng sản đã được hợp nhất dưới sự chủ trì của đồng chí Nguyễn Ái Quốc tại Hương Cảng vào đầu năm 1930.",
        "clues": [
            {"id": "hk_1", "name": "Mốc thời gian 3/2/1930", "detail": "Hội nghị hợp nhất các tổ chức cộng sản quyết định thành lập Đảng."},
            {"id": "hk_2", "name": "Chánh cương vắn tắt của Đảng", "detail": "Văn kiện thông qua tại Hội nghị vạch ra đường lối giải phóng dân tộc đúng đắn."}
        ]
    },
    "Vinh - Ben Thuy": {
        "event": "Phong trào cách mạng 1930-1931",
        "year": "1930-1931",
        "witness": "Tự vệ đỏ Nghệ Tĩnh",
        "dialogue": "Vinh và Bến Thủy là một trong những địa bàn tiêu biểu của phong trào cách mạng 1930-1931, lập nên chính quyền Xô viết tự quản.",
        "clues": [
            {"id": "vinh_1", "name": "Địa bàn phong trào", "detail": "Vinh - Bến Thủy gắn với cao trào cách mạng 1930-1931."},
            {"id": "vinh_2", "name": "Trống lệnh biểu tình Xô Viết", "detail": "Tiếng trống mở đầu cho cuộc bãi công, biểu tình vũ trang của nhân dân Nghệ - Tĩnh."}
        ]
    },
    "Pac Bo": {
        "event": "Nguyễn Ái Quốc trở về Tổ quốc",
        "year": "1941",
        "witness": "Đồng chí dẫn đường người Tày",
        "dialogue": "Pác Bó gắn với sự kiện Nguyễn Ái Quốc vượt qua mốc 108 trở về Việt Nam đầu năm 1941 sau 30 năm bôn ba.",
        "clues": [
            {"id": "pacbo_1", "name": "Cột mốc biên giới 108", "detail": "Cột mốc lịch sử nơi Bác Hồ đặt bước chân đầu tiên trở về đất mẹ ngày 28/01/1941."},
            {"id": "pacbo_2", "name": "Nghị quyết Trung ương 8 (5/1941)", "detail": "Quyết định đặt nhiệm vụ giải phóng dân tộc lên hàng đầu và thành lập Mặt trận Việt Minh."}
        ]
    },
    "Tan Trao": {
        "event": "Chuẩn bị Tổng khởi nghĩa Tháng Tám",
        "year": "1945",
        "witness": "Đại biểu Quốc dân Đại hội",
        "dialogue": "Tân Trào là thủ đô giải phóng, nơi Quốc dân Đại hội họp ngày 16/8/1945 nhất trí tán thành lệnh Tổng khởi nghĩa.",
        "clues": [
            {"id": "tant_1", "name": "Quân lệnh số 1", "detail": "Ủy ban Khởi nghĩa toàn quốc ban bố lệnh phát động Tổng khởi nghĩa đêm 13/8/1945."}
        ]
    },
    "Ba Dinh": {
        "event": "Đọc Tuyên ngôn Độc lập",
        "year": "1945",
        "witness": "Chiến sĩ Tự vệ Thành Hoàng Diệu",
        "dialogue": "Ngày 2 tháng 9 năm 1945, Chủ tịch Hồ Chí Minh đọc Tuyên ngôn Độc lập tại Quảng trường Ba Đình khai sinh nước VNDCCH.",
        "clues": [
            {"id": "badinh_1", "name": "Bản thảo Tuyên ngôn Độc lập", "detail": "Soạn thảo tại 48 Hàng Ngang, khẳng định quyền độc lập tự do thiêng liêng của dân tộc."}
        ]
    },
    "Viet Bac": {
        "event": "Căn cứ địa kháng chiến chống Pháp",
        "year": "1946-1950",
        "witness": "Chiến sĩ Trung đoàn Thủ đô",
        "dialogue": "Việt Bắc là căn cứ địa quan trọng của cuộc kháng chiến, nơi diễn ra chiến thắng Việt Bắc Thu - Đông 1947 và Biên giới 1950.",
        "clues": [
            {"id": "vietbac_1", "name": "Chỉ thị Phá tan cuộc tấn công mùa đông của giặc Pháp", "detail": "Ban Thường vụ Trung ương Đảng chỉ đạo chiến đấu bảo vệ căn cứ địa Việt Bắc."}
        ]
    },
    "Dien Bien Phu": {
        "event": "Chiến dịch Điện Biên Phủ",
        "year": "1954",
        "witness": "Đại tướng Võ Nguyên Giáp",
        "dialogue": "Chiến dịch Điện Biên Phủ kết thúc thắng lợi ngày 7 tháng 5 năm 1954, đập tan tập đoàn cứ điểm mạnh nhất của Pháp.",
        "clues": [
            {"id": "dbp_1", "name": "Ngày 7-5-1954", "detail": "Cờ Quyết chiến Quyết thắng phất cao trên nóc hầm tướng De Castries lúc 17h30."},
            {"id": "dbp_2", "name": "Lá cờ Quyết chiến Quyết thắng", "detail": "Chiến thắng tạo bước ngoặt chấn động địa cầu kết thúc thắng lợi kháng chiến chống Pháp."}
        ]
    },
    "Dinh Doc Lap": {
        "event": "Chiến dịch Hồ Chí Minh toàn thắng",
        "year": "1975",
        "witness": "Đại đội trưởng xe tăng Bùi Quang Thận",
        "dialogue": "11h30 ngày 30/4/1975, chúng tôi húc đổ cổng sắt Dinh Độc Lập. Tôi chạy lên nóc Dinh cắm lá cờ Mặt trận Dân tộc Giải phóng miền Nam Việt Nam.",
        "clues": [
            {"id": "dinh_1", "name": "Xe tăng 390 và 843", "detail": "Xe tăng húc đổ cánh cổng Dinh Độc Lập lúc 11h30 ngày 30/4/1975."},
            {"id": "dinh_2", "name": "Lá cờ trên nóc Dinh Độc Lập", "detail": "Lá cờ chiến thắng do Bùi Quang Thận cắm đánh dấu sự toàn thắng của Chiến dịch Hồ Chí Minh."}
        ]
    },
    "Hien Luong - Quang Tri": {
        "event": "Khát vọng Thống nhất non sông",
        "year": "1954-1975",
        "witness": "Chiến sĩ công an vũ trang bảo vệ giới tuyến",
        "dialogue": "Cầu Hiền Lương bắc qua sông Bến Hải ở vĩ tuyến 17 là nơi chứng kiến nỗi đau chia cắt đất nước và quyết tâm sắt đá giải phóng miền Nam.",
        "clues": [
            {"id": "hl_1", "name": "Vĩ tuyến 17 Hiệp định Genève", "detail": "Giới tuyến quân sự tạm thời sau năm 1954 chia cắt hai miền Nam - Bắc."},
            {"id": "hl_2", "name": "Cột cờ Hiền Lương", "detail": "Biểu tượng của niềm tin chiến thắng và tinh thần thống nhất Tổ quốc."}
        ]
    },
    "Ha Noi 1972": {
        "event": "Điện Biên Phủ trên không",
        "year": "1972",
        "witness": "Chiến sĩ tên lửa phòng không Hà Nội",
        "dialogue": "Trong 12 ngày đêm cuối năm 1972, lưới lửa phòng không Hà Nội đã bắn rơi hàng chục pháo đài bay B-52 của đế quốc Mỹ.",
        "clues": [
            {"id": "hn_1", "name": "Xác máy bay B-52 rơi hồ Hữu Tiệp", "detail": "Minh chứng cho thất bại thảm hại của cuộc tập kích chiến lược đường không của Mỹ."},
            {"id": "hn_2", "name": "Hiệp định Paris 1973", "detail": "Chiến thắng buộc Mỹ phải ký hiệp định rút hết quân viễn chinh về nước."}
        ]
    }
}

FALLBACK_QUESTIONS = {
    "Ben Nha Rong": [
        {
            "question": "Nguyễn Tất Thành ra đi tìm đường cứu nước từ bến cảng nào vào năm 1911?",
            "options": ["Cảng Đà Nẵng", "Bến Nhà Rồng (Sài Gòn)", "Cảng Hải Phòng", "Cảng Cửa Lò"],
            "answer": 1,
            "explanation": "Ngày 5/6/1911, người thanh niên yêu nước Nguyễn Tất Thành lấy tên Văn Ba rời bến cảng Nhà Rồng ra đi cứu nước."
        }
    ],
    "Hong Kong": [
        {
            "question": "Đảng Cộng sản Việt Nam được thành lập vào ngày tháng năm nào?",
            "options": ["03/02/1930", "02/09/1945", "19/08/1945", "28/01/1941"],
            "answer": 0,
            "explanation": "Ngày 3/2/1930 tại Hương Cảng, Hội nghị hợp nhất các tổ chức cộng sản do Nguyễn Ái Quốc chủ trì đã quyết định thành lập Đảng."
        }
    ],
    "Vinh - Ben Thuy": [
        {
            "question": "Phong trào đấu tranh cách mạng tiêu biểu nhất trong giai đoạn 1930 - 1931 là gì?",
            "options": ["Khởi nghĩa Yên Bái", "Khởi nghĩa Ba Tơ", "Xô viết Nghệ - Tĩnh", "Khởi nghĩa Nam Kỳ"],
            "answer": 2,
            "explanation": "Phong trào Xô viết Nghệ - Tĩnh là đỉnh cao của cao trào cách mạng 1930-1931, lập ra chính quyền của công nông."
        }
    ],
    "Pac Bo": [
        {
            "question": "Nguyễn Ái Quốc trở về Tổ quốc trực tiếp lãnh đạo cách mạng vào thời gian nào?",
            "options": ["Mùa thu năm 1940", "Đầu năm 1941", "Tháng 8 năm 1945", "Cuối năm 1946"],
            "answer": 1,
            "explanation": "Ngày 28/01/1941, Bác qua mốc 108 biên giới Việt - Trung về đến hang Pác Bó (Cao Bằng)."
        }
    ],
    "Tan Trao": [
        {
            "question": "Đại hội Quốc dân Tân Trào (16/8/1945) đã đưa ra quyết định quan trọng nào?",
            "options": ["Ký hiệp định đình chiến", "Tán thành lệnh Tổng khởi nghĩa giành chính quyền", "Kháng chiến toàn quốc", "Đổi tên Đảng"],
            "answer": 1,
            "explanation": "Quốc dân Đại hội Tân Trào đã thông qua lệnh Tổng khởi nghĩa giành chính quyền trước khi quân Đồng minh vào Đông Dương."
        }
    ],
    "Ba Dinh": [
        {
            "question": "Bản Tuyên ngôn Độc lập được Chủ tịch Hồ Chí Minh đọc tại đâu vào ngày 2/9/1945?",
            "options": ["Nhà hát Lớn Hà Nội", "Quảng trường Ba Đình", "Bắc Bộ Phủ", "Đình Tân Trào"],
            "answer": 1,
            "explanation": "Ngày 2/9/1945 tại Quảng trường Ba Đình, Bác Hồ đã đọc bản Tuyên ngôn Độc lập khai sinh nước VNDCCH."
        }
    ],
    "Viet Bac": [
        {
            "question": "Chiến dịch nào đã bảo vệ an toàn cơ quan đầu não kháng chiến trong Thu - Đông 1947?",
            "options": ["Chiến dịch Điện Biên Phủ", "Chiến dịch Tây Bắc", "Chiến dịch Việt Bắc Thu - Đông 1947", "Chiến dịch Biên Giới 1950"],
            "answer": 2,
            "explanation": "Chiến thắng Việt Bắc Thu - Đông 1947 đã phá tan chiến lược đánh nhanh thắng nhanh của giặc Pháp."
        }
    ],
    "Dien Bien Phu": [
        {
            "question": "Chiến dịch Điện Biên Phủ kết thúc thắng lợi hoàn toàn vào ngày nào?",
            "options": ["07/05/1954", "20/07/1954", "02/09/1954", "19/12/1954"],
            "answer": 0,
            "explanation": "Vào lúc 17h30 ngày 07/05/1954, cứ điểm Điện Biên Phủ bị tiêu diệt hoàn toàn, tướng De Castries bị bắt sống."
        }
    ],
    "Dinh Doc Lap": [
        {
            "question": "Chiến dịch Hồ Chí Minh toàn thắng, giải phóng hoàn toàn miền Nam vào ngày nào?",
            "options": ["30/04/1975", "26/03/1975", "01/05/1975", "02/09/1975"],
            "answer": 0,
            "explanation": "11h30 ngày 30/4/1975, lá cờ cách mạng tung bay trên nóc Dinh Độc Lập, đánh dấu Chiến dịch Hồ Chí Minh toàn thắng."
        }
    ],
    "Hien Luong - Quang Tri": [
        {
            "question": "Hiệp định Genève năm 1954 lấy con sông nào làm giới tuyến quân sự tạm thời?",
            "options": ["Sông Bến Hải (Vĩ tuyến 17)", "Sông Gianh", "Sông Hương", "Sông Thạch Hãn"],
            "answer": 0,
            "explanation": "Hiệp định Genève 1954 quy định lấy sông Bến Hải (vĩ tuyến 17) làm giới tuyến quân sự tạm thời giữa hai miền."
        }
    ],
    "Ha Noi 1972": [
        {
            "question": "Trận Điện Biên Phủ trên không đánh bại cuộc tập kích bằng máy bay B-52 của Mỹ diễn ra trong bao nhiêu ngày đêm?",
            "options": ["12 ngày đêm", "7 ngày đêm", "20 ngày đêm", "55 ngày đêm"],
            "answer": 0,
            "explanation": "Cuộc chiến đấu 12 ngày đêm (18/12 - 30/12/1972) của quân dân Hà Nội đã làm nên chiến thắng Điện Biên Phủ trên không lừng lẫy."
        }
    ]
}


# ------------------------------------------------------------------------------
# 3. THUẬT TOÁN CHUYỂN ĐỔI (DATA MAPPING & TRANSFORMATION ALGORITHMS)
# ------------------------------------------------------------------------------
def transform_locations(dia_diem_rows, su_kien_rows):
    """
    Thuật toán:
    1. Lập chỉ mục các sự kiện theo ma_dia_diem.
    2. Duyệt từng dòng địa điểm trong CSDL, tra cứu cấu hình tọa độ trên Map.
    3. Ghép mốc thời gian và tóm tắt sự kiện vào đối tượng địa điểm.
    """
    events_by_loc = {}
    for ev in su_kien_rows:
        loc_id = ev.get("ma_dia_diem")
        if loc_id not in events_by_loc:
            events_by_loc[loc_id] = ev

    result_locations = []
    for row in dia_diem_rows:
        loc_id = row.get("ma_dia_diem")
        cfg = LOCATION_MAP_CONFIG.get(loc_id, {
            "key": row.get("ten_dia_diem", "DiaDiem"),
            "side": "r", "dy": 0,
            "start": 1914, "end": 1954,
            "x": int(row.get("toa_do_x", 300)),
            "y": int(row.get("toa_do_y", 300))
        })

        ev = events_by_loc.get(loc_id, {})
        event_time = ev.get("ngay_thang_chi_tiet") or str(ev.get("nam_dien_ra", ""))
        desc = row.get("mo_ta") or ev.get("tom_tat_dien_bien", "")

        result_locations.append({
            "id": loc_id,
            "name": cfg["key"],
            "display_name": row.get("ten_dia_diem", cfg["key"]),
            "x": cfg["x"],
            "y": cfg["y"],
            "side": cfg["side"],
            "dy": cfg.get("dy", 0),
            "start": cfg["start"],
            "end": cfg["end"],
            "event_time": event_time,
            "description": desc
        })

    # Tự động bổ sung các địa danh mốc 1954 - 1975 (như Dinh Độc Lập) nếu MySQL mới chỉ có 8 mốc đầu
    existing_ids = {loc["id"] for loc in result_locations}
    for fallback_loc in FALLBACK_LOCATIONS:
        if fallback_loc["id"] not in existing_ids:
            result_locations.append(fallback_loc)

    return result_locations


def transform_investigation_data(dia_diem_rows, su_kien_rows, nhan_vat_rows, manh_moi_rows):
    """
    Thuật toán:
    1. Nhóm nhân vật theo ma_dia_diem.
    2. Nhóm manh mối theo ma_su_kien.
    3. Liên kết sự kiện theo ma_dia_diem -> Tạo dictionary phân cấp cho InvestigationScene.
    """
    npcs_by_loc = {}
    for nv in nhan_vat_rows:
        loc_id = nv.get("ma_dia_diem")
        if loc_id not in npcs_by_loc:
            npcs_by_loc[loc_id] = nv

    clues_by_event = {}
    for cl in manh_moi_rows:
        ev_id = cl.get("ma_su_kien")
        if ev_id not in clues_by_event:
            clues_by_event[ev_id] = []
        clues_by_event[ev_id].append({
            "id": str(cl.get("ma_manh_moi", len(clues_by_event[ev_id]) + 1)),
            "name": cl.get("tieu_de_manh_moi", "Manh mối"),
            "detail": cl.get("noi_dung_chi_tiet", "")
        })

    events_by_loc = {}
    for ev in su_kien_rows:
        loc_id = ev.get("ma_dia_diem")
        if loc_id not in events_by_loc:
            events_by_loc[loc_id] = ev

    investigation_dict = {}
    for row in dia_diem_rows:
        loc_id = row.get("ma_dia_diem")
        cfg = LOCATION_MAP_CONFIG.get(loc_id)
        key_name = cfg["key"] if cfg else row.get("ten_dia_diem", "")

        ev = events_by_loc.get(loc_id, {})
        nv = npcs_by_loc.get(loc_id, {})
        ev_id = ev.get("ma_su_kien")
        clues_list = clues_by_event.get(ev_id, [])

        investigation_dict[key_name] = {
            "event": ev.get("ten_su_kien", "Sự kiện lịch sử"),
            "year": str(ev.get("nam_dien_ra", "")),
            "witness": nv.get("ten_nhan_vat", "Nhân chứng lịch sử"),
            "dialogue": nv.get("loi_thoai", "Hãy tìm thêm manh mối để sáng tỏ sự kiện này."),
            "clues": clues_list if clues_list else [
                {"id": f"clue_{loc_id}_1", "name": "Tư liệu sự kiện", "detail": ev.get("tom_tat_dien_bien", "")}
            ]
        }

    # Bổ sung dữ liệu điều tra cho các địa danh 1954 - 1975 nếu thiếu
    for k, v in FALLBACK_INVESTIGATION_DATA.items():
        if k not in investigation_dict:
            investigation_dict[k] = v

    return investigation_dict


def transform_deduction_questions(su_kien_rows, cau_hoi_rows):
    """
    Thuật toán:
    1. Nhóm các câu hỏi trắc nghiệm theo ma_su_kien.
    2. Chuyển đổi đáp án 'A','B','C','D' thành index 0, 1, 2, 3.
    3. Ánh xạ về key địa danh cho DeductionScene.
    """
    questions_by_event = {}
    char_to_index = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

    for q in cau_hoi_rows:
        ev_id = q.get("ma_su_kien")
        if ev_id not in questions_by_event:
            questions_by_event[ev_id] = []

        dap_an_char = str(q.get("dap_an_dung", "A")).strip().upper()
        answer_idx = char_to_index.get(dap_an_char, 0)

        questions_by_event[ev_id].append({
            "question": q.get("noi_dung_cau_hoi", ""),
            "options": [
                q.get("dap_an_a", ""),
                q.get("dap_an_b", ""),
                q.get("dap_an_c", ""),
                q.get("dap_an_d", "")
            ],
            "answer": answer_idx,
            "explanation": q.get("giai_thich_chi_tiet", "")
        })

    deduction_dict = {}
    for ev in su_kien_rows:
        loc_id = ev.get("ma_dia_diem")
        cfg = LOCATION_MAP_CONFIG.get(loc_id)
        if not cfg:
            continue
        key_name = cfg["key"]
        ev_id = ev.get("ma_su_kien")

        if ev_id in questions_by_event and questions_by_event[ev_id]:
            deduction_dict[key_name] = questions_by_event[ev_id]

    return deduction_dict


# ------------------------------------------------------------------------------
# 4. PHƯƠNG THỨC CHÍNH PHỤC VỤ GAME (GAME DATA SERVICE CLASS)
# ------------------------------------------------------------------------------
class GameDataService:
    """Lớp dịch vụ trung tâm cung cấp toàn bộ dữ liệu sạch cho các Scene của Game."""

    def __init__(self):
        self.is_connected = False
        self.status_message = "Chưa kết nối"
        self.locations = FALLBACK_LOCATIONS
        self.investigation_data = FALLBACK_INVESTIGATION_DATA
        self.questions = FALLBACK_QUESTIONS
        self.current_user = None

    def login(self, username, password):
        """Xác thực đăng nhập và tải tiến trình của người chơi từ MySQL."""
        user, msg = authenticate_user(username, password)
        if not user:
            return False, None, msg
        
        self.current_user = user
        progress = self.load_user_progress(user["ma_nguoi_dung"])
        return True, user, progress

    def register(self, username, password, fullname):
        """Đăng ký tài khoản người dùng mới vào MySQL."""
        user, msg = register_user(username, password, fullname)
        if not user:
            return False, None, msg
        
        self.current_user = user
        progress = {
            "score": 0,
            "current_loc_id": 1,
            "max_year": 1914,
            "completed": set()
        }
        return True, user, progress

    def load_user_progress(self, user_id):
        """Tải tiến trình từ bảng tien_do_choi và giải mã sang định dạng game."""
        import json
        row, msg = fetch_user_progress(user_id)
        if not row:
            return {
                "score": 0,
                "current_loc_id": 1,
                "max_year": 1914,
                "completed": set(),
                "task4": self.load_task4_progress(user_id)
            }

        ds_raw = row.get("danh_sach_dia_diem_da_mo") or "[]"
        try:
            completed_list = json.loads(ds_raw)
            if not isinstance(completed_list, list):
                completed_list = []
        except Exception:
            completed_list = []

        completed_set = set()
        for item in completed_list:
            if isinstance(item, int):
                cfg = LOCATION_MAP_CONFIG.get(item)
                if cfg:
                    completed_set.add(cfg["key"])
            else:
                completed_set.add(str(item))

        return {
            "score": int(row.get("diem_tri_thuc") or 0),
            "current_loc_id": int(row.get("ma_dia_diem_hien_tai") or 1),
            "max_year": int(row.get("nam_mo_khoa_cao_nhat") or 1914),
            "completed": completed_set,
            "task4": self.load_task4_progress(user_id)
        }

    def sync_user_progress(self, user_id, current_loc_id, max_year, score, completed_set):
        """Lưu lại tiến độ chơi và điểm số của người chơi vào CSDL MySQL."""
        import json
        ds_json = json.dumps(list(completed_set), ensure_ascii=False)
        return save_user_progress(user_id, current_loc_id, max_year, score, ds_json)

    def load_task4_progress(self, user_id):
        """Load Task 4 clue IDs and quiz attempts; tolerate an unapplied migration."""
        import json
        rows, _ = fetch_task4_progress(user_id)
        result = {}
        for row in rows or []:
            try:
                clue_ids = json.loads(row.get("clue_ids") or "[]")
                if not isinstance(clue_ids, list):
                    clue_ids = []
            except (TypeError, ValueError):
                clue_ids = []
            result[int(row["ma_dia_diem"])] = {
                "clue_ids": set(str(item) for item in clue_ids),
                "quiz_attempts": int(row.get("quiz_attempts") or 0),
            }
        return result

    def sync_task4_progress(self, user_id, location_id, clue_ids, quiz_attempts):
        """Persist one location's Task 4 progress."""
        import json
        return save_task4_progress(
            user_id, location_id,
            json.dumps(sorted(set(clue_ids)), ensure_ascii=False),
            quiz_attempts,
        )

    def get_locations_from_db(self):
        """Lấy danh sách địa điểm từ MySQL hoặc Fallback Cache an toàn."""
        raw_dia_diem, _ = fetch_raw_dia_diem()
        raw_su_kien, _ = fetch_raw_su_kien()
        if raw_dia_diem and len(raw_dia_diem) > 0:
            return transform_locations(raw_dia_diem, raw_su_kien or [])
        return FALLBACK_LOCATIONS

    def load_game_data(self):
        """
        Nạp dữ liệu từ MySQL XAMPP.
        Nếu thành công -> áp dụng thuật toán chuyển đổi và đổ dữ liệu vào.
        Nếu thất bại -> dùng Fallback Cache an toàn và ghi nhận trạng thái.
        """
        print("\n[GameDataService] Đang tải dữ liệu từ CSDL MySQL...")
        raw_dia_diem, status_dd = fetch_raw_dia_diem()
        raw_su_kien, _ = fetch_raw_su_kien()
        raw_nhan_vat, _ = fetch_raw_nhan_vat()
        raw_manh_moi, _ = fetch_raw_manh_moi()
        raw_cau_hoi, _ = fetch_raw_cau_hoi()

        # Kiểm tra xem có lấy được dữ liệu thật từ CSDL không
        if raw_dia_diem and len(raw_dia_diem) > 0:
            try:
                self.locations = transform_locations(raw_dia_diem, raw_su_kien or [])
                self.investigation_data = transform_investigation_data(
                    raw_dia_diem,
                    raw_su_kien or [],
                    raw_nhan_vat or [],
                    raw_manh_moi or []
                )
                self.questions = transform_deduction_questions(raw_su_kien or [], raw_cau_hoi or [])

                # Bổ sung các câu hỏi fallback nếu CSDL chưa có đủ
                for k, v in FALLBACK_QUESTIONS.items():
                    if k not in self.questions:
                        self.questions[k] = v

                self.is_connected = True
                self.status_message = f"CSDL: MySQL Connected ({len(self.locations)} địa điểm)"
                print(f"[GameDataService] THÀNH CÔNG: Đã nạp {len(self.locations)} địa điểm, "
                      f"{len(self.investigation_data)} dữ liệu điều tra, {len(self.questions)} bộ câu hỏi từ MySQL!")
            except Exception as e:
                print(f"[GameDataService] Lỗi khi chuyển đổi dữ liệu SQL: {e}")
                self.use_fallback(f"Lỗi mapping CSDL: {e}")
        else:
            self.use_fallback(f"Không thể kết nối MySQL ({status_dd})")

        return {
            "locations": self.locations,
            "investigation_data": self.investigation_data,
            "questions": self.questions,
            "is_connected": self.is_connected,
            "status_message": self.status_message
        }

    def use_fallback(self, reason):
        """Kích hoạt dữ liệu dự phòng an toàn."""
        self.is_connected = False
        self.status_message = f"CSDL: Offline Cache (Lý do: {reason})"
        self.locations = FALLBACK_LOCATIONS
        self.investigation_data = FALLBACK_INVESTIGATION_DATA
        self.questions = FALLBACK_QUESTIONS
        print(f"[GameDataService] {self.status_message}")


# Khởi tạo một thể hiện dùng chung (Singleton)
game_data_service = GameDataService()
