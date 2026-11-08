"""Dữ liệu danh mục (reference data) dùng cho bộ sinh dữ liệu giả lập và ETL."""
from __future__ import annotations

import re
import unicodedata

# ---------------------------------------------------------------------------
# Khoa / Ngành / Phương thức xét tuyển
# ---------------------------------------------------------------------------
KHOA = [
    ("KHCB", "Khoa Khoa học cơ bản"),
    ("KHMT", "Khoa Khoa học máy tính"),
    ("KTMT", "Khoa Kỹ thuật máy tính và Điện tử"),
    ("KTS", "Khoa Kinh tế số và Thương mại điện tử"),
]

# (ma_nganh, ten_nganh, ma_khoa, he_dao_tao, trọng số nhu cầu, tốc độ tăng/năm)
NGANH = [
    ("IT", "Công nghệ thông tin", "KHMT", "Đại học chính quy", 1.6, 0.08),
    ("CS", "Khoa học máy tính", "KHMT", "Đại học chính quy", 0.9, 0.12),
    ("SE", "Kỹ thuật phần mềm", "KHMT", "Đại học chính quy", 1.1, 0.05),
    ("CE", "Kỹ thuật máy tính", "KTMT", "Đại học chính quy", 0.7, 0.00),
    ("ET", "Công nghệ kỹ thuật điện tử - viễn thông", "KTMT", "Đại học chính quy", 0.6, -0.08),
    ("IOT", "Internet vạn vật", "KTMT", "Chất lượng cao", 0.5, 0.15),
    ("BA", "Quản trị kinh doanh", "KTS", "Đại học chính quy", 0.9, -0.10),
    ("EC", "Thương mại điện tử", "KTS", "Đại học chính quy", 0.8, 0.10),
    ("DM", "Marketing số", "KTS", "Đại học chính quy", 0.7, 0.14),
    ("FT", "Công nghệ tài chính", "KTS", "Chất lượng cao", 0.5, 0.06),
]

# (ma_ptxt, ten, thang_diem, mo_ta, điểm TB, độ lệch chuẩn, ảnh hưởng tới học lực)
PHUONG_THUC = [
    ("HB", "Xét học bạ THPT", 30.0, "Tổng điểm trung bình 3 môn tổ hợp lớp 12", 24.0, 2.3, -0.15),
    ("THPT", "Xét điểm thi tốt nghiệp THPT", 30.0, "Tổng điểm 3 môn thi tốt nghiệp THPT", 21.0, 3.0, 0.10),
    ("DGNL", "Xét điểm thi đánh giá năng lực", 1200.0, "Điểm kỳ thi ĐGNL ĐHQG TP.HCM", 760.0, 110.0, 0.25),
]

# ---------------------------------------------------------------------------
# Tỉnh/thành: (tên chuẩn, vùng miền, trọng số, ảnh hưởng học lực)
# ---------------------------------------------------------------------------
TINH_THANH = [
    ("Đà Nẵng", "Duyên hải Nam Trung Bộ", 22, 0.15),
    ("Quảng Nam", "Duyên hải Nam Trung Bộ", 16, 0.00),
    ("Quảng Ngãi", "Duyên hải Nam Trung Bộ", 9, 0.00),
    ("Bình Định", "Duyên hải Nam Trung Bộ", 6, 0.05),
    ("Phú Yên", "Duyên hải Nam Trung Bộ", 3, -0.05),
    ("Khánh Hòa", "Duyên hải Nam Trung Bộ", 3, 0.05),
    ("Thừa Thiên Huế", "Bắc Trung Bộ", 9, 0.15),
    ("Quảng Trị", "Bắc Trung Bộ", 5, -0.05),
    ("Quảng Bình", "Bắc Trung Bộ", 5, 0.00),
    ("Hà Tĩnh", "Bắc Trung Bộ", 5, 0.20),
    ("Nghệ An", "Bắc Trung Bộ", 6, 0.20),
    ("Thanh Hóa", "Bắc Trung Bộ", 3, 0.05),
    ("Gia Lai", "Tây Nguyên", 4, -0.15),
    ("Đắk Lắk", "Tây Nguyên", 4, -0.10),
    ("Kon Tum", "Tây Nguyên", 3, -0.20),
    ("Lâm Đồng", "Tây Nguyên", 2, 0.00),
    ("Hà Nội", "Đồng bằng sông Hồng", 2, 0.10),
    ("TP. Hồ Chí Minh", "Đông Nam Bộ", 3, 0.05),
]

TINH_THANH_ALIAS = {  # khóa đã bỏ dấu, viết thường, bỏ tiền tố -> tên chuẩn
    "hue": "Thừa Thiên Huế",
    "hcm": "TP. Hồ Chí Minh",
    "tphcm": "TP. Hồ Chí Minh",
    "saigon": "TP. Hồ Chí Minh",
    "daklak": "Đắk Lắk",
    "hn": "Hà Nội",
}

# ---------------------------------------------------------------------------
# Môn học
# ---------------------------------------------------------------------------
MON_DAI_CUONG = [  # 12 môn – học kỳ 1, 2 (khoa KHCB quản lý)
    ("Toán cao cấp A1", 3), ("Triết học Mác - Lênin", 3), ("Tiếng Anh 1", 3),
    ("Tin học đại cương", 3), ("Vật lý đại cương", 3), ("Pháp luật đại cương", 2),
    ("Toán cao cấp A2", 3), ("Kinh tế chính trị Mác - Lênin", 2), ("Tiếng Anh 2", 3),
    ("Xác suất thống kê", 3), ("Kỹ năng mềm", 2), ("Chủ nghĩa xã hội khoa học", 2),
]

