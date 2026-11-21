"""Tạo file sơ đồ draw.io đa tab (.drawio) đầy đủ đường nối quan hệ (Edges & Connectors)
cho đồ án Kho dữ liệu VKU.

Bao gồm 5 tabs chuẩn chỉnh:
  1. Hình 1.1 - Kiến trúc tổng quan Kho dữ liệu giáo dục
  2. Hình 2.1 - Sơ đồ ERD CSDL Nguồn OLTP (Chuẩn 3NF có khóa ngoại)
  3. Hình 3.1 - Sơ đồ Kho dữ liệu Star Schema (2 Fact, 6 Dim đa chiều)
  4. Hình 4.1 & 4.2 - Quy trình ETL Pipeline & Luồng cách ly Reject
  5. Kiến trúc Web Dashboard MVC
"""
import xml.etree.ElementTree as ET
from pathlib import Path

def add_edge(parent, edge_id, src_id, tgt_id, label="1..N", stroke="#003366", width=2, dashed=False, style_extra=""):
    style = (
        f"edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;"
        f"strokeColor={stroke};strokeWidth={width};endArrow=block;endFill=1;"
        f"fontFamily=Helvetica;fontSize=11;fontColor=#333333;labelBackgroundColor=#ffffff;"
    )
    if dashed:
        style += "dashed=1;"
    if style_extra:
        style += style_extra
    
    edge = ET.SubElement(parent, "mxCell", id=str(edge_id), value=label, style=style, parent="1", edge="1", source=str(src_id), target=str(tgt_id))
    ET.SubElement(edge, "mxGeometry", relative="1", **{"as": "geometry"})
    return edge

