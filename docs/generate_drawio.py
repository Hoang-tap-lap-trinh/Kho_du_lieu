"""Tạo file sơ đồ draw.io đa tab (.drawio) cho đồ án Kho dữ liệu VKU.

Bao gồm 4 tabs:
  1. CSDL Nguồn OLTP (Chuẩn hóa 3NF - 11 bảng)
  2. Kho dữ liệu đa chiều Star Schema (2 Fact, 6 Dimension)
  3. Luồng dữ liệu quy trình ETL (Extract, Transform, Load, Reject)
  4. Kiến trúc hệ thống Web Dashboard MVC
"""
import xml.etree.ElementTree as ET
from pathlib import Path

def create_drawio():
    mxfile = ET.Element("mxfile", host="app.diagrams.net", agent="VKU-DataWarehouse", version="21.0.0")

    # =========================================================================
    # TAB 1: CSDL NGUỒN OLTP 3NF
    # =========================================================================
    diag1 = ET.SubElement(mxfile, "diagram", id="tab1", name="1. CSDL Nguồn OLTP (3NF)")
    model1 = ET.SubElement(diag1, "mxGraphModel", dx="1422", dy="794", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1169", pageHeight="827")
    root1 = ET.SubElement(model1, "root")
    ET.SubElement(root1, "mxCell", id="0")
    ET.SubElement(root1, "mxCell", id="1", parent="0")

    tables_3nf = [
        ("Khoa", 40, 40, 160, 90, "<b>Khoa</b><hr/>+ ma_khoa (PK)<br/>+ ten_khoa", "#dae8fc", "#6c8ebf"),
        ("Nganh", 260, 40, 180, 120, "<b>Nganh</b><hr/>+ ma_nganh (PK)<br/>+ ten_nganh<br/>+ ma_khoa (FK)<br/>+ he_dao_tao", "#dae8fc", "#6c8ebf"),
        ("MonHoc", 500, 40, 180, 120, "<b>MonHoc</b><hr/>+ ma_mon (PK)<br/>+ ten_mon<br/>+ so_tin_chi<br/>+ loai_mon", "#dae8fc", "#6c8ebf"),
        ("GiangVien", 740, 40, 180, 120, "<b>GiangVien</b><hr/>+ ma_gv (PK)<br/>+ ho_ten<br/>+ ma_khoa (FK)<br/>+ hoc_vi", "#dae8fc", "#6c8ebf"),
        ("HocKy", 980, 40, 160, 110, "<b>HocKy</b><hr/>+ ma_hoc_ky (PK)<br/>+ ten_hoc_ky<br/>+ nam_hoc<br/>+ ngay_bat_dau", "#dae8fc", "#6c8ebf"),
        ("SinhVien", 260, 240, 200, 170, "<b>SinhVien</b><hr/>+ ma_sv (PK)<br/>+ ho_ten<br/>+ gioi_tinh<br/>+ ngay_sinh<br/>+ tinh_thanh<br/>+ ma_nganh (FK)<br/>+ ma_lop<br/>+ nam_nhap_hoc<br/>+ trang_thai", "#d5e8d4", "#82b366"),
        ("LichSuChuyenNganh", 40, 240, 180, 140, "<b>LichSuChuyenNganh</b><hr/>+ id (PK)<br/>+ ma_sv (FK)<br/>+ ma_nganh_cu (FK)<br/>+ ma_nganh_moi (FK)<br/>+ ngay_chuyen", "#fff2cc", "#d6b656"),
        ("LopHocPhan", 620, 240, 190, 130, "<b>LopHocPhan</b><hr/>+ ma_lhp (PK)<br/>+ ma_mon (FK)<br/>+ ma_hoc_ky (FK)<br/>+ ma_gv (FK)<br/>+ si_so_toi_da", "#dae8fc", "#6c8ebf"),
        ("DangKyHocPhan", 620, 450, 200, 160, "<b>DangKyHocPhan</b><hr/>+ ma_dang_ky (PK)<br/>+ ma_sv (FK)<br/>+ ma_lhp (FK)<br/>+ ngay_dang_ky<br/>+ diem_qua_trinh<br/>+ diem_thi<br/>+ diem_tong_ket", "#f8cecc", "#b85450"),
        ("PhuongThucXetTuyen", 40, 480, 180, 90, "<b>PhuongThucXetTuyen</b><hr/>+ ma_ptxt (PK)<br/>+ ten_ptxt", "#dae8fc", "#6c8ebf"),
        ("HoSoTuyenSinh", 260, 480, 210, 180, "<b>HoSoTuyenSinh</b><hr/>+ ma_ho_so (PK)<br/>+ ho_ten, gioi_tinh<br/>+ tinh_thanh<br/>+ ma_nganh (FK)<br/>+ ma_ptxt (FK)<br/>+ nam_tuyen_sinh<br/>+ diem_xet_tuyen<br/>+ trang_thai, da_nhap_hoc<br/>+ ma_sv (FK)", "#f8cecc", "#b85450"),
    ]

    cell_id = 2
    for name, x, y, w, h, content, fill, stroke in tables_3nf:
        style = f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};align=left;spacingLeft=10;verticalAlign=top;"
        ET.SubElement(root1, "mxCell", id=str(cell_id), value=content, style=style, parent="1", vertex="1")
        ET.SubElement(root1.find(f".//*[@id='{cell_id}']"), "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h), **{"as": "geometry"})
        cell_id += 1

    # =========================================================================
    # TAB 2: KHO DỮ LIỆU STAR SCHEMA
    # =========================================================================
    diag2 = ET.SubElement(mxfile, "diagram", id="tab2", name="2. Kho dữ liệu Star Schema")
    model2 = ET.SubElement(diag2, "mxGraphModel", dx="1422", dy="794", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1169", pageHeight="827")
    root2 = ET.SubElement(model2, "root")
    ET.SubElement(root2, "mxCell", id="0")
    ET.SubElement(root2, "mxCell", id="1", parent="0")

    tables_star = [
        # Dimensions
        ("dim_sinh_vien", 50, 50, 220, 210, "<b>dim_sinh_vien (SCD Type 2)</b><hr/>+ sinh_vien_key (PK)<br/>+ ma_sv (NK)<br/>+ ho_ten<br/>+ gioi_tinh<br/>+ nam_sinh<br/>+ tinh_thanh<br/>+ vung_mien<br/>+ ma_nganh, ten_nganh<br/>+ ma_khoa, ten_khoa<br/>+ ngay_hieu_luc<br/>+ ngay_het_han<br/>+ is_current", "#d5e8d4", "#82b366"),
        ("dim_hoc_phan", 350, 50, 180, 130, "<b>dim_hoc_phan</b><hr/>+ hoc_phan_key (PK)<br/>+ ma_mon (NK)<br/>+ ten_mon<br/>+ so_tin_chi<br/>+ loai_mon", "#dae8fc", "#6c8ebf"),
        ("dim_giang_vien", 600, 50, 180, 130, "<b>dim_giang_vien</b><hr/>+ giang_vien_key (PK)<br/>+ ma_gv (NK)<br/>+ ho_ten<br/>+ hoc_vi<br/>+ ten_khoa", "#dae8fc", "#6c8ebf"),
        ("dim_thoi_gian", 860, 50, 200, 160, "<b>dim_thoi_gian (Conformed)</b><hr/>+ date_key (PK, YYYYMMDD)<br/>+ full_date<br/>+ ngay, thang, nam<br/>+ quy, thu_trong_tuan<br/>+ hoc_ky_nien_khoa<br/>+ ma_hoc_ky", "#dae8fc", "#6c8ebf"),
        ("dim_nganh", 50, 380, 180, 120, "<b>dim_nganh</b><hr/>+ nganh_key (PK)<br/>+ ma_nganh (NK)<br/>+ ten_nganh<br/>+ ten_khoa<br/>+ he_dao_tao", "#dae8fc", "#6c8ebf"),
        ("dim_tinh_thanh", 860, 380, 180, 110, "<b>dim_tinh_thanh</b><hr/>+ tinh_thanh_key (PK)<br/>+ ten_tinh_thanh<br/>+ vung_mien", "#dae8fc", "#6c8ebf"),
        ("dim_ptxt", 50, 540, 200, 100, "<b>dim_phuong_thuc_xt</b><hr/>+ ptxt_key (PK)<br/>+ ma_ptxt (NK)<br/>+ ten_ptxt", "#dae8fc", "#6c8ebf"),

        # Facts
        ("fact_ket_qua_hoc_tap", 420, 260, 280, 230, "<b>fact_ket_qua_hoc_tap (Periodic/Accumulating)</b><hr/>+ fact_id (PK)<br/>+ sinh_vien_key (FK)<br/>+ hoc_phan_key (FK)<br/>+ giang_vien_key (FK)<br/>+ date_key (FK)<br/>+ ma_lhp<br/>+ diem_qua_trinh<br/>+ diem_thi<br/>+ diem_tong_ket<br/>+ diem_he_4<br/>+ diem_chu (A, B, C, D, F)<br/>+ ket_qua (Đạt, Rớt)<br/>+ so_tin_chi", "#f8cecc", "#b85450"),
        ("fact_tuyen_sinh", 420, 540, 280, 200, "<b>fact_tuyen_sinh (Admissions Fact)</b><hr/>+ tuyen_sinh_key (PK)<br/>+ sinh_vien_key (FK)<br/>+ nganh_key (FK)<br/>+ ptxt_key (FK)<br/>+ date_key (FK)<br/>+ tinh_thanh_key (FK)<br/>+ nam_tuyen_sinh<br/>+ diem_xet_tuyen<br/>+ trang_thai (Trúng tuyển/Không)<br/>+ da_nhap_hoc (0/1)", "#fff2cc", "#d6b656"),
    ]

    cell_id = 2
    for name, x, y, w, h, content, fill, stroke in tables_star:
        style = f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};align=left;spacingLeft=10;verticalAlign=top;"
        ET.SubElement(root2, "mxCell", id=str(cell_id), value=content, style=style, parent="1", vertex="1")
        ET.SubElement(root2.find(f".//*[@id='{cell_id}']"), "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h), **{"as": "geometry"})
        cell_id += 1

    # =========================================================================
    # TAB 3: LUỒNG ETL PIPELINE
    # =========================================================================
    diag3 = ET.SubElement(mxfile, "diagram", id="tab3", name="3. Quy trình ETL Pipeline")
    model3 = ET.SubElement(diag3, "mxGraphModel", dx="1422", dy="794", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1169", pageHeight="827")
    root3 = ET.SubElement(model3, "root")
    ET.SubElement(root3, "mxCell", id="0")
    ET.SubElement(root3, "mxCell", id="1", parent="0")

    etl_nodes = [
        ("Nguồn OLTP", 50, 150, 150, 80, "<b>edu_source (OLTP 3NF)</b><br/>11 Bảng tác vụ<br/>(~240,000 dòng thô)", "#dae8fc", "#6c8ebf"),
        ("Extract", 260, 150, 140, 80, "<b>EXTRACT</b><br/>Đọc theo Batch<br/>Chuyển vào Staging", "#fff2cc", "#d6b656"),
        ("Data Quality Filter", 460, 130, 180, 120, "<b>TRANSFORM & CLEANSE</b><br/>• Kiểm tra miền [0, 10]<br/>• Lọc trùng lặp Grain<br/>• Chuẩn hóa 63 Tỉnh/thành<br/>• Xử lý SCD Type 2", "#d5e8d4", "#82b366"),
        ("Quarantine", 460, 320, 180, 80, "<b>etl_reject (Cách ly)</b><br/>2,537 dòng lỗi<br/>Kèm lý do vi phạm", "#f8cecc", "#b85450"),
        ("Audit Log", 460, 20, 180, 70, "<b>etl_log / dq_report</b><br/>Ghi vết nhật ký<br/>Audit Trail toàn vẹn", "#e1d5e7", "#9673a6"),
        ("Load", 700, 150, 140, 80, "<b>LOAD</b><br/>Nạp Dim trước (SCD2)<br/>Nạp Fact sau (Bulk 1K)", "#fff2cc", "#d6b656"),
        ("Kho Dữ Liệu", 900, 130, 180, 120, "<b>edu_dw (Star Schema)</b><br/>• 2 Bảng Fact sạch<br/>• 6 Bảng Chiều chuẩn<br/>• 100% Sạch & Không NULL", "#d5e8d4", "#82b366"),
        ("OLAP & BI", 900, 320, 180, 90, "<b>Khai Thác OLAP</b><br/>• 5 Câu hỏi quản lý<br/>• Web Dashboard MVC<br/>• Báo cáo Power BI", "#dae8fc", "#6c8ebf"),
    ]

    cell_id = 2
    for name, x, y, w, h, content, fill, stroke in etl_nodes:
        style = f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};align=center;verticalAlign=middle;"
        ET.SubElement(root3, "mxCell", id=str(cell_id), value=content, style=style, parent="1", vertex="1")
        ET.SubElement(root3.find(f".//*[@id='{cell_id}']"), "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h), **{"as": "geometry"})
        cell_id += 1

    # =========================================================================
    # TAB 4: KIẾN TRÚC WEB DASHBOARD MVC
    # =========================================================================
    diag4 = ET.SubElement(mxfile, "diagram", id="tab4", name="4. Kiến trúc Web MVC")
    model4 = ET.SubElement(diag4, "mxGraphModel", dx="1422", dy="794", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1169", pageHeight="827")
    root4 = ET.SubElement(model4, "root")
    ET.SubElement(root4, "mxCell", id="0")
    ET.SubElement(root4, "mxCell", id="1", parent="0")

    mvc_nodes = [
        ("Client", 50, 150, 160, 90, "<b>Trình duyệt Web (Client)</b><br/>Single Page App (SPA)<br/>Chart.js Trực quan hóa", "#dae8fc", "#6c8ebf"),
        ("Router", 270, 150, 150, 90, "<b>ROUTER & SERVER</b><br/><code>web_app.py</code><br/>HTTP Request Dispatcher", "#fff2cc", "#d6b656"),
        ("Controller", 480, 130, 200, 130, "<b>CONTROLLERS</b><br/>• OlapController<br/>• Scd2Controller<br/>• EtlController<br/>• SqlController", "#d5e8d4", "#82b366"),
        ("Model", 750, 130, 190, 130, "<b>MODELS</b><br/>• OlapModel<br/>• Scd2Model<br/>• EtlModel<br/>• SqlModel", "#e1d5e7", "#9673a6"),
        ("View", 480, 340, 200, 100, "<b>VIEWS</b><br/>• JSON API Response<br/>• HTML UI Renderer<br/>• Static Asset Handler", "#f8cecc", "#b85450"),
        ("Database", 750, 340, 190, 100, "<b>DATABASE DW</b><br/>• MariaDB 10.4<br/>• edu_dw Views<br/>• SQLAlchemy Pool", "#dae8fc", "#6c8ebf"),
    ]

    cell_id = 2
    for name, x, y, w, h, content, fill, stroke in mvc_nodes:
        style = f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};align=center;verticalAlign=middle;"
        ET.SubElement(root4, "mxCell", id=str(cell_id), value=content, style=style, parent="1", vertex="1")
        ET.SubElement(root4.find(f".//*[@id='{cell_id}']"), "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h), **{"as": "geometry"})
        cell_id += 1

    out_path = Path("docs/diagrams/VKU_DataWarehouse_Diagrams.drawio")
    tree = ET.ElementTree(mxfile)
    tree.write(out_path, encoding="utf-8", xml_declaration=True)
    print(f"Đã tạo file sơ đồ draw.io tại: {out_path}")

if __name__ == "__main__":
    create_drawio()