# Mỗi khoa 36 môn: 12 cơ sở ngành, 21 chuyên ngành, 3 thực tập/đồ án
MON_THEO_KHOA = {
    "KHMT": [
        "Cấu trúc dữ liệu và giải thuật", "Lập trình hướng đối tượng", "Cơ sở dữ liệu",
        "Toán rời rạc", "Kiến trúc máy tính", "Hệ điều hành", "Mạng máy tính",
        "Lập trình Java", "Phân tích và thiết kế hệ thống", "Công nghệ phần mềm",
        "Lập trình Python", "Lý thuyết đồ thị",
        "Lập trình Web", "Trí tuệ nhân tạo", "Học máy", "Kho dữ liệu", "Khai phá dữ liệu",
        "An toàn thông tin", "Phát triển ứng dụng di động", "Điện toán đám mây",
        "Kiểm thử phần mềm", "Quản lý dự án phần mềm", "Hệ quản trị cơ sở dữ liệu",
        "Xử lý ảnh", "Xử lý ngôn ngữ tự nhiên", "Thị giác máy tính", "Dữ liệu lớn",
        "Lập trình song song", "Đồ họa máy tính", "Chương trình dịch", "Phát triển game",
        "DevOps", "Blockchain căn bản",
        "Thực tập doanh nghiệp (KHMT)", "Đồ án chuyên ngành (KHMT)", "Khóa luận tốt nghiệp (KHMT)",
    ],
    "KTMT": [
        "Mạch điện", "Linh kiện điện tử", "Mạch điện tử tương tự", "Kỹ thuật số",
        "Lập trình C nâng cao", "Tín hiệu và hệ thống", "Kỹ thuật vi xử lý",
        "Xử lý tín hiệu số", "Lý thuyết điều khiển tự động", "Kỹ thuật đo lường",
        "Kiến trúc máy tính nâng cao", "Lập trình hệ thống",
        "Lập trình vi điều khiển", "Hệ thống nhúng", "Thiết kế mạch in", "Thông tin số",
        "Kỹ thuật truyền thông", "Anten và truyền sóng", "Mạng cảm biến không dây",
        "Internet vạn vật", "Thiết kế hệ thống số FPGA", "Điện tử công suất", "Robot học",
        "Hệ điều hành nhúng thời gian thực", "Mạng viễn thông", "Kỹ thuật siêu cao tần",
        "Thiết kế vi mạch VLSI", "Truyền thông di động", "Bảo mật hệ thống IoT",
        "Điện toán biên", "Cơ sở dữ liệu IoT", "Thị giác máy cho hệ nhúng", "Xử lý ảnh số",
        "Thực tập doanh nghiệp (KTMT)", "Đồ án chuyên ngành (KTMT)", "Khóa luận tốt nghiệp (KTMT)",
    ],
    "KTS": [
        "Kinh tế vi mô", "Kinh tế vĩ mô", "Nguyên lý kế toán", "Nguyên lý marketing",
        "Quản trị học", "Tài chính doanh nghiệp", "Thống kê kinh doanh", "Kinh tế lượng",
        "Hệ thống thông tin quản lý", "Thương mại điện tử căn bản", "Hành vi người tiêu dùng",
        "Luật kinh tế",
        "Marketing số", "Quản trị chuỗi cung ứng", "Phân tích dữ liệu kinh doanh",
        "Quản trị dự án", "Luật thương mại điện tử", "Thanh toán điện tử",
        "Quản trị quan hệ khách hàng", "Tiếp thị nội dung", "Tối ưu hóa công cụ tìm kiếm",
        "Quảng cáo trực tuyến", "Quản trị nhân sự", "Quản trị chiến lược",
        "Khởi nghiệp đổi mới sáng tạo", "Công nghệ tài chính", "Ngân hàng số",
        "Phân tích báo cáo tài chính", "Quản trị rủi ro", "Logistics thương mại điện tử",
        "Thiết kế trải nghiệm người dùng", "Kinh doanh quốc tế", "Kỹ năng đàm phán",
        "Thực tập doanh nghiệp (KTS)", "Đồ án chuyên ngành (KTS)", "Khóa luận tốt nghiệp (KTS)",
    ],
}

# Các môn được cố ý làm "khó" để tạo tỷ lệ rớt cao bất thường (phục vụ câu hỏi phân tích 1)
MON_KHO = {
    "Toán cao cấp A1", "Cấu trúc dữ liệu và giải thuật", "Xử lý tín hiệu số", "Kinh tế lượng",
    "Chương trình dịch",
}

HOC_VI = [("Thạc sĩ", 0.55), ("Tiến sĩ", 0.35), ("Phó giáo sư, Tiến sĩ", 0.10)]


# ---------------------------------------------------------------------------
# Hàm chuẩn hóa dùng cho ETL
# ---------------------------------------------------------------------------
def bo_dau(text: str) -> str:
    """Bỏ dấu tiếng Việt: 'Đà Nẵng' -> 'Da Nang'."""
    text = text.replace("đ", "d").replace("Đ", "D")
    nfkd = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in nfkd if unicodedata.category(ch) != "Mn")


def khoa_so_khop(text: str) -> str:
    """Tạo khóa so khớp: bỏ dấu, viết thường, bỏ tiền tố 'TP.', 'Tỉnh', bỏ ký tự đặc biệt."""
    s = bo_dau(str(text)).lower().strip()
    s = re.sub(r"^(?:(?:thanh pho|tp\.?|tinh)\s*)+", "", s)
    return re.sub(r"[^a-z0-9]", "", s)


TINH_THANH_LOOKUP = {khoa_so_khop(ten): ten for ten, *_ in TINH_THANH}
TINH_THANH_LOOKUP.update(TINH_THANH_ALIAS)
VUNG_MIEN = {ten: vung for ten, vung, *_ in TINH_THANH}

