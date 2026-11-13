"""Dữ liệu suy luận dòng thời gian (Timeline Deduction) và ôn tập sử liệu chuẩn học thuật.

Bao gồm 4 mốc lịch sử lớn của cách mạng Việt Nam:
1. Pác Bó (1941) - Nguyễn Ái Quốc về nước lãnh đạo cách mạng & thành lập Mặt trận Việt Minh.
2. Quảng trường Ba Đình (1945) - Tuyên ngôn Độc lập khai sinh nước Việt Nam Dân chủ Cộng hòa.
3. Điện Biên Phủ (1954) - Chiến thắng lừng lẫy năm châu kết thúc 9 năm kháng chiến chống Pháp.
4. Dinh Độc Lập (1975) - Chiến dịch Hồ Chí Minh toàn thắng, giải phóng hoàn toàn miền Nam.

Mỗi địa điểm đều tuân thủ chặt chẽ cấu trúc 4 giai đoạn logic nhân - quả:
  Stage 0: Bối cảnh / Nguyên nhân
  Stage 1: Chủ trương / Hành động
  Stage 2: Diễn biến đỉnh điểm
  Stage 3: Kết quả / Ý nghĩa lịch sử
"""

from .quest_system import Clue

TIMELINE_QUEST_CONFIGS = {
    "Pac Bo": {
        "quest_id": "pac_bo_1941",
        "title": "ÔN TẬP SỬ LIỆU - PÁC BÓ 1941",
        "event_label": "Pác Bó 1941",
        "clues": [
            Clue(
                id="pacbo_testimony",
                title="Lời khai người dẫn đường",
                kind="lời khai",
                detail="Nguyễn Ái Quốc trở về Cao Bằng ngày 28/01/1941 qua mốc 108.",
                source="Hồ Chí Minh: Biên niên tiểu sử, tập 3",
                timeline_stage=0,
            ),
            Clue(
                id="pacbo_resolution",
                title="Nghị quyết Hội nghị TW 8",
                kind="văn kiện",
                detail="Hội nghị tháng 5/1941 xác định giải phóng dân tộc là nhiệm vụ hàng đầu.",
                source="Văn kiện Đảng Toàn tập, tập 7 (1940–1945)",
                timeline_stage=1,
            ),
            Clue(
                id="pacbo_typewriter",
                title="Máy chữ tại căn cứ Pác Bó",
                kind="hiện vật",
                detail="Hiện vật gắn với hoạt động làm việc, soạn thảo tài liệu tại căn cứ.",
                source="Khu di tích quốc gia đặc biệt Pác Bó, hồ sơ trưng bày",
                timeline_stage=2,
            ),
            Clue(
                id="pacbo_vietminh",
                title="Mặt trận Việt Minh ra đời",
                kind="văn kiện",
                detail="Hội nghị Trung ương 8 quyết định thành lập Việt Minh ngày 19/5/1941.",
                source="Văn kiện Đảng Toàn tập, tập 7 (1940–1945)",
                timeline_stage=3,
            ),
        ],
        "questions": [
            {
                "id": "pacbo_q1",
                "question": "Nguyễn Ái Quốc trở về Tổ quốc năm nào?",
                "options": ["1930", "1941", "1945", "1954"],
                "answer": 1,
                "explanation": "Nguyễn Ái Quốc trở về Pác Bó ngày 28/01/1941 sau 30 năm bôn ba.",
                "source": "Hồ Chí Minh: Biên niên tiểu sử, tập 3",
            },
            {
                "id": "pacbo_q2",
                "question": "Hội nghị Trung ương 8 họp vào tháng nào?",
                "options": ["1/1941", "3/1941", "5/1941", "8/1941"],
                "answer": 2,
                "explanation": "Hội nghị diễn ra từ ngày 10 đến 19/5/1941 do đồng chí Nguyễn Ái Quốc chủ trì.",
                "source": "Văn kiện Đảng Toàn tập, tập 7",
            },
            {
                "id": "pacbo_q3",
                "question": "Mặt trận Việt Minh thành lập ngày nào?",
                "options": ["19/5/1941", "2/9/1945", "3/2/1930", "7/5/1954"],
                "answer": 0,
                "explanation": "Mặt trận Việt Minh được quyết định thành lập ngày 19/5/1941 tại Pác Bó.",
                "source": "Văn kiện Đảng Toàn tập, tập 7",
            },
        ],
    },
    "Ba Dinh": {
        "quest_id": "ba_dinh_1945",
        "title": "ÔN TẬP SỬ LIỆU - QUẢNG TRƯỜNG BA ĐÌNH 1945",
        "event_label": "Ba Đình 1945",
        "clues": [
            Clue(
                id="badinh_context",
                title="Cách mạng Tháng Tám toàn thắng",
                kind="văn kiện",
                detail="Cuộc Tổng khởi nghĩa giành chính quyền thắng lợi rực rỡ trên phạm vi cả nước.",
                source="Lịch sử Việt Nam, tập 9 - Viện Sử học",
                timeline_stage=0,
            ),
            Clue(
                id="badinh_draft",
                title="Soạn thảo Tuyên ngôn Độc lập",
                kind="văn kiện",
                detail="Chủ tịch Hồ Chí Minh soạn thảo Tuyên ngôn Độc lập tại ngôi nhà 48 Hàng Ngang.",
                source="Hồ Chí Minh: Biên niên tiểu sử, tập 3",
                timeline_stage=1,
            ),
            Clue(
                id="badinh_ceremony",
                title="Lễ Độc lập ngày 2/9/1945",
                kind="lời khai",
                detail="Hàng chục vạn đồng bào tập hợp lắng nghe Bác đọc Tuyên ngôn Độc lập tại Ba Đình.",
                source="Báo Cứu Quốc, số đặc biệt ngày 5/9/1945",
                timeline_stage=2,
            ),
            Clue(
                id="badinh_birth",
                title="Nước VNDCCH ra đời",
                kind="văn kiện",
                detail="Nước Việt Nam Dân chủ Cộng hòa ra đời, mở ra kỷ nguyên độc lập, tự do cho dân tộc.",
                source="Tuyên ngôn Độc lập ngày 2/9/1945",
                timeline_stage=3,
            ),
        ],
        "questions": [
            {
                "id": "badinh_q1",
                "question": "Bản Tuyên ngôn Độc lập được Bác Hồ soạn thảo tại đâu?",
                "options": ["Hang Pác Bó", "Số nhà 48 Hàng Ngang (Hà Nội)", "Đình Tân Trào", "An toàn khu Định Hóa"],
                "answer": 1,
                "explanation": "Tại căn gác số 48 Hàng Ngang, Chủ tịch Hồ Chí Minh đã khởi thảo bản Tuyên ngôn Độc lập.",
                "source": "Hồ Chí Minh: Biên niên tiểu sử, tập 3",
            },
            {
                "id": "badinh_q2",
                "question": "Chủ tịch Hồ Chí Minh đọc Tuyên ngôn Độc lập tại Ba Đình vào ngày nào?",
                "options": ["19/8/1945", "23/8/1945", "25/8/1945", "2/9/1945"],
                "answer": 3,
                "explanation": "Vào lúc 14 giờ ngày 2/9/1945, Chủ tịch Hồ Chí Minh đọc bản Tuyên ngôn Độc lập lịch sử.",
                "source": "Lịch sử Việt Nam, tập 9 - Viện Sử học",
            },
            {
                "id": "badinh_q3",
                "question": "Bản Tuyên ngôn khẳng định quyền bất khả xâm phạm nào của dân tộc?",
                "options": ["Quyền tự do và độc lập", "Quyền mở rộng lãnh thổ", "Quyền bảo hộ quân sự", "Quyền trung lập hóa"],
                "answer": 0,
                "explanation": "'Nước Việt Nam có quyền hưởng tự do và độc lập, và sự thật đã thành một nước tự do, độc lập.'",
                "source": "Tuyên ngôn Độc lập ngày 2/9/1945",
            },
        ],
    },
    "Dien Bien Phu": {
        "quest_id": "dien_bien_phu_1954",
        "title": "ÔN TẬP SỬ LIỆU - ĐIỆN BIÊN PHỦ 1954",
        "event_label": "Điện Biên Phủ 1954",
        "clues": [
            Clue(
                id="dbp_context",
                title="Tập đoàn cứ điểm Navarre",
                kind="văn kiện",
                detail="Pháp xây dựng Điện Biên Phủ thành 'pháo đài bất khả xâm phạm' với 49 cứ điểm.",
                source="Lịch sử cuộc Kháng chiến chống thực dân Pháp 1945–1954",
                timeline_stage=0,
            ),
            Clue(
                id="dbp_guideline",
                title="Đổi phương châm tác chiến",
                kind="văn kiện",
                detail="Đại tướng Võ Nguyên Giáp quyết định chuyển sang 'Đánh chắc tiến chắc'.",
                source="Điện Biên Phủ - Điểm hẹn lịch sử, Đại tướng Võ Nguyên Giáp",
                timeline_stage=1,
            ),
            Clue(
                id="dbp_climax",
                title="Bắt sống tướng De Castries",
                kind="hiện vật",
                detail="Quân ta tiêu diệt đồi A1, đánh thẳng vào sở chỉ huy bắt sống toàn bộ bộ chỉ huy Pháp chiều 7/5/1954.",
                source="Bảo tàng Chiến thắng Lịch sử Điện Biên Phủ",
                timeline_stage=2,
            ),
            Clue(
                id="dbp_result",
                title="Ký kết Hiệp định Genève",
                kind="văn kiện",
                detail="Chiến thắng chấn động địa cầu buộc thực dân Pháp ký Hiệp định Genève, giải phóng miền Bắc.",
                source="Văn kiện Đảng Toàn tập, tập 15 (1954)",
                timeline_stage=3,
            ),
        ],
        "questions": [
            {
                "id": "dbp_q1",
                "question": "Đại tướng Võ Nguyên Giáp quyết định chuyển phương châm tác chiến sang phương châm nào?",
                "options": ["Đánh nhanh thắng nhanh", "Đánh chắc tiến chắc", "Bao vây cô lập", "Phòng ngự phản công"],
                "answer": 1,
                "explanation": "Quyết định chuyển sang 'Đánh chắc, tiến chắc' là quyết định khó khăn nhất nhưng vô cùng sáng suốt.",
                "source": "Điện Biên Phủ - Điểm hẹn lịch sử",
            },
            {
                "id": "dbp_q2",
                "question": "Tướng chỉ huy quân Pháp bị bắt sống tại cứ điểm Điện Biên Phủ là ai?",
                "options": ["Tướng Navarre", "Tướng De Castries", "Tướng Cogny", "Tướng Salan"],
                "answer": 1,
                "explanation": "17h30 ngày 7/5/1954, tướng De Castries cùng toàn bộ bộ tham mưu tập đoàn cứ điểm bị bắt sống.",
                "source": "Bảo tàng Chiến thắng Lịch sử Điện Biên Phủ",
            },
            {
                "id": "dbp_q3",
                "question": "Thắng lợi Điện Biên Phủ trực tiếp dẫn đến việc ký kết văn kiện ngoại giao nào?",
                "options": ["Hiệp định sơ bộ 6/3", "Hiệp định Genève 1954", "Hiệp định Paris 1973", "Tuyên bố chung Potsdam"],
                "answer": 1,
                "explanation": "Chiến thắng buộc Pháp phải ký Hiệp định Genève chấm dứt chiến tranh, lập lại hòa bình ở Đông Dương.",
                "source": "Văn kiện Đảng Toàn tập, tập 15",
            },
        ],
    },
    "Dinh Doc Lap": {
        "quest_id": "dinh_doc_lap_1975",
        "title": "ÔN TẬP SỬ LIỆU - DINH ĐỘC LẬP 1975",
        "event_label": "Dinh Độc Lập 1975",
        "clues": [
            Clue(
                id="dinh_context",
                title="Thời cơ chiến lược 1975",
                kind="văn kiện",
                detail="Thắng lợi của Chiến dịch Tây Nguyên và Huế - Đà Nẵng tạo thời cơ ngàn năm có một.",
                source="Tổng hành dinh trong Mùa Xuân toàn thắng, Đại tướng Võ Nguyên Giáp",
                timeline_stage=0,
            ),
            Clue(
                id="dinh_order",
                title="Mệnh lệnh 'Thần tốc' của Đại tướng",
                kind="văn kiện",
                detail="Bức điện 7/4/1975: 'Thần tốc, thần tốc hơn nữa; táo bạo, táo bạo hơn nữa; tranh thủ từng giờ, từng phút'.",
                source="Văn kiện Đảng Toàn tập, tập 36 (1975)",
                timeline_stage=1,
            ),
            Clue(
                id="dinh_climax",
                title="Xe tăng húc đổ cổng Dinh",
                kind="hiện vật",
                detail="Xe tăng 390 và 843 húc tung cánh cổng Dinh Độc Lập lúc 11h30 ngày 30/4/1975.",
                source="Bảo tàng Lịch sử Quân sự Việt Nam",
                timeline_stage=2,
            ),
            Clue(
                id="dinh_result",
                title="Chiến dịch Hồ Chí Minh toàn thắng",
                kind="lời khai",
                detail="Dương Văn Minh tuyên bố đầu hàng vô điều kiện, cờ cách mạng tung bay nóc Dinh, non sông thống nhất.",
                source="Lịch sử Kháng chiến chống Mỹ cứu nước 1954–1975",
                timeline_stage=3,
            ),
        ],
        "questions": [
            {
                "id": "dinh_q1",
                "question": "Bức điện lịch sử của Đại tướng Võ Nguyên Giáp ngày 7/4/1975 có mệnh lệnh nổi tiếng nào?",
                "options": [
                    "Quyết tử cho Tổ quốc quyết sinh",
                    "Thần tốc, thần tốc hơn nữa; táo bạo, táo bạo hơn nữa",
                    "Đánh chắc tiến chắc",
                    "Không có gì quý hơn độc lập tự do",
                ],
                "answer": 1,
                "explanation": "'Thần tốc, thần tốc hơn nữa; táo bạo, táo bạo hơn nữa; tranh thủ từng giờ, từng phút xốc tới mặt trận...'",
                "source": "Tổng hành dinh trong Mùa Xuân toàn thắng",
            },
            {
                "id": "dinh_q2",
                "question": "Chiếc xe tăng nào húc tung cánh cổng chính Dinh Độc Lập trưa ngày 30/4/1975?",
                "options": ["Xe tăng 390", "Xe tăng 843", "Xe tăng 985", "Xe tăng 280"],
                "answer": 0,
                "explanation": "Xe tăng 390 do Trung úy Vũ Đăng Toàn chỉ huy đã húc tung cổng chính Dinh Độc Lập vào trưa 30/4/1975.",
                "source": "Bảo tàng Lịch sử Quân sự Việt Nam",
            },
            {
                "id": "dinh_q3",
                "question": "Thắng lợi trưa 30/4/1975 đánh dấu thắng lợi hoàn toàn của chiến dịch lịch sử nào?",
                "options": ["Chiến dịch Tây Nguyên", "Chiến dịch Huế - Đà Nẵng", "Chiến dịch Hồ Chí Minh", "Chiến dịch Đường 9 - Nam Lào"],
                "answer": 2,
                "explanation": "Chiến dịch Hồ Chí Minh lịch sử toàn thắng, chấm dứt 21 năm kháng chiến chống Mỹ cứu nước.",
                "source": "Văn kiện Đảng Toàn tập, tập 36",
            },
        ],
    },
}
