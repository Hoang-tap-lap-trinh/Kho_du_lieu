"""Tạo slide thuyết trình PowerPoint (.pptx) chuẩn cho buổi bảo vệ đồ án Kho dữ liệu VKU.

Sử dụng thư viện python-pptx để sinh file slide chuyên nghiệp, hiện đại,
bám sát kịch bản thuyết trình, chuẩn kiến thức môn học (Conceptual/Logical/Physical DW,
Hierarchies, SCD2, OLAP, Benchmark) và bảng phân công của nhóm 3 người.
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

    # Color Palette - VKU Identity
    COLOR_PRIMARY = RGBColor(0, 51, 102)     # VKU Deep Blue (#003366)
    COLOR_SECONDARY = RGBColor(230, 81, 0)   # Orange Accent (#E65100)
    COLOR_DARK = RGBColor(33, 33, 33)        # Charcoal Text (#212121)
    COLOR_LIGHT = RGBColor(245, 247, 250)    # Soft Background
    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_GRAY = RGBColor(110, 110, 110)
    COLOR_ACCENT_BG = RGBColor(238, 244, 250)

    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category_text="ĐỒ ÁN KHO DỮ LIỆU - VKU"):
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.7), Inches(1.15))
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
        p1.font.size = Pt(22)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_PRIMARY
        p1.space_before = Pt(3)

        # Decorative underline
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.73), Inches(0.04))
        line.fill.solid()
        line.fill.fore_color.rgb = COLOR_SECONDARY
        line.line.color.rgb = COLOR_SECONDARY

    def add_card(slide, left, top, width, height, title, items, fill_color=COLOR_WHITE, border_color=COLOR_PRIMARY, title_color=COLOR_PRIMARY):
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
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = title_color

        for it in items:
            pi = tf.add_paragraph()
            pi.text = f"• {it}"
            pi.font.size = Pt(12)
            pi.font.color.rgb = COLOR_DARK
            pi.space_before = Pt(5)

    # =========================================================================
    # SLIDE 1: BÌA BÁO CÁO
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_PRIMARY
    bg1.line.fill.background()

    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.1), Inches(11.333), Inches(5.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN & TRUYỀN THÔNG VIỆT - HÀN (VKU)"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = RGBColor(200, 220, 240)

    p2 = tf1.add_paragraph()
    p2.text = "BÁO CÁO ĐỒ ÁN MÔN HỌC: KHO DỮ LIỆU & OLAP"
    p2.font.size = Pt(14)
    p2.font.color.rgb = COLOR_SECONDARY
    p2.space_before = Pt(8)

    p3 = tf1.add_paragraph()
    p3.text = "XÂY DỰNG KHO DỮ LIỆU GIÁO DỤC PHỤC VỤ PHÂN TÍCH ĐIỂM SỐ, TUYỂN SINH VÀ KẾT QUẢ HỌC TẬP"
    p3.font.size = Pt(26)
    p3.font.bold = True
    p3.font.color.rgb = COLOR_WHITE
    p3.space_before = Pt(14)

    p4 = tf1.add_paragraph()
    p4.text = "Giảng viên hướng dẫn: ThS. Mai Lam\n" \
              "Nhóm thực hiện: Cao Huy Hoàng (24ITB050 - Trưởng nhóm) | Võ Nguyễn Thành Long (24ITB105) | Nguyễn Thanh Tùng (24ITB220)\n" \
              "Đà Nẵng, Học kỳ I - Năm học 2026-2027"
    p4.font.size = Pt(13)
    p4.font.color.rgb = RGBColor(220, 230, 242)
    p4.space_before = Pt(28)

    # =========================================================================
    # SLIDE 2: ĐẶT VẤN ĐỀ & BỐI CẢNH THỰC TIỄN
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "1. Bối cảnh thực tiễn & Sự cần thiết của Kho dữ liệu")
    add_card(s2, 0.8, 1.8, 5.6, 5.1, "Hạn chế của hệ thống CSDL tác vụ (OLTP - 3NF)", [
        "Tối ưu cho thao tác ghi giao dịch hàng ngày (nhập điểm, đăng ký môn), không tối ưu cho truy vấn phân tích.",
        "Dữ liệu phân tán trên nhiều bảng; các báo cáo quản trị phải JOIN 7-8 bảng gây nghẽn tài nguyên CSDL trường.",
        "Không lưu vết lịch sử biến động (khi sinh viên chuyển ngành/lớp, cập nhật đè làm sai lệch thống kê quá khứ).",
        "Dữ liệu thô tồn tại nhiều bất thường (trùng lặp, điểm ngoài thang đo, thiếu điểm, gõ sai địa danh)."
    ])
    add_card(s2, 6.9, 1.8, 5.6, 5.1, "Giải pháp: Xây dựng Kho dữ liệu (Data Warehouse)", [
        "Tập trung hóa dữ liệu đào tạo và tuyển sinh thành nguồn chân lý duy nhất (Single Source of Truth).",
        "Áp dụng quy trình ETL tự động hóa để làm sạch và cách ly bản ghi vi phạm vào bảng kiểm dịch.",
        "Mô hình hóa dữ liệu đa chiều Star Schema (đa Fact, dùng chung Conformed Dimensions) tăng tốc truy vấn.",
        "Ứng dụng kỹ thuật SCD Loại 2 (Slowly Changing Dimension Type 2) bảo toàn trọn vẹn lịch sử đào tạo.",
        "Trực quan hóa đa chiều tức thời qua Web MVC Dashboard và báo cáo Power BI."
    ])

    # =========================================================================
    # SLIDE 3: MỤC TIÊU & 5 BÀI TOÁN NGHIỆP VỤ OLAP
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "2. Mục tiêu nghiên cứu & 5 Câu hỏi quản trị (OLAP Q1 - Q5)")
    add_card(s3, 0.8, 1.8, 3.6, 5.1, "Mục tiêu Kỹ thuật", [
        "Xây dựng CSDL nguồn 3NF chuẩn (11 bảng) với > 227.000 dòng.",
        "Pipeline ETL tự động: Lọc lỗi, chuẩn hóa, cách ly bản ghi xấu vào etl_reject.",
        "Kho dữ liệu Star Schema (2 Fact, 6 Dim, Surrogate Keys).",
        "Bộ 10 Test Cases kiểm định tự động đạt PASS 100%.",
        "Đo lường Benchmark tăng tốc truy vấn."
    ])
    add_card(s3, 4.8, 1.8, 7.7, 5.1, "5 Câu hỏi phân tích nghiệp vụ trọng tâm (OLAP Q1 - Q5)", [
        "Q1 (Học phần & Tỷ lệ qua môn): Phân tích tỷ lệ Đạt/Rớt môn theo Khoa, Ngành, Môn học qua từng học kỳ và xác định Top 15 môn có tỷ lệ rớt cao nhất?",
        "Q2 (Chất lượng đào tạo): Thống kê Điểm trung bình (hệ 10 và hệ 4) theo Khoa, Ngành và Khóa học nhằm phát hiện sự phân hóa chất lượng?",
        "Q3 (Đầu vào vs Đầu ra): Mối tương quan giữa Phương thức tuyển sinh đầu vào (Học bạ, THPT, ĐGNL) với kết quả GPA năm nhất và GPA tích lũy?",
        "Q4 (Quy luật tuyển sinh): Xu hướng tuyển sinh, tỷ lệ trúng tuyển và tỷ lệ nhập học thực tế theo từng ngành qua 4 năm (2019-2022)?",
        "Q5 (Phân bổ vùng miền): Kết quả học tập và tỷ lệ sinh viên Giỏi/Xuất sắc theo 18 Tỉnh/thành miền Trung - Tây Nguyên?"
    ])

    # =========================================================================
    # SLIDE 4: KIẾN TRÚC TỔNG THỂ HỆ THỐNG
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "3. Kiến trúc tổng thể hệ thống (End-to-End Pipeline)")
    add_card(s4, 0.8, 1.8, 3.6, 5.1, "TẦNG 1: NGUỒN OLTP (3NF)", [
        "CSDL tác vụ: edu_source",
        "11 Bảng chuẩn hóa 3NF liên kết chặt chẽ.",
        "Quy mô: 227.267 dòng đăng ký học phần, 8.012 hồ sơ tuyển sinh.",
        "Chèn lỗi chủ đích: 905 dòng trùng lặp, 905 dòng thiếu điểm, 679 dòng điểm ngoài [0,10], 671 dòng sai điểm TK."
    ])
    add_card(s4, 4.8, 1.8, 3.7, 5.1, "TẦNG 2: ETL & QUARANTINE", [
        "Extract: Đọc phân đoạn từ 11 bảng nguồn.",
        "Transform: Kiểm tra miền giá trị, chuẩn hóa chuỗi, tính điểm hệ 4 và điểm chữ.",
        "Quarantine: Bắt và cách ly 2.537 dòng sai vào bảng etl_reject kèm lý do cụ thể.",
        "Audit Log: Ghi vết etl_log và etl_data_quality.",
        "Xử lý SCD2: Stored Procedure cho dim_sinh_vien."
    ])
    add_card(s4, 8.9, 1.8, 3.6, 5.1, "TẦNG 3: KHO DỮ LIỆU & BI", [
        "CSDL kho: edu_dw (Star Schema).",
        "2 Fact sạch: fact_ket_qua_hoc_tap (224.778 dòng) và fact_tuyen_sinh (7.964 dòng).",
        "6 Conformed Dimensions dùng chung.",
        "Giao diện: Web Dashboard MVC (8050) và Báo cáo tương tác Power BI DAX."
    ])

    # =========================================================================
    # SLIDE 5: THIẾT KẾ KHO DỮ LIỆU STAR SCHEMA & HIERARCHIES
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "4. Thiết kế Kho dữ liệu đa chiều (Star Schema & Hierarchies)")
    add_card(s5, 0.8, 1.8, 5.6, 5.1, "Mô hình Multi-Star & Conformed Dimensions", [
        "fact_ket_qua_hoc_tap: Từng lượt học phần của sinh viên (diem_qt, diem_thi, diem_tk, diem_he_4, diem_chu, ket_qua Đạt/Rớt).",
        "fact_tuyen_sinh: Điểm xét tuyển quy đổi thang 30, trạng thái trúng tuyển, nhập học.",
        "Shared Dimensions: Cả 2 Fact liên kết chặt qua dim_sinh_vien, dim_nganh, dim_thoi_gian (phục vụ đối chiếu chéo Tuyển sinh vs Điểm số).",
        "Surrogate Keys: 100% sử dụng khóa thay thế số nguyên tự tăng, độc lập khóa nghiệp vụ tự nhiên."
    ])
    add_card(s5, 6.9, 1.8, 5.6, 5.1, "Cây phân cấp phân tích (Hierarchies theo bài giảng)", [
        "Balanced Hierarchy (Phân cấp cân bằng):",
        "  • Đào tạo: Ngành -> Khoa",
        "  • Địa lý: Tỉnh/Thành -> Vùng miền (18 tỉnh miền Trung - Tây Nguyên)",
        "Parallel Hierarchies (Phân cấp song song trên dim_thoi_gian):",
        "  • Nhánh 1 (Lịch tự nhiên): Ngày -> Tháng -> Quý -> Năm",
        "  • Nhánh 2 (Niên giám đào tạo): Ngày -> Học kỳ (HK1, HK2) -> Năm học",
        "Hỗ trợ các thao tác Roll-up / Drill-down linh hoạt giữa các cấp độ."
    ])

    # =========================================================================
    # SLIDE 6: KỸ THUẬT SLOWLY CHANGING DIMENSION TYPE 2 (SCD2)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "5. Quản lý chiều biến đổi chậm: SCD Loại 2 (dim_sinh_vien)")
    add_card(s6, 0.8, 1.8, 5.6, 5.1, "Nguyên lý SCD Loại 2 trong Đề tài", [
        "Nghiệp vụ thực tế: Sinh viên có thể chuyển ngành hoặc chuyển lớp sau năm thứ nhất (khoảng 3%).",
        "Nếu dùng SCD1: Ghi đè ngành mới sẽ làm sai lệch báo cáo điểm các kỳ trước đó thuộc ngành cũ.",
        "Giải pháp SCD2:",
        "  • Đóng bản ghi cũ: ngay_het_han = ngày đổi ngành - 1 ngày, is_current = 0.",
        "  • Mở bản ghi mới: ngay_hieu_luc = ngày đổi ngành, ngay_het_han = 9999-12-31, is_current = 1, sinh surrogate key mới.",
        "  • Điểm các kỳ trước tự động tra cứu đúng phiên bản theo khoảng ngày học kỳ."
    ])
    add_card(s6, 6.9, 1.8, 5.6, 5.1, "Thực nghiệm kiểm chứng (Sinh viên 19IT001)", [
        "Sinh viên: Trần Văn Phúc (19IT001).",
        "Phiên bản 1 (key=871): Ngành IT từ 2019-09-01 đến 2021-08-19 (is_current = 0).",
        "Phiên bản 2 (key=8192): Chuyển sang ngành SE từ 2021-08-20 đến 9999-12-31 (is_current = 1).",
        "Kết quả tra cứu Fact: Điểm 4 học kỳ đầu gắn với ngành IT; điểm các học kỳ sau gắn với ngành SE.",
        "Tính Idempotent: Chạy lại pipeline ETL nhiều lần kết quả vẫn bất biến, không sinh dòng rác trùng lặp."
    ])

    # =========================================================================
    # SLIDE 7: BỘ 10 TEST CASES KIỂM THỬ CHẤT LƯỢNG DỮ LIỆU
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "6. Kiểm thử chất lượng dữ liệu: 10/10 Test Cases PASS")
    add_card(s7, 0.8, 1.8, 11.7, 5.1, "Bảng tổng hợp kết quả kiểm thử tự động (tests/run_dq_tests.py)", [
        "TC01 (Quy mô dữ liệu): Fact học tập đạt 224.778 dòng (Vượt yêu cầu >= 100.000 dòng) -> PASS",
        "TC02 (Bảo toàn học tập): Nguồn 227.267 = Fact 224.778 + Reject 2.489 dòng -> PASS",
        "TC03 (Bảo toàn tuyển sinh): Nguồn 8.012 = Fact 7.964 + Reject 48 dòng -> PASS",
        "TC04 (Đối soát sinh viên): 4.948 sinh viên nguồn = 4.948 bản ghi is_current=1 trong kho -> PASS",
        "TC05 (Miền giá trị điểm): 0 dòng NULL hoặc ngoài thang [0, 10] trong Fact -> PASS",
        "TC06 (Công thức đào tạo): 0 dòng lệch công thức ROUND(0.4*QT + 0.6*Thi, 1) -> PASS",
        "TC07 (Grain duy nhất): 0 trường hợp trùng lặp cặp (sinh_vien, lop_hoc_phan) trong Fact -> PASS",
        "TC08 (Toàn vẹn khóa ngoại): 0 dòng mồ côi (Orphan FK) giữa Fact và Dimension -> PASS",
        "TC09 (Chuẩn hóa danh mục): 0 giá trị tỉnh/thành hoặc giới tính lạ sai quy chuẩn -> PASS",
        "TC10 (Tính đúng đắn SCD2): 149 phiên bản lịch sử đổi ngành, 0 bản ghi chồng lấn thời gian -> PASS"
    ])

    # =========================================================================
    # SLIDE 8: ĐÁNH GIÁ HIỆU NĂNG: OLTP 3NF vs STAR SCHEMA
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "7. Đánh giá hiệu năng truy vấn (Benchmark Thực nghiệm)")
    add_card(s8, 0.8, 1.8, 5.6, 5.1, "Kết quả đo lường thời gian thực (225.000 dòng)", [
        "Q1 (Tỷ lệ rớt môn theo Khoa/Môn/Năm):",
        "  • OLTP 3NF (7 phép JOIN): 1.854,66 ms",
        "  • Kho dữ liệu Star Schema: 919,18 ms",
        "  • Tăng tốc: Nhanh hơn 2,02 lần (Giảm 50.4% thời gian phản hồi).",
        "Q2 (Điểm TB hệ 10 & 4 theo Khoa/Ngành/Năm):",
        "  • OLTP 3NF: 4.796,73 ms -> Star Schema: 4.280,19 ms (Nhanh hơn 1,12 lần).",
        "Q3 (Kết quả học tập theo Học vị GV/Loại môn):",
        "  • OLTP 3NF: 3.442,95 ms -> Star Schema: 2.515,31 ms (Nhanh hơn 1,37 lần)."
    ])
    add_card(s8, 6.9, 1.8, 5.6, 5.1, "Phân tích nguyên nhân kỹ thuật", [
        "Giảm tải phép JOIN: Star Schema chỉ cần JOIN trực tiếp 1 Fact với Dimension tương ứng, trong khi 3NF phải duyệt qua chuỗi bảng bắc cầu.",
        "Tối ưu khóa: Khóa thay thế kiểu số nguyên (INT) kết hợp chỉ mục B-Tree Index so khớp nhanh hơn nhiều so với khóa chuỗi VARCHAR ở nguồn.",
        "Phi chuẩn hóa có kiểm soát: Tích hợp sẵn tên Khoa vào dim_nganh và dim_mon_hoc giúp loại bỏ hoàn toàn việc JOIN bảng Khoa.",
        "Tránh xung đột tài nguyên: Tách biệt hoàn toàn tải đọc báo cáo phân tích khỏi CSDL giao dịch tác vụ đang chạy."
    ])

    # =========================================================================
    # SLIDE 9: KẾT QUẢ PHÂN TÍCH 5 CÂU HỎI NGHIỆP VỤ (INSIGHTS)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "8. Phát hiện nổi bật từ 5 góc nhìn phân tích (OLAP Insights)")
    add_card(s9, 0.8, 1.8, 5.6, 5.1, "Chất lượng học tập & Tuyển sinh", [
        "Top môn rớt cao: Các môn kỹ thuật cơ sở (Cấu trúc dữ liệu, Giải thuật, Kiến trúc máy tính) có tỷ lệ rớt từ 5.2% - 7.8% -> Nhà trường cần có chương trình trợ giảng/phụ đạo đầu kỳ.",
        "Tương quan Đầu vào & Đầu ra: Nhóm thí sinh trúng tuyển 24-27 điểm có GPA trung bình 3.29/4.0 (tỷ lệ rớt chỉ 0.04%), vượt trội rõ rệt so với nhóm 18-21 điểm (GPA 2.18, tỷ lệ rớt 29%).",
        "Xu hướng tuyển sinh: Ngành Công nghệ thông tin (IT) và Kỹ thuật phần mềm (SE) luôn đạt tỷ lệ nhập học > 88% qua các năm."
    ])
    add_card(s9, 6.9, 1.8, 5.6, 5.1, "Địa phương & Hiệu quả đào tạo", [
        "Phân bổ nguồn tuyển: Thí sinh Đà Nẵng, Quảng Nam, Thừa Thiên Huế, Quảng Trị chiếm > 75% tổng số sinh viên; chất lượng học lực giữa các tỉnh rất đồng đều (tỷ lệ qua môn > 98.6%).",
        "Hiệu quả giảng viên: Các lớp do giảng viên có học vị Tiến sĩ đảm nhiệm có tỷ lệ sinh viên đạt loại Giỏi/Xuất sắc cao hơn 6-8% so với trung bình.",
        "Khuyến nghị quản trị: Nhà trường nên phân bổ ngân sách phụ đạo cho các môn rớt cao và tăng chỉ tiêu cho các ngành CNTT, Trí tuệ nhân tạo."
    ])

    # =========================================================================
    # SLIDE 10: ỨNG DỤNG WEB DASHBOARD THEO KIẾN TRÚC MVC
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "9. Ứng dụng Web Dashboard phân tích (Kiến trúc MVC)")
    add_card(s10, 0.8, 1.8, 5.6, 5.1, "Kiến trúc phần mềm MVC chuẩn", [
        "Model (mvc/models/): olap_model.py, scd2_model.py, etl_model.py, sql_model.py (Truy vấn SQLAlchemy và xử lý dữ liệu lõi).",
        "View (mvc/views/): web/index.html (Single Page App với biểu đồ tương tác Chart.js), view.py (Đóng gói chuẩn JSON API).",
        "Controller (mvc/controllers/): olap_controller.py, scd2_controller.py, etl_controller.py, router.py (Điều hướng nghiệp vụ).",
        "Lợi ích: Tách biệt rõ ràng tầng dữ liệu và giao diện, dễ bảo trì và mở rộng."
    ])
    add_card(s10, 6.9, 1.8, 5.6, 5.1, "Các tính năng chính trên Giao diện Web", [
        "Khởi động 1-click qua chay_web.bat tại địa chỉ http://localhost:8050.",
        "Trang Dashboard trực quan: 5 Biểu đồ phân tích OLAP với bộ lọc tương tác thời gian thực.",
        "Trang Kiểm thử & ETL: Theo dõi trạng thái 10 Test Cases, lịch sử nạp dữ liệu và danh sách cách ly etl_reject.",
        "Trang SCD2 Explorer: Tra cứu trực quan lịch sử chuyển ngành của sinh viên.",
        "Trang SQL Console: Cho phép gõ trực tiếp câu lệnh SQL truy vấn kho dữ liệu."
    ])

    # =========================================================================
    # SLIDE 11: PHÂN CÔNG NHIỆM VỤ THÀNH VIÊN
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "10. Phân công công việc & Đóng góp của các thành viên")
    add_card(s11, 0.8, 1.8, 3.6, 5.1, "Cao Huy Hoàng (24ITB050)\nTrưởng nhóm - Data Engineer", [
        "Chịu trách nhiệm thiết kế kiến trúc toàn hệ thống.",
        "Xây dựng CSDL nguồn 3NF và CSDL kho Star Schema.",
        "Lập trình Pipeline ETL tự động bằng Python và Stored Procedures.",
        "Lập trình Web Dashboard MVC.",
        "Mức độ hoàn thành: 100%."
    ], border_color=COLOR_SECONDARY)
    add_card(s11, 4.8, 1.8, 3.7, 5.1, "Võ Nguyễn Thành Long (24ITB105)\nData Modeler & Analyst", [
        "Khảo sát tài liệu và 5 bài báo quốc tế liên quan (có DOI).",
        "Thiết kế sơ đồ ERD 3NF và Lược đồ hình sao (Star Schema).",
        "Lập bảng ánh xạ dữ liệu nguồn - đích (Source-to-Target Data Mapping).",
        "Biên soạn Báo cáo toàn văn đồ án.",
        "Mức độ hoàn thành: 100%."
    ], border_color=COLOR_PRIMARY)
    add_card(s11, 8.9, 1.8, 3.6, 5.1, "Nguyễn Thanh Tùng (24ITB220)\nQA & BI Specialist", [
        "Xây dựng bộ 10 kịch bản kiểm thử chất lượng dữ liệu (DQ Tests).",
        "Thực hiện đo lường hiệu năng truy vấn (Benchmark OLTP vs Star Schema).",
        "Viết truy vấn OLAP cho 5 câu hỏi quản trị và thiết kế Power BI.",
        "Soạn kịch bản và chuẩn bị Slide thuyết trình.",
        "Mức độ hoàn thành: 100%."
    ], border_color=COLOR_PRIMARY)

    # =========================================================================
    # SLIDE 12: KẾT LUẬN & HƯỚNG MỞ RỘNG
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "11. Kết luận & Hướng phát triển")
    add_card(s12, 0.8, 1.8, 5.6, 5.1, "Kết quả đạt được của Đề tài", [
        "Hoàn thành toàn diện đề tài Kho dữ liệu giáo dục đại học với quy mô lớn (> 227.000 dòng).",
        "Hiện thực hóa đầy đủ các chuẩn bài giảng: Star Schema, Conformed Dimensions, SCD Type 2, Stored Procedures, Data Quality Quarantine.",
        "Chứng minh hiệu quả thực nghiệm qua Benchmark (tăng tốc gấp 2,02 lần) và 10/10 Test Cases PASS.",
        "Bàn giao trọn gói: Mã nguồn Git, Web Dashboard MVC, Báo cáo Word 6 chương, Hướng dẫn Power BI và Slide thuyết trình."
    ])
    add_card(s12, 6.9, 1.8, 5.6, 5.1, "Hướng phát triển tương lai", [
        "Tích hợp mô hình Học máy (Machine Learning) để cảnh báo sớm sinh viên có nguy cơ rớt môn/buộc thôi học ngay từ giữa kỳ.",
        "Nâng cấp kiến trúc ETL thành Streaming Data Pipeline bằng Apache Kafka / Spark Streaming phục vụ chấm điểm và phản hồi trực tuyến.",
        "Mở rộng Kho dữ liệu lên nền tảng Cloud (Google BigQuery / Snowflake) phục vụ liên kết dữ liệu toàn thể Đại học Đà Nẵng."
    ])

    # =========================================================================
    # SLIDE 13: KẾT THÚC & Q&A
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    bg13 = s13.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg13.fill.solid()
    bg13.fill.fore_color.rgb = COLOR_PRIMARY
    bg13.line.fill.background()

    tb13 = s13.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.333), Inches(3.8))
    tf13 = tb13.text_frame
    tf13.word_wrap = True

    p = tf13.paragraphs[0]
    p.text = "XIN CHÂN THÀNH CẢM ƠN THẦY CÔ VÀ CÁC BẠN ĐÃ LẮNG NGHE!"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE

    p2 = tf13.add_paragraph()
    p2.text = "Kính mong nhận được sự góp ý và đánh giá từ ThS. Mai Lam và Hội đồng phản biện"
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
    print(f"Đã tạo file slide PowerPoint tại: {out_file.resolve()}")

if __name__ == "__main__":
    create_presentation()
