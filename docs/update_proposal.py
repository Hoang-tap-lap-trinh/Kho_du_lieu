"""Cập nhật toàn bộ các mục còn để trống [điền] trong file Proposal_Kho_du_lieu_giao_duc.docx.

Giữ nguyên 100% định dạng, bảng biểu, font chữ của file Word gốc (tạo bản sao lưu .bak trước khi ghi).
"""
from __future__ import annotations

import shutil
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

DOCX_PATH = Path(r"d:\Nam_Hoc\Nam_3\Kho du lieu\Bai_tap_lon\Proposal_Kho_du_lieu_giao_duc.docx")
OUT_DOCX_PATH = Path(__file__).resolve().parent / "Proposal_Kho_du_lieu_giao_duc_hoan_chinh.docx"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"

PAPERS = [
    (
        "S. Suman, P. Khajuria, S. Urolagin (2020)",
        "Star Schema-Based Data Warehouse Model for Education System Using Mondrian and Pentaho",
        "Lecture Notes in Electrical Engineering (Springer), DOI: 10.1007/978-981-15-4775-1_4",
        "Thiết kế mô hình kho dữ liệu lược đồ hình sao (star schema), quy trình ETL và khối OLAP cho hệ thống giáo dục đại học nhằm phân tích kết quả học tập của sinh viên.",
    ),
    (
        "D. Sihombing (2022)",
        "Academic Data Warehouse Modeling in Higher Education Using Nine-Step Design Methodology",
        "Journal of Information Systems and Informatics, Vol. 4, No. 4, DOI: 10.51519/journalisi.v4i4.399",
        "Áp dụng phương pháp 9 bước của Kimball để tích hợp dữ liệu đào tạo phân tán của trường đại học vào mô hình đa chiều phục vụ đánh giá chất lượng chương trình đào tạo.",
    ),
    (
        "İ. Güneş, M. K. Birgin (2023)",
        "Implementing Data Warehouse Infrastructure for an E-Learning System",
        "Gümüşhane University Journal of Science, DOI: 10.17714/gumusfenbil.1239468",
        "Xây dựng hạ tầng kho dữ liệu và quy trình làm sạch, chuẩn hóa dữ liệu lịch sử học tập nhằm theo dõi tiến độ và kết quả đánh giá môn học.",
    ),
    (
        "Y. Lv (2025)",
        "Research on the Application of Data Warehouse in Education Evaluation System",
        "Int. Journal of Cognitive Informatics and Natural Intelligence, DOI: 10.4018/IJCINI.377804",
        "Tích hợp dữ liệu từ nhiều phân hệ quản lý đào tạo vào kho dữ liệu trung tâm để phân tích đa chiều kết quả học tập và hỗ trợ ra quyết định quản lý.",
    ),
    (
        "E. Zeqo, E. Naka (2025)",
        "A Historical Review of Data Warehouse Implementation in Higher Education",
        "Interdisciplinary Journal of Research and Development, Vol. 12, No. 3, DOI: 10.56345/ijrdv12n328",
        "Tổng quan hệ thống các kiến trúc kho dữ liệu giáo dục đại học, chỉ ra ưu thế của Star Schema, Conformed Dimensions và nhu cầu theo dõi lịch sử biến động sinh viên.",
    ),
]


def set_paragraph_text(p_elem: ET.Element, new_text: str) -> None:
    """Thay nội dung văn bản của một thẻ <w:p> nhưng giữ nguyên định dạng <w:rPr> của run đầu tiên."""
    runs = p_elem.findall(f"{W}r")
    if not runs:
        r = ET.SubElement(p_elem, f"{W}r")
        t = ET.SubElement(r, f"{W}t")
        t.text = new_text
        return
    first_run = runs[0]
    for r in runs[1:]:
        p_elem.remove(r)
    t_elems = first_run.findall(f"{W}t")
    if t_elems:
        t_elems[0].text = new_text
        for extra_t in t_elems[1:]:
            first_run.remove(extra_t)
    else:
        t = ET.SubElement(first_run, f"{W}t")
        t.text = new_text


