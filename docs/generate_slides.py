"""Tạo slide thuyết trình PowerPoint (.pptx) chuẩn cho buổi bảo vệ đồ án Kho dữ liệu VKU.

Sử dụng thư viện python-pptx để sinh file slide chuyên nghiệp, hiện đại,
bám sát kịch bản thuyết trình và bảng phân công của nhóm 3 người.
"""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 Widescreen
    prs.slide_height = Inches(7.5)

    # Color Palette
    COLOR_PRIMARY = RGBColor(0, 51, 102)     # VKU Deep Blue
    COLOR_SECONDARY = RGBColor(230, 81, 0)   # Orange Accent
    COLOR_DARK = RGBColor(33, 33, 33)        # Charcoal Text
    COLOR_LIGHT = RGBColor(245, 247, 250)    # Soft Background
    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_GRAY = RGBColor(120, 120, 120)

    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category_text="ĐỒ ÁN KHO DỮ LIỆU - VKU"):
        # Header banner
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        
        p0 = tf.paragraphs[0]
        p0.text = category_text.upper()
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = COLOR_SECONDARY

        p1 = tf.add_paragraph()
        p1.text = title_text
        p1.font.size = Pt(24)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_PRIMARY

        # Decorative underline
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.73), Inches(0.04))
        line.fill.solid()
        line.fill.fore_color.rgb = COLOR_SECONDARY
        line.line.color.rgb = COLOR_SECONDARY

    def add_card(slide, left, top, width, height, title, items, fill_color=COLOR_WHITE, border_color=COLOR_PRIMARY):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = fill_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(Inches(left + 0.25), Inches(top + 0.2), Inches(width - 0.5), Inches(height - 0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = COLOR_PRIMARY

        for it in items:
            pi = tf.add_paragraph()
            pi.text = f"• {it}"
            pi.font.size = Pt(13)
            pi.font.color.rgb = COLOR_DARK
            pi.space_before = Pt(6)

    # =========================================================================
    # SLIDE 1: BÌA BÁO CÁO
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_PRIMARY
    bg1.line.fill.background()

    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.333), Inches(4.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN & TRUYỀN THÔNG VIỆT - HÀN"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = RGBColor(200, 220, 240)

    p2 = tf1.add_paragraph()
    p2.text = "BÁO CÁO ĐỒ ÁN MÔN HỌC: KHO DỮ LIỆU"
    p2.font.size = Pt(14)
    p2.font.color.rgb = COLOR_SECONDARY
    p2.space_before = Pt(10)

    p3 = tf1.add_paragraph()
    p3.text = "XÂY DỰNG KHO DỮ LIỆU GIÁO DỤC PHỤC VỤ PHÂN TÍCH ĐIỂM SỐ, TUYỂN SINH VÀ KẾT QUẢ HỌC TẬP"
    p3.font.size = Pt(28)
    p3.font.bold = True
    p3.font.color.rgb = COLOR_WHITE
    p3.space_before = Pt(14)

    p4 = tf1.add_paragraph()
    p4.text = "Giảng viên hướng dẫn: ThS. Mai Lam\nNhóm thực hiện: Cao Huy Hoàng (24ITB050 - Trưởng nhóm) | Võ Nguyễn Thành Long (24ITB105) | Nguyễn Thanh Tùng (24ITB220)"
    p4.font.size = Pt(14)
    p4.font.color.rgb = RGBColor(220, 230, 242)
    p4.space_before = Pt(30)

    # =========================================================================
    # SLIDE 2: ĐẶT VẤN ĐỀ & BỐI CẢNH THỰC TIỄN
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "1. Bối cảnh thực tiễn & Sự cần thiết của Kho dữ liệu")
    add_card(s2, 0.8, 1.8, 5.6, 5.0, "Thách thức của hệ thống OLTP tác vụ", [
        "Hệ thống quản lý đào tạo truyền thống (3NF) tối ưu cho ghi chép từng giao dịch hàng ngày.",
        "Dữ liệu phân tán trên nhiều bảng, truy vấn báo cáo liên bảng (JOIN 7-8 bảng) gây nghẽn hệ thống.",
        "Không lưu vết lịch sử biến động ngành/khoa của sinh viên theo thời gian thực.",
        "Thiếu cơ chế tổng hợp đa chiều phục vụ ra quyết định của Ban Giám hiệu."
    ])
    add_card(s2, 6.9, 1.8, 5.6, 5.0, "Giải pháp: Xây dựng Kho dữ liệu (Data Warehouse)", [
        "Tập trung hóa dữ liệu đào tạo và tuyển sinh thành nguồn chân lý duy nhất (Single Source of Truth).",
        "Mô hình hóa dữ liệu đa chiều theo Lược đồ hình sao (Star Schema) tối ưu tốc độ phân tích.",
        "Ứng dụng kỹ thuật SCD Loại 2 (Slowly Changing Dimension Type 2) bảo toàn lịch sử đổi ngành.",
        "Trực quan hóa tức thời bằng Web Dashboard tương tác và Báo cáo Power BI."
    ])

    # =========================================================================
    # SLIDE 3: MỤC TIÊU & 5 BÀI TOÁN NGHIỆP VỤ OLAP
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "2. Mục tiêu nghiên cứu & 5 Câu hỏi quản trị (OLAP)")
    add_card(s3, 0.8, 1.8, 3.6, 5.0, "Mục tiêu Kỹ thuật", [
        "Xây dựng CSDL nguồn 3NF chuẩn (11 bảng) với > 227.000 dòng.",
        "Pipeline ETL tự động: Lọc lỗi, chuẩn hóa, cách ly bản ghi xấu.",
        "Kho dữ liệu Star Schema (2 Fact, 6 Dim).",
        "Bộ 10 Test Cases kiểm định tự động."
    ])
    add_card(s3, 4.8, 1.8, 7.7, 5.0, "5 Câu hỏi phân tích nghiệp vụ trọng tâm (OLAP Q1 - Q5)", [
        "Q1: Tỷ lệ qua môn và rớt môn theo từng Khoa, Ngành và Môn học qua các năm học (Top môn rớt cao)?",
        "Q2: Điểm trung bình hệ 10 và hệ 4 theo Khoa, Ngành và Khóa học nhằm phát hiện phân hóa chất lượng?",
        "Q3: Mối tương quan giữa Phương thức tuyển sinh đầu vào và Điểm trung bình tích lũy GPA khi tốt nghiệp?",
        "Q4: Xu hướng tuyển sinh, tỷ lệ trúng tuyển và tỷ lệ nhập học thực tế theo từng Ngành học?",
        "Q5: Kết quả học tập và tỷ lệ sinh viên Giỏi/Xuất sắc theo 18 Tỉnh/thành miền Trung - Tây Nguyên?"
    ])

    # =========================================================================
    # SLIDE 4: KIẾN TRÚC TỔNG THỂ HỆ THỐNG
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "3. Kiến trúc tổng thể hệ thống (Architecture)")
    add_card(s4, 0.8, 1.8, 3.6, 5.0, "TẦNG 1: NGUỒN OLTP (3NF)", [
        "CSDL tác vụ: edu_source",
        "11 Bảng chuẩn hóa 3NF",
        "Quy mô: 227.267 dòng đăng ký học phần, 8.012 hồ sơ tuyển sinh",
        "Có chèn lỗi chủ đích: trùng lặp, ngoài thang, thiếu điểm để kiểm thử ETL."
    ])
    add_card(s4, 4.8, 1.8, 3.7, 5.0, "TẦNG 2: ETL & QUARANTINE", [
        "Trích xuất (Extract): Batch 1.000 dòng",
        "Làm sạch (Transform): Kiểm tra miền giá trị, chuẩn hóa tỉnh/thành, điểm chữ",
        "Bảng cách ly: etl_reject (2.537 dòng lỗi)",
        "Nhật ký kiểm toán: etl_log, etl_data_quality",
        "Xử lý SCD Loại 2 trên dim_sinh_vien."
    ])
    add_card(s4, 8.9, 1.8, 3.6, 5.0, "TẦNG 3: KHO DỮ LIỆU & BI", [
        "CSDL kho: edu_dw (Star Schema)",
        "Fact Kết quả học tập (224.778 dòng sạch)",
        "Fact Tuyển sinh (7.964 dòng sạch)",
        "6 Bảng Chiều (Dimensions)",
        "Giao diện: Web Dashboard MVC & Power BI."
    ])

    # =========================================================================
    # SLIDE 5: THIẾT KẾ KHO DỮ LIỆU STAR SCHEMA
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "4. Thiết kế Kho dữ liệu đa chiều (Star Schema)")
    add_card(s5, 0.8, 1.8, 5.6, 5.0, "2 Bảng Fact trung tâm (Fact Tables)", [
        "fact_ket_qua_hoc_tap: Lưu trữ từng lượt học phần của sinh viên (diem_qua_trinh, diem_thi, diem_tong_ket, diem_he_4, diem_chu, ket_qua Đạt/Rớt).",
        "fact_tuyen_sinh: Lưu trữ hồ sơ tuyển sinh (diem_xet_tuyen, trang_thai trúng tuyển, da_nhap_hoc, nam_tuyen_sinh).",
        "Đặc điểm: Toàn bộ khóa ngoại liên kết tới Dimension đều là Khóa thay thế (Surrogate Key kiểu số nguyên), tăng tốc truy vấn tối đa."
    ])
    add_card(s5, 6.9, 1.8, 5.6, 5.0, "6 Bảng Chiều chuẩn hóa (Dimensions)", [
        "dim_sinh_vien: Hỗ trợ SCD Loại 2 (ngay_hieu_luc, ngay_het_han, is_current).",
        "dim_hoc_phan: Môn học, số tín chỉ, loại môn (Đại cương / Chuyên ngành).",
        "dim_giang_vien: Giảng viên, học vị (Tiến sĩ, Thạc sĩ), đơn vị công tác.",
        "dim_thoi_gian: Chiều conformed biểu diễn từng ngày từ 2019-2027.",
        "dim_nganh: Ngành đào tạo, Khoa trực thuộc, hệ đào tạo.",
        "dim_tinh_thanh & dim_phuong_thuc_xt: Danh mục chuẩn hóa."
    ])

    # =========================================================================
    # SLIDE 6: KỸ THUẬT SLOWLY CHANGING DIMENSION TYPE 2 (SCD2)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "5. Quản lý chiều biến đổi chậm: SCD Loại 2")
    add_card(s6, 0.8, 1.8, 5.6, 5.0, "Nguyên lý SCD Loại 2 trong Đề tài", [
        "Khi sinh viên đổi ngành (khoảng 3% sinh viên đầu năm 2):",
        "KHÔNG ghi đè dữ liệu cũ (SCD1 làm mất lịch sử điểm số của ngành trước đó).",
        "TẠO BẢN GHI MỚI trong dim_sinh_vien với surrogate key mới.",
        "Đóng phiên bản cũ: ngay_het_han = ngày đổi ngành - 1, is_current = 0.",
        "Mở phiên bản mới: ngay_hieu_luc = ngày đổi ngành, ngay_het_han = 9999-12-31, is_current = 1."
    ])
    add_card(s6, 6.9, 1.8, 5.6, 5.0, "Thực nghiệm kiểm chứng (Sinh viên 19IT001)", [
        "Sinh viên: Trần Văn Phúc (19IT001).",
        "Phiên bản 1: Ngành IT (Công nghệ thông tin) từ 2019-09-01 đến 2021-08-19 (is_current = 0).",
        "Phiên bản 2: Ngành SE (Kỹ thuật phần mềm) từ 2021-08-20 đến 9999-12-31 (is_current = 1).",
        "Kết quả: Điểm các kỳ 2019-2020 gắn với ngành IT, điểm các kỳ sau gắn với ngành SE.",
        "Kiểm tra tính Idempotent: Chạy lại ETL nhiều lần không bị trùng lặp khóa."
    ])

    # =========================================================================
    # SLIDE 7: BỘ 10 TEST CASES KIỂM THỬ CHẤT LƯỢNG DỮ LIỆU
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "6. Kiểm thử chất lượng dữ liệu: 10/10 Test Cases PASS")
    add_card(s7, 0.8, 1.8, 11.7, 5.0, "Bảng tổng hợp kết quả kiểm thử tự động (tests/run_dq_tests.py)", [
        "TC01 (Quy mô dữ liệu): Fact học tập đạt 224.778 dòng (Yêu cầu >= 100.000 dòng) -> PASS",
        "TC02 (Đối soát nguồn - kho): Nguồn 227.267 = Fact 224.778 + Reject 2.489 dòng -> PASS",
        "TC03 (Đối soát tuyển sinh): Nguồn 8.012 = Fact 7.964 + Reject 48 dòng -> PASS",
        "TC04 (Đối soát sinh viên): 4.948 sinh viên nguồn = 4.948 bản ghi is_current=1 trong kho -> PASS",
        "TC05 (Miền giá trị điểm): 0 dòng NULL hoặc ngoài thang [0, 10] trong Fact -> PASS",
        "TC06 (Công thức đào tạo): 0 dòng lệch công thức ROUND(0.4*QT + 0.6*Thi, 1) -> PASS",
        "TC07 (Grain duy nhất): 0 trường hợp trùng lặp cặp (sinh_vien, lop_hoc_phan) -> PASS",
        "TC08 (Toàn vẹn khóa ngoại): 0 dòng mồ côi (Orphan FK) giữa Fact và Dimension -> PASS",
        "TC09 (Chuẩn hóa danh mục): 0 giá trị tỉnh/thành hoặc giới tính lạ -> PASS",
        "TC10 (Tính đúng đắn SCD2): 149 phiên bản lịch sử đổi ngành, 0 bản ghi chồng lấn thời gian -> PASS"
    ])

    # =========================================================================
    # SLIDE 8: ĐÁNH GIÁ HIỆU NĂNG: OLTP 3NF vs STAR SCHEMA
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "7. Đánh giá hiệu năng truy vấn (Benchmark)")
    add_card(s8, 0.8, 1.8, 5.6, 5.0, "Kết quả đo lường thực tế (225.000 dòng)", [
        "Q1 (Tỷ lệ rớt theo Khoa/Môn): OLTP 3NF mất 1.854 ms vs Kho Star Schema mất 919 ms -> Nhanh hơn 2.02 lần (Tăng tốc 102%).",
        "Q2 (Điểm TB Khoa/Ngành/Năm): OLTP 3NF mất 4.796 ms vs Kho Star Schema mất 4.280 ms -> Nhanh hơn 1.12 lần.",
        "Q3 (Kết quả theo Giảng viên/Học vị): OLTP 3NF mất 3.442 ms vs Kho Star Schema mất 2.515 ms -> Nhanh hơn 1.37 lần.",
        "Tổng kết: Lược đồ Star Schema giảm số phép JOIN liên bảng, sử dụng Surrogate Keys số nguyên và Index tối ưu hơn hẳn 3NF."
    ])
    add_card(s8, 6.9, 1.8, 5.6, 5.0, "Ý nghĩa thực tiễn đối với hệ thống", [
        "Hạn chế nghẽn đường truyền (Bottleneck) trên CSDL tác vụ khi phòng đào tạo trích xuất báo cáo.",
        "Thời gian phản hồi truy vấn dưới 1 giây đáp ứng tiêu chuẩn thời gian thực cho Dashboard.",
        "Khả năng mở rộng quy mô (Scalability) tốt khi dữ liệu trường tăng lên hàng triệu dòng qua nhiều khóa học."
    ])

    # =========================================================================
    # SLIDE 9: KẾT QUẢ PHÂN TÍCH 5 CÂU HỎI NGHIỆP VỤ (INSIGHTS)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "8. Phát hiện nổi bật từ 5 góc nhìn phân tích (OLAP)")
    add_card(s9, 0.8, 1.8, 5.6, 5.0, "Chất lượng học tập & Tuyển sinh", [
        "Top môn rớt cao: Các môn kỹ thuật cốt lõi (Cấu trúc dữ liệu, Giải thuật, Kiến trúc máy tính) có tỷ lệ rớt từ 5.2% - 7.8% -> Cần phụ đạo đầu kỳ.",
        "Tương quan Điểm tuyển sinh & GPA: Thí sinh trúng tuyển từ 24-27 điểm có GPA đại học trung bình đạt 3.29/4.0 (rớt chỉ 0.04%), cao vượt trội so với nhóm 18-21 điểm (GPA 2.18, rớt 29%).",
        "Xu hướng tuyển sinh: Ngành Công nghệ thông tin và Kỹ thuật phần mềm giữ tỷ lệ nhập học > 88% qua các năm."
    ])
    add_card(s9, 6.9, 1.8, 5.6, 5.0, "Địa phương & Hiệu quả giảng dạy", [
        "Phân bổ địa lý: Thí sinh các tỉnh Thừa Thiên Huế, Quảng Nam, Đà Nẵng, Quảng Trị chiếm số lượng lớn; chất lượng học lực giữa các tỉnh đồng đều (tỷ lệ qua môn > 98.6%).",
        "Hiệu quả giảng viên: Lớp do giảng viên có học vị Tiến sĩ giảng dạy có tỷ lệ sinh viên đạt điểm Giỏi/Xuất sắc cao hơn 6-8% so với mặt bằng chung.",
        "Khuyến nghị: Nhà trường nên phân bổ ngân sách phụ đạo cho các môn tỷ lệ rớt cao và đẩy mạnh chỉ tiêu tuyển sinh vào các ngành có nhu cầu xã hội lớn."
    ])

    # =========================================================================
    # SLIDE 10: ỨNG DỤNG WEB DASHBOARD THEO KIẾN TRÚC MVC
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "9. Ứng dụng Web Dashboard phân tích (Kiến trúc MVC)")
    add_card(s10, 0.8, 1.8, 5.6, 5.0, "Kiến trúc phần mềm MVC chuẩn", [
        "Model: olap_model.py, scd2_model.py, etl_model.py, sql_model.py (Truy vấn SQLAlchemy và xử lý dữ liệu lõi).",
        "View: web/index.html (Single Page App với biểu đồ tương tác Chart.js), view.py (Đóng gói JSON API).",
        "Controller: olap_controller.py, scd2_controller.py, etl_controller.py, router.py (Điều hướng nghiệp vụ).",
        "Lợi ích: Tách biệt hoàn toàn tầng dữ liệu và hiển thị, dễ bảo trì và mở rộng."
    ])
    add_card(s10, 6.9, 1.8, 5.6, 5.0, "Các tính năng chính trên Giao diện Web", [
        "Chạy nhanh bằng 1 click qua file chay_web.bat tại cổng http://localhost:8050.",
        "Trang Dashboard trực quan: 5 Biểu đồ phân tích OLAP với bộ lọc tương tác.",
        "Trang Kiểm thử & ETL: Xem trạng thái 10 Test Cases, nhật ký ETL và danh sách dòng reject.",
        "Trang SCD2 Explorer: Tra cứu lịch sử phiên bản sinh viên trực quan.",
        "Trang SQL Console: Cho phép giảng viên gõ trực tiếp câu lệnh SQL truy vấn kho."
    ])

    # =========================================================================
    # SLIDE 11: PHÂN CÔNG NHIỆM VỤ THÀNH VIÊN
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "10. Phân công công việc & Đóng góp của các thành viên")
    add_card(s11, 0.8, 1.8, 3.6, 5.0, "Cao Huy Hoàng (24ITB050)\nTrưởng nhóm - Data Engineer", [
        "Chịu trách nhiệm thiết kế kiến trúc toàn hệ thống.",
        "Xây dựng CSDL nguồn 3NF và CSDL kho Star Schema.",
        "Lập trình Pipeline ETL tự động bằng Python và Stored Procedures.",
        "Lập trình Web Dashboard MVC.",
        "Mức độ hoàn thành: 100%."
    ])
    add_card(s11, 4.8, 1.8, 3.7, 5.0, "Võ Nguyễn Thành Long (24ITB105)\nData Modeler & Analyst", [
        "Khảo sát tài liệu và 5 công trình nghiên cứu quốc tế liên quan.",
        "Thiết kế sơ đồ ERD 3NF và Lược đồ hình sao (Star Schema).",
        "Lập bảng ánh xạ dữ liệu nguồn - đích (Source-to-Target Data Mapping).",
        "Biên soạn Báo cáo toàn văn đồ án.",
        "Mức độ hoàn thành: 100%."
    ])
    add_card(s11, 8.9, 1.8, 3.6, 5.0, "Nguyễn Thanh Tùng (24ITB220)\nQA & BI Specialist", [
        "Xây dựng bộ 10 kịch bản kiểm thử chất lượng dữ liệu (DQ Tests).",
        "Thực hiện đo lường hiệu năng truy vấn (Benchmark OLTP vs Star Schema).",
        "Viết truy vấn OLAP cho 5 câu hỏi quản trị và thiết kế Power BI.",
        "Soạn kịch bản và chuẩn bị Slide thuyết trình.",
        "Mức độ hoàn thành: 100%."
    ])

    # =========================================================================
    # SLIDE 12: KẾT LUẬN & HƯỚNG MỞ RỘNG
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "11. Kết luận & Hướng phát triển")
    add_card(s12, 0.8, 1.8, 5.6, 5.0, "Kết quả đạt được", [
        "Hoàn thành toàn diện bài toán Kho dữ liệu giáo dục đại học với quy mô lớn (> 227.000 dòng).",
        "Hiện thực hóa đầy đủ các kỹ thuật nâng cao: Star Schema, Slowly Changing Dimension Type 2, Stored Procedures, Data Quality Quarantine.",
        "Chứng minh hiệu quả thực tế qua Benchmark (tăng tốc gấp 2.02 lần) và 10/10 Test Cases PASS.",
        "Sản phẩm đầu ra trọn gói: Mã nguồn Git, Web Dashboard MVC, Báo cáo Word và Power BI."
    ])
    add_card(s12, 6.9, 1.8, 5.6, 5.0, "Hướng phát triển tương lai", [
        "Tích hợp mô hình Học máy (Machine Learning) để dự báo sớm sinh viên có nguy cơ rớt môn/buộc thôi học ngay từ giữa kỳ.",
        "Nâng cấp kiến trúc ETL thành Streaming Data Pipeline bằng Apache Kafka / Spark Streaming phục vụ chấm điểm trực tuyến.",
        "Triển khai Kho dữ liệu lên nền tảng Điện toán đám mây (Google Cloud BigQuery / Snowflake) phục vụ toàn thể Đại học Đà Nẵng."
    ])

    # =========================================================================
    # SLIDE 13: KẾT THÚC & Q&A
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    bg13 = s13.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg13.fill.solid()
    bg13.fill.fore_color.rgb = COLOR_PRIMARY
    bg13.line.fill.background()

    tb13 = s13.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(11.333), Inches(3.5))
    tf13 = tb13.text_frame
    tf13.word_wrap = True

    p = tf13.paragraphs[0]
    p.text = "XIN CHÂN THÀNH CẢM ƠN THẦY CÔ VÀ CÁC BẠN ĐÃ LẮNG NGHE!"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE

    p2 = tf13.add_paragraph()
    p2.text = "Kính mong nhận được sự góp ý và đánh giá từ Thầy Mai Lam và Hội đồng"
    p2.alignment = PP_ALIGN.CENTER
    p2.font.size = Pt(18)
    p2.font.color.rgb = COLOR_SECONDARY
    p2.space_before = Pt(20)

    p3 = tf13.add_paragraph()
    p3.text = "NHÓM THỰC HIỆN: CAO HUY HOÀNG - VÕ NGUYỄN THÀNH LONG - NGUYỄN THANH TÙNG\nTrường Đại học Công nghệ Thông tin & Truyền thông Việt - Hàn (VKU)"
    p3.alignment = PP_ALIGN.CENTER
    p3.font.size = Pt(14)
    p3.font.color.rgb = RGBColor(200, 220, 240)
    p3.space_before = Pt(25)

    out_file = Path("docs/Slide_Thuyet_Trinh_Kho_du_lieu.pptx")
    prs.save(out_file)
    print(f"Đã tạo file slide PowerPoint tại: {out_file}")

if __name__ == "__main__":
    create_presentation()