def create_drawio():
    mxfile = ET.Element("mxfile", host="app.diagrams.net", agent="VKU-DataWarehouse", version="21.0.0")

    # =========================================================================
    # TAB 1: HÌNH 1.1 - KIẾN TRÚC TỔNG QUAN KHO DỮ LIỆU GIÁO DỤC
    # =========================================================================
    diag1 = ET.SubElement(mxfile, "diagram", id="tab1", name="Hình 1.1. Kiến trúc Tổng quan KDL")
    model1 = ET.SubElement(diag1, "mxGraphModel", dx="1422", dy="794", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1300", pageHeight="850")
    root1 = ET.SubElement(model1, "root")
    ET.SubElement(root1, "mxCell", id="0")
    ET.SubElement(root1, "mxCell", id="1", parent="0")

    arch_layers = [
        # (id, name, x, y, w, h, title, fill, stroke)
        (2, "Layer 1: CSDL Nguồn Tác vụ (OLTP)", 40, 60, 240, 520, "#e1f5fe", "#0288d1"),
        (3, "Layer 2: Tích hợp Dữ liệu & ETL", 340, 60, 300, 520, "#fff3e0", "#f57c00"),
        (4, "Layer 3: Kho Dữ liệu Đa chiều (DW)", 700, 60, 270, 520, "#e8f5e9", "#388e3c"),
        (5, "Layer 4: Ứng dụng & Khai thác (BI/OLAP)", 1030, 60, 230, 520, "#f3e5f5", "#7b1fa2"),
    ]
    for cid, name, x, y, w, h, fill, stroke in arch_layers:
        style = f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth=2;align=center;verticalAlign=top;fontStyle=1;fontSize=13;fontColor={stroke};spacingTop=10;"
        ET.SubElement(root1, "mxCell", id=str(cid), value=name, style=style, parent="1", vertex="1")
        ET.SubElement(root1.find(f".//*[@id='{cid}']"), "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h), **{"as": "geometry"})

    # Nodes inside Arch
    arch_nodes = [
        # In Layer 1
        (10, 1, 60, 120, 200, 90, "<b>edu_source (MariaDB 10.4)</b><hr/>• Sinh viên & Hồ sơ tuyển sinh<br/>• Điểm đăng ký học phần<br/>• Lớp học phần, Môn học, GV", "#ffffff", "#0288d1"),
        (11, 1, 60, 240, 200, 70, "<b>File dữ liệu thô (Raw CSV)</b><hr/>• Dữ liệu tuyển sinh 4 năm<br/>• 227.267 bản ghi học tập", "#ffffff", "#0288d1"),
        (12, 1, 60, 340, 200, 80, "<b>Chèn lỗi chủ đích</b><hr/>• 905 dòng trùng, 905 NULL<br/>• 679 dòng ngoài thang 0-10<br/>• 292 lỗi chính tả tỉnh thành", "#ffebee", "#c62828"),

        # In Layer 2
        (20, 1, 360, 120, 260, 70, "<b>EXTRACT (Trích xuất)</b><hr/>• Đọc từ 11 bảng nguồn OLTP<br/>• Đưa vào tầng Staging bộ nhớ", "#ffffff", "#f57c00"),
        (21, 1, 360, 220, 260, 110, "<b>TRANSFORM & DATA QUALITY</b><hr/>• Bộ lọc quy tắc điểm [0, 10]<br/>• Xử lý SCD Type 2 (Đổi ngành)<br/>• Chuẩn hóa 18 tỉnh miền Trung<br/>• Tính điểm hệ 4, điểm chữ A-F", "#ffffff", "#f57c00"),
        (22, 1, 360, 360, 260, 70, "<b>Bảng Cách ly (etl_reject)</b><hr/>• 2.537 dòng lỗi bị loại bỏ<br/>• Lưu vết nguyên nhân vi phạm", "#ffebee", "#d32f2f"),
        (23, 1, 360, 460, 260, 60, "<b>Nhật ký kiểm toán (etl_log)</b><hr/>• Audit Trail, đếm dòng & thời gian", "#f3e5f5", "#8e24aa"),

        # In Layer 3
        (30, 1, 720, 120, 230, 80, "<b>Fact Đào tạo & Điểm số</b><hr/>• <code>fact_ket_qua_hoc_tap</code><br/>• 224.778 dòng sạch (100%)", "#ffffff", "#388e3c"),
        (31, 1, 720, 230, 230, 80, "<b>Fact Tuyển sinh</b><hr/>• <code>fact_tuyen_sinh</code><br/>• 7.964 hồ sơ trúng tuyển", "#ffffff", "#388e3c"),
        (32, 1, 720, 340, 230, 120, "<b>6 Conformed Dimensions</b><hr/>• dim_sinh_vien (SCD2)<br/>• dim_hoc_phan, dim_giang_vien<br/>• dim_thoi_gian, dim_nganh<br/>• dim_tinh_thanh, dim_ptxt", "#ffffff", "#388e3c"),

        # In Layer 4
        (40, 1, 1050, 120, 190, 90, "<b>Web Dashboard MVC</b><hr/>• Cổng 8050 tương tác<br/>• 6 Biểu đồ phân tích OLAP<br/>• Demo SCD2 đổi ngành", "#ffffff", "#7b1fa2"),
        (41, 1, 1050, 240, 190, 80, "<b>Báo cáo Power BI DAX</b><hr/>• 3 Trang Dashboard đa chiều<br/>• Mô hình Star Schema 1:*", "#ffffff", "#7b1fa2"),
        (42, 1, 1050, 350, 190, 80, "<b>SQL OLAP Analytics</b><hr/>• CUBE, ROLLUP, Drill-down<br/>• Benchmark hiệu năng", "#ffffff", "#7b1fa2"),
    ]

    for cid, parent_id, x, y, w, h, content, fill, stroke in arch_nodes:
        style = f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth=1.5;align=left;spacingLeft=8;verticalAlign=top;fontSize=11;"
        ET.SubElement(root1, "mxCell", id=str(cid), value=content, style=style, parent=str(parent_id), vertex="1")
        ET.SubElement(root1.find(f".//*[@id='{cid}']"), "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h), **{"as": "geometry"})

    # Edges in Architecture
    add_edge(root1, 100, 10, 20, "Trích xuất", stroke="#0288d1")
    add_edge(root1, 101, 11, 20, "Batch Load", stroke="#0288d1")
    add_edge(root1, 102, 20, 21, "Pipeline", stroke="#f57c00")
    add_edge(root1, 103, 21, 22, "Cách ly dữ liệu sai", stroke="#d32f2f")
    add_edge(root1, 104, 21, 23, "Ghi nhật ký", stroke="#8e24aa")
    add_edge(root1, 105, 21, 30, "Load dữ liệu sạch", stroke="#388e3c")
    add_edge(root1, 106, 21, 31, "Load tuyển sinh", stroke="#388e3c")
    add_edge(root1, 107, 21, 32, "Nạp Dim (SCD2)", stroke="#388e3c")
    add_edge(root1, 108, 30, 40, "Truy vấn OLAP", stroke="#7b1fa2")
    add_edge(root1, 109, 31, 41, "DAX Measures", stroke="#7b1fa2")
    add_edge(root1, 110, 32, 42, "Slice / Dice", stroke="#7b1fa2")

    # =========================================================================
    # TAB 2: HÌNH 2.1 - SƠ ĐỒ ERD CSDL NGUỒN OLTP (3NF - 11 BẢNG CÓ QUAN HỆ)
    # =========================================================================
    diag2 = ET.SubElement(mxfile, "diagram", id="tab2", name="Hình 2.1. ERD CSDL Nguồn 3NF")
    model2 = ET.SubElement(diag2, "mxGraphModel", dx="1422", dy="794", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1400", pageHeight="950")
    root2 = ET.SubElement(model2, "root")
    ET.SubElement(root2, "mxCell", id="0")
    ET.SubElement(root2, "mxCell", id="1", parent="0")

    tables_3nf = {
        "Khoa": (50, 40, 180, 90, "<b>Khoa</b><hr/>🔑 ma_khoa (PK)<br/>+ ten_khoa", "#dae8fc", "#6c8ebf"),
        "Nganh": (310, 40, 190, 120, "<b>Nganh</b><hr/>🔑 ma_nganh (PK)<br/>+ ten_nganh<br/>🔗 ma_khoa (FK)<br/>+ he_dao_tao", "#dae8fc", "#6c8ebf"),
        "GiangVien": (570, 40, 190, 120, "<b>GiangVien</b><hr/>🔑 ma_gv (PK)<br/>+ ho_ten<br/>🔗 ma_khoa (FK)<br/>+ hoc_vi", "#dae8fc", "#6c8ebf"),
        "MonHoc": (830, 40, 180, 120, "<b>MonHoc</b><hr/>🔑 ma_mon (PK)<br/>+ ten_mon<br/>+ so_tin_chi<br/>+ loai_mon", "#dae8fc", "#6c8ebf"),
        "HocKy": (1080, 40, 170, 110, "<b>HocKy</b><hr/>🔑 ma_hoc_ky (PK)<br/>+ ten_hoc_ky<br/>+ nam_hoc<br/>+ ngay_bat_dau", "#dae8fc", "#6c8ebf"),

        "SinhVien": (310, 260, 210, 180, "<b>SinhVien</b><hr/>🔑 ma_sv (PK)<br/>+ ho_ten<br/>+ gioi_tinh, ngay_sinh<br/>+ tinh_thanh<br/>🔗 ma_nganh (FK)<br/>+ ma_lop, nam_nhap_hoc<br/>+ trang_thai", "#d5e8d4", "#82b366"),
        "LopHocPhan": (830, 260, 200, 140, "<b>LopHocPhan</b><hr/>🔑 ma_lhp (PK)<br/>🔗 ma_mon (FK)<br/>🔗 ma_hoc_ky (FK)<br/>🔗 ma_gv (FK)<br/>+ si_so_toi_da", "#dae8fc", "#6c8ebf"),

        "PhuongThucXetTuyen": (50, 520, 180, 90, "<b>PhuongThucXetTuyen</b><hr/>🔑 ma_ptxt (PK)<br/>+ ten_ptxt", "#dae8fc", "#6c8ebf"),
        "HoSoTuyenSinh": (310, 520, 220, 190, "<b>HoSoTuyenSinh</b><hr/>🔑 ma_ho_so (PK)<br/>+ ho_ten, gioi_tinh, tinh_thanh<br/>🔗 ma_nganh (FK)<br/>🔗 ma_ptxt (FK)<br/>+ nam_tuyen_sinh, diem_xet_tuyen<br/>+ trang_thai, da_nhap_hoc<br/>🔗 ma_sv (FK)", "#f8cecc", "#b85450"),

        "LichSuChuyenNganh": (50, 260, 200, 140, "<b>LichSuChuyenNganh</b><hr/>🔑 id (PK)<br/>🔗 ma_sv (FK)<br/>🔗 ma_nganh_cu (FK)<br/>🔗 ma_nganh_moi (FK)<br/>+ ngay_chuyen", "#fff2cc", "#d6b656"),
        "DangKyHocPhan": (830, 480, 210, 170, "<b>DangKyHocPhan</b><hr/>🔑 ma_dang_ky (PK)<br/>🔗 ma_sv (FK)<br/>🔗 ma_lhp (FK)<br/>+ ngay_dang_ky<br/>+ diem_qua_trinh<br/>+ diem_thi<br/>+ diem_tong_ket", "#f8cecc", "#b85450"),
    }

    id_map_3nf = {}
    cell_id = 2
    for name, (x, y, w, h, content, fill, stroke) in tables_3nf.items():
        style = f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth=1.5;align=left;spacingLeft=8;verticalAlign=top;fontSize=11;"
        ET.SubElement(root2, "mxCell", id=str(cell_id), value=content, style=style, parent="1", vertex="1")
        ET.SubElement(root2.find(f".//*[@id='{cell_id}']"), "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h), **{"as": "geometry"})
        id_map_3nf[name] = cell_id
        cell_id += 1

    # Quan hệ Khóa ngoại ERD (1 : N)
    edges_3nf = [
        ("Khoa", "Nganh", "1 : N (ma_khoa)"),
        ("Khoa", "GiangVien", "1 : N (ma_khoa)"),
        ("Nganh", "SinhVien", "1 : N (ma_nganh)"),
        ("Nganh", "HoSoTuyenSinh", "1 : N (ma_nganh)"),
        ("PhuongThucXetTuyen", "HoSoTuyenSinh", "1 : N (ma_ptxt)"),
        ("SinhVien", "HoSoTuyenSinh", "1 : 1 (ma_sv)"),
        ("SinhVien", "LichSuChuyenNganh", "1 : N (ma_sv)"),
        ("Nganh", "LichSuChuyenNganh", "1 : N (chuyển ngành)"),
        ("MonHoc", "LopHocPhan", "1 : N (ma_mon)"),
        ("GiangVien", "LopHocPhan", "1 : N (ma_gv)"),
        ("HocKy", "LopHocPhan", "1 : N (ma_hoc_ky)"),
        ("LopHocPhan", "DangKyHocPhan", "1 : N (ma_lhp)"),
        ("SinhVien", "DangKyHocPhan", "1 : N (ma_sv)"),
    ]

    edge_id = 200
    for src, tgt, lbl in edges_3nf:
        add_edge(root2, edge_id, id_map_3nf[src], id_map_3nf[tgt], label=lbl, stroke="#1a237e", width=1.8)
        edge_id += 1

    # =========================================================================
    # TAB 3: HÌNH 3.1 - SƠ ĐỒ KHO DỮ LIỆU STAR SCHEMA (2 FACT, 6 DIM CÓ QUAN HỆ)
    # =========================================================================
    diag3 = ET.SubElement(mxfile, "diagram", id="tab3", name="Hình 3.1. Sơ đồ Star Schema")
    model3 = ET.SubElement(diag3, "mxGraphModel", dx="1422", dy="794", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1400", pageHeight="950")
    root3 = ET.SubElement(model3, "root")
    ET.SubElement(root3, "mxCell", id="0")
    ET.SubElement(root3, "mxCell", id="1", parent="0")

    tables_star = {
        # Dimensions
        "dim_sinh_vien": (60, 160, 230, 220, "<b>dim_sinh_vien (SCD Type 2)</b><hr/>🔑 sinh_vien_key (Surrogate PK)<br/>• ma_sv (Natural Key)<br/>• ho_ten, gioi_tinh, nam_sinh<br/>• tinh_thanh, vung_mien<br/>• ma_nganh, ten_nganh<br/>• ma_khoa, ten_khoa<br/>• ngay_hieu_luc, ngay_het_han<br/>• is_current (1=Hiện tại, 0=Lịch sử)", "#d5e8d4", "#82b366"),
        "dim_hoc_phan": (360, 30, 190, 130, "<b>dim_hoc_phan</b><hr/>🔑 hoc_phan_key (PK)<br/>• ma_mon (NK)<br/>• ten_mon<br/>• so_tin_chi<br/>• loai_mon", "#dae8fc", "#6c8ebf"),
        "dim_giang_vien": (620, 30, 190, 130, "<b>dim_giang_vien</b><hr/>🔑 giang_vien_key (PK)<br/>• ma_gv (NK)<br/>• ho_ten, hoc_vi<br/>• ten_khoa", "#dae8fc", "#6c8ebf"),
        "dim_thoi_gian": (930, 220, 220, 180, "<b>dim_thoi_gian (Conformed Dim)</b><hr/>🔑 date_key (PK, YYYYMMDD)<br/>• full_date<br/>• ngay, thang, nam, quy<br/>• thu_trong_tuan<br/>• hoc_ky_nien_khoa<br/>• ma_hoc_ky", "#dae8fc", "#6c8ebf"),

        "dim_nganh": (60, 560, 200, 130, "<b>dim_nganh</b><hr/>🔑 nganh_key (PK)<br/>• ma_nganh (NK)<br/>• ten_nganh<br/>• ten_khoa, he_dao_tao", "#dae8fc", "#6c8ebf"),
        "dim_tinh_thanh": (930, 560, 200, 120, "<b>dim_tinh_thanh</b><hr/>🔑 tinh_thanh_key (PK)<br/>• ten_tinh_thanh<br/>• vung_mien", "#dae8fc", "#6c8ebf"),
        "dim_ptxt": (360, 750, 210, 100, "<b>dim_phuong_thuc_xt</b><hr/>🔑 ptxt_key (PK)<br/>• ma_ptxt (NK)<br/>• ten_ptxt", "#dae8fc", "#6c8ebf"),

        # Facts trung tâm
        "fact_ket_qua_hoc_tap": (450, 210, 320, 230, "<b>fact_ket_qua_hoc_tap (Fact Đào tạo)</b><hr/>🔑 fact_id (PK)<br/>🔗 sinh_vien_key (FK)<br/>🔗 hoc_phan_key (FK)<br/>🔗 giang_vien_key (FK)<br/>🔗 date_key (FK)<br/>• ma_lhp<br/>• diem_qua_trinh, diem_thi<br/>• diem_tong_ket, diem_he_4<br/>• diem_chu (A, B, C, D, F)<br/>• ket_qua (Đạt, Rớt), so_tin_chi", "#f8cecc", "#b85450"),
        "fact_tuyen_sinh": (450, 500, 320, 210, "<b>fact_tuyen_sinh (Fact Tuyển sinh)</b><hr/>🔑 tuyen_sinh_key (PK)<br/>🔗 sinh_vien_key (FK)<br/>🔗 nganh_key (FK)<br/>🔗 ptxt_key (FK)<br/>🔗 date_key (FK)<br/>🔗 tinh_thanh_key (FK)<br/>• nam_tuyen_sinh, diem_xet_tuyen<br/>• trang_thai (Trúng tuyển/Không)<br/>• da_nhap_hoc (0/1)", "#fff2cc", "#d6b656"),
    }

    id_map_star = {}
    cell_id = 2
    for name, (x, y, w, h, content, fill, stroke) in tables_star.items():
        style = f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth=1.5;align=left;spacingLeft=8;verticalAlign=top;fontSize=11;"
        ET.SubElement(root3, "mxCell", id=str(cell_id), value=content, style=style, parent="1", vertex="1")
        ET.SubElement(root3.find(f".//*[@id='{cell_id}']"), "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h), **{"as": "geometry"})
        id_map_star[name] = cell_id
        cell_id += 1

    # Quan hệ Star Schema (1 Dim liên kết sang Nhiều Fact)
    edges_star = [
        # Sang fact_ket_qua_hoc_tap
        ("dim_sinh_vien", "fact_ket_qua_hoc_tap", "1 : N (sinh_vien_key)"),
        ("dim_hoc_phan", "fact_ket_qua_hoc_tap", "1 : N (hoc_phan_key)"),
        ("dim_giang_vien", "fact_ket_qua_hoc_tap", "1 : N (giang_vien_key)"),
        ("dim_thoi_gian", "fact_ket_qua_hoc_tap", "1 : N (date_key)"),

        # Sang fact_tuyen_sinh
        ("dim_sinh_vien", "fact_tuyen_sinh", "1 : N (sinh_vien_key)"),
        ("dim_nganh", "fact_tuyen_sinh", "1 : N (nganh_key)"),
        ("dim_ptxt", "fact_tuyen_sinh", "1 : N (ptxt_key)"),
        ("dim_thoi_gian", "fact_tuyen_sinh", "1 : N (date_key)"),
        ("dim_tinh_thanh", "fact_tuyen_sinh", "1 : N (tinh_thanh_key)"),
    ]

    edge_id = 300
    for src, tgt, lbl in edges_star:
        add_edge(root3, edge_id, id_map_star[src], id_map_star[tgt], label=lbl, stroke="#b71c1c" if "ket_qua" in tgt else "#e65100", width=2)
        edge_id += 1

    # =========================================================================
    # TAB 4: HÌNH 4.1 & 4.2 - QUY TRÌNH ETL VÀ LUỒNG CÁCH LY REJECT
    # =========================================================================
    diag4 = ET.SubElement(mxfile, "diagram", id="tab4", name="Hình 4.1 & 4.2. Quy trình ETL")
    model4 = ET.SubElement(diag4, "mxGraphModel", dx="1422", dy="794", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1300", pageHeight="850")
    root4 = ET.SubElement(model4, "root")
    ET.SubElement(root4, "mxCell", id="0")
    ET.SubElement(root4, "mxCell", id="1", parent="0")

    etl_nodes = {
        "source": (40, 160, 160, 90, "<b>edu_source (OLTP 3NF)</b><hr/>• 11 Bảng tác vụ<br/>• 227.267 bản ghi thô<br/>• Chứa lỗi chủ đích", "#dae8fc", "#6c8ebf"),
        "extract": (250, 160, 150, 90, "<b>1. EXTRACT</b><hr/>• Trích xuất theo lô<br/>• <code>extract.py</code><br/>• Nạp vào tầng Staging", "#fff2cc", "#d6b656"),
        "transform": (460, 130, 220, 150, "<b>2. TRANSFORM & CLEANSE</b><hr/>• <code>transform.py</code><br/>• Kiểm tra miền [0, 10]<br/>• Lọc trùng lặp Grain<br/>• Chuẩn hóa 18 Tỉnh/thành<br/>• Tính điểm hệ 4, chữ A-F<br/>• Xử lý SCD Type 2", "#d5e8d4", "#82b366"),
        "reject": (460, 360, 220, 100, "<b>Bảng Cách ly (etl_reject)</b><hr/>• 2.537 dòng lỗi vi phạm<br/>• Ghi nhận nguyên nhân<br/>• Không làm dừng hệ thống", "#f8cecc", "#b85450"),
        "audit": (460, 20, 220, 80, "<b>Nhật ký Kiểm toán (etl_log)</b><hr/>• Ghi số dòng In/Out/Reject<br/>• Thời gian chạy pipeline", "#e1d5e7", "#9673a6"),
        "load": (740, 160, 160, 90, "<b>3. LOAD</b><hr/>• <code>load.py</code><br/>• Nạp Dim trước (SCD2)<br/>• Nạp Fact sau (Bulk 1K)", "#fff2cc", "#d6b656"),
        "dw": (960, 140, 200, 130, "<b>Kho Dữ liệu (edu_dw)</b><hr/>• fact_ket_qua_hoc_tap (224K)<br/>• fact_tuyen_sinh (7.9K)<br/>• 6 Bảng Dimension sạch<br/>• Đạt 10/10 Test Cases", "#d5e8d4", "#82b366"),
    }

    id_map_etl = {}
    cell_id = 2
    for name, (x, y, w, h, content, fill, stroke) in etl_nodes.items():
        style = f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth=1.5;align=left;spacingLeft=8;verticalAlign=top;fontSize=11;"
        ET.SubElement(root4, "mxCell", id=str(cell_id), value=content, style=style, parent="1", vertex="1")
        ET.SubElement(root4.find(f".//*[@id='{cell_id}']"), "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h), **{"as": "geometry"})
        id_map_etl[name] = cell_id
        cell_id += 1

    edges_etl = [
        ("source", "extract", "Đọc dữ liệu thô", "#003366", False),
        ("extract", "transform", "Chuyển sang làm sạch", "#f57c00", False),
        ("transform", "reject", "Dữ liệu sai -> Cách ly", "#c62828", False),
        ("transform", "audit", "Ghi vết kiểm toán", "#8e24aa", True),
        ("transform", "load", "Dữ liệu hợp lệ", "#2e7d32", False),
        ("load", "dw", "Ghi vào Kho dữ liệu", "#2e7d32", False),
    ]

    edge_id = 400
    for src, tgt, lbl, clr, dashed in edges_etl:
        add_edge(root4, edge_id, id_map_etl[src], id_map_etl[tgt], label=lbl, stroke=clr, width=2, dashed=dashed)
        edge_id += 1

    # =========================================================================
    # TAB 5: KIẾN TRÚC WEB DASHBOARD MVC
    # =========================================================================
    diag5 = ET.SubElement(mxfile, "diagram", id="tab5", name="Kiến trúc Web Dashboard MVC")
    model5 = ET.SubElement(diag5, "mxGraphModel", dx="1422", dy="794", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1300", pageHeight="850")
    root5 = ET.SubElement(model5, "root")
    ET.SubElement(root5, "mxCell", id="0")
    ET.SubElement(root5, "mxCell", id="1", parent="0")

    mvc_nodes = {
        "client": (50, 160, 180, 100, "<b>Trình duyệt Web (Client)</b><hr/>• Single Page App (SPA)<br/>• Chart.js biểu đồ tương tác<br/>• Gửi HTTP / API Request", "#dae8fc", "#6c8ebf"),
        "router": (280, 160, 170, 100, "<b>ROUTER & DISPATCHER</b><hr/>• <code>web_app.py</code><br/>• Điều hướng URL<br/>• Phân phối đến Controller", "#fff2cc", "#d6b656"),
        "controller": (510, 140, 210, 140, "<b>CONTROLLERS (mvc/controllers)</b><hr/>• OlapController (5 câu hỏi)<br/>• Scd2Controller (Đổi ngành)<br/>• EtlController (Log & Test)<br/>• SqlController (Query)", "#d5e8d4", "#82b366"),
        "model": (780, 140, 200, 140, "<b>MODELS (mvc/models)</b><hr/>• OlapModel, Scd2Model<br/>• EtlModel, SqlModel<br/>• Thực thi SQL truy vấn Kho", "#e1d5e7", "#9673a6"),
        "view": (510, 360, 210, 100, "<b>VIEWS (mvc/views)</b><hr/>• Định dạng JSON Response<br/>• Render giao diện HTML<br/>• Trả về trình duyệt", "#f8cecc", "#b85450"),
        "database": (780, 360, 200, 100, "<b>DATABASE KHO DỮ LIỆU</b><hr/>• MariaDB (edu_dw & edu_source)<br/>• 2 Fact, 6 Dim, OLAP Views<br/>• Stored Procedures SCD2", "#dae8fc", "#6c8ebf"),
    }

    id_map_mvc = {}
    cell_id = 2
    for name, (x, y, w, h, content, fill, stroke) in mvc_nodes.items():
        style = f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth=1.5;align=left;spacingLeft=8;verticalAlign=top;fontSize=11;"
        ET.SubElement(root5, "mxCell", id=str(cell_id), value=content, style=style, parent="1", vertex="1")
        ET.SubElement(root5.find(f".//*[@id='{cell_id}']"), "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h), **{"as": "geometry"})
        id_map_mvc[name] = cell_id
        cell_id += 1

    edges_mvc = [
        ("client", "router", "1. Gửi Request", "#003366", False),
        ("router", "controller", "2. Gọi Controller", "#003366", False),
        ("controller", "model", "3. Yêu cầu dữ liệu", "#2e7d32", False),
        ("model", "database", "4. Truy vấn SQL", "#8e24aa", False),
        ("database", "model", "5. Trả kết quả tập dòng", "#8e24aa", True),
        ("model", "controller", "6. Trả dữ liệu sạch", "#2e7d32", True),
        ("controller", "view", "7. Chuyển sang View", "#c62828", False),
        ("view", "client", "8. Trả JSON / Render UI", "#c62828", False),
    ]

    edge_id = 500
    for src, tgt, lbl, clr, dashed in edges_mvc:
        add_edge(root5, edge_id, id_map_mvc[src], id_map_mvc[tgt], label=lbl, stroke=clr, width=1.8, dashed=dashed)
        edge_id += 1

    out_path = Path("docs/diagrams/VKU_DataWarehouse_Diagrams.drawio")
    tree = ET.ElementTree(mxfile)
    tree.write(out_path, encoding="utf-8", xml_declaration=True)
    print(f"Đã cập nhật file sơ đồ draw.io với đầy đủ kết nối tại: {out_path}")

if __name__ == "__main__":
    create_drawio()