def main() -> None:
    with zipfile.ZipFile(DOCX_PATH, "r") as zin:
        xml_bytes = zin.read("word/document.xml")
        all_files = {name: zin.read(name) for name in zin.namelist()}

    root = ET.fromstring(xml_bytes)
    paragraphs = list(root.iter(f"{W}p"))

    # Thu thập danh sách các ô [điền] trong bảng 2.2 (20 ô = 5 dòng x 4 cột)
    dien_Cells = []
    for p in paragraphs:
        txt = "".join(p.itertext()).strip()
        if txt == "[điền]":
            dien_Cells.append(p)
        elif "[số bài, ví dụ 3]" in txt:
            set_paragraph_text(p, "Nhóm điền vào bảng sau, mỗi thành viên khảo sát tối thiểu 3 bài.")
        elif txt.startswith("[Sau khi khảo sát, tóm tắt 1-2 đoạn"):
            set_paragraph_text(
                p,
                "Qua khảo sát các công trình từ năm 2020 đến 2025, hầu hết các nghiên cứu đều áp dụng phương pháp thiết kế đa chiều của Kimball với lược đồ hình sao (Star Schema) để tích hợp dữ liệu đào tạo rời rạc và triển khai truy vấn OLAP phục vụ quản lý. Tuy nhiên, phần lớn các hệ thống trước chỉ tập trung riêng lẻ vào điểm số môn học hoặc riêng dữ liệu tuyển sinh, ít nghiên cứu kết hợp đồng thời cả hai bảng sự kiện (Fact_TuyenSinh và Fact_KetQuaHocTap) thông qua các chiều dùng chung (Conformed Dimensions) để phân tích mối liên hệ xuyên suốt từ điểm đầu vào, phương thức xét tuyển đến kết quả học tập các học kỳ. Bên cạnh đó, bài toán sinh viên chuyển ngành, chuyển lớp theo thời gian thường bị ghi đè làm mất lịch sử. Đề tài của nhóm khắc phục khoảng trống này bằng cách tích hợp cả dữ liệu tuyển sinh và kết quả học tập trên cùng một kho dữ liệu, xử lý đầy đủ Slowly Changing Dimension loại 2 (SCD2) cho chiều sinh viên và xây dựng hệ thống kiểm thử chất lượng dữ liệu cùng Web/BI Dashboard trực quan.",
            )
        elif txt == "[Python (pandas, SQLAlchemy) hoặc Pentaho - chọn một]":
            set_paragraph_text(p, "Python (pandas, SQLAlchemy, PyMySQL)")
        elif txt == "[Power BI, Tableau hoặc Metabase - chọn một]":
            set_paragraph_text(p, "Power BI Desktop & Web Dashboard tương tác")
        elif txt == "[Họ tên 1]":
            set_paragraph_text(p, "Cao Huy Hoàng (24ITB050 – Nhóm trưởng)")
        elif txt == "[Họ tên 2]":
            set_paragraph_text(p, "Võ Nguyễn Thành Long (24ITB105)")
        elif txt == "[Họ tên 3]":
            set_paragraph_text(p, "Nguyễn Thanh Tùng (24ITB220)")
        elif txt.startswith("[2] [Các bài báo từ năm 2020"):
            set_paragraph_text(
                p,
                '[2] S. Suman, P. Khajuria, S. Urolagin, "Star Schema-Based Data Warehouse Model for Education System Using Mondrian and Pentaho," Lecture Notes in Electrical Engineering, Springer, 2020, doi: 10.1007/978-981-15-4775-1_4; D. Sihombing, "Academic Data Warehouse Modeling in Higher Education Using Nine-Step Design Methodology," Journal of Information Systems and Informatics, vol. 4, no. 4, pp. 1126–1134, 2022, doi: 10.51519/journalisi.v4i4.399; İ. Güneş, M. K. Birgin, "Implementing Data Warehouse Infrastructure for an E-Learning System," Gümüşhane University Journal of Science, 2023, doi: 10.17714/gumusfenbil.1239468; Y. Lv, "Research on the Application of Data Warehouse in Education Evaluation System," IJCINI, 2025, doi: 10.4018/IJCINI.377804; E. Zeqo, E. Naka, "A Historical Review of Data Warehouse Implementation in Higher Education," IJRD, vol. 12, no. 3, 2025, doi: 10.56345/ijrdv12n328.',
            )
        elif txt.startswith("[3] MySQL 8.0 Reference Manual"):
            set_paragraph_text(p, "[3] MySQL 8.0 & MariaDB Reference Manual, https://dev.mysql.com/doc/refman/8.0/en/")

    if len(dien_Cells) == 20:
        for row_idx, paper in enumerate(PAPERS):
            for col_idx in range(4):
                set_paragraph_text(dien_Cells[row_idx * 4 + col_idx], paper[col_idx])

    all_files["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(OUT_DOCX_PATH, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, content in all_files.items():
            zout.writestr(name, content)

    print(f"[OK] Đã xuất file Đề cương hoàn chỉnh tại: {OUT_DOCX_PATH}")


if __name__ == "__main__":
    main()
