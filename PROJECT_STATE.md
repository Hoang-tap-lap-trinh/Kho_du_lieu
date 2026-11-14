# PROJECT_STATE.md – Trạng Thái Đồ Án Kho Dữ Liệu Giáo Dục (VKU)

**Cập nhật lần cuối:** 15/11/2026  
**Đề tài:** Xây dựng kho dữ liệu giáo dục phục vụ phân tích điểm số, tuyển sinh và kết quả học tập  
*(Building an Education Data Warehouse for Analyzing Grades, Admissions and Academic Performance)*  
**Giảng viên hướng dẫn:** ThS. Mai Lam  
**Trạng thái đề tài:** **100% HOÀN THÀNH TOÀN DIỆN (SẴN SÀNG NỘP BÀI VÀ BẢO VỆ)**

---

## 1. Thông tin nhóm & Trạng thái phân công

| Thành viên | Mã SV | Vai trò | Nhiệm vụ đảm nhận | Trạng thái |
|---|---|---|---|---|
| **Cao Huy Hoàng** | 24ITB050 | Nhóm trưởng – Data Engineer | Thiết kế & tạo CSDL nguồn `edu_source` (3NF), bộ sinh dữ liệu có kiểm soát lỗi chủ đích, thiết kế & tạo Kho dữ liệu `edu_dw` (Star Schema), lập trình pipeline ETL Python, Stored Procedure SCD loại 2, kiểm thử tự động, đo hiệu năng, xây dựng Web Dashboard MVC, quản lý Git | **100% Hoàn thành xuất sắc** |
| **Võ Nguyễn Thành Long** | 24ITB105 | Thiết kế & Khảo sát | Khảo sát tài liệu & 5 bài báo quốc tế (2020–2025, có DOI); thiết kế sơ đồ ERD 3NF, Star Schema, ETL Flow trên Draw.io (`docs/diagrams/`); lập bảng ánh xạ Source-to-Target Data Mapping; biên soạn Báo cáo toàn văn đồ án | **100% Hoàn thành xuất sắc** |
| **Nguyễn Thanh Tùng** | 24ITB220 | Phân tích OLAP & Trình bày | Thiết kế & thực thi 10 Test Cases kiểm thử chất lượng dữ liệu (10/10 PASS); thực hiện đo lường hiệu năng Benchmark; viết truy vấn 5 câu hỏi OLAP; xây dựng báo cáo Power BI & DAX; soạn slide thuyết trình PowerPoint | **100% Hoàn thành xuất sắc** |

---

## 2. Bản chất dữ liệu & Chu trình "Dữ liệu thô ban đầu -> Lọc/làm sạch -> Kho dữ liệu"

- **Nguồn gốc dữ liệu:** Trong thực tế, dữ liệu đào tạo đại học (điểm số của sinh viên, thông tin CCCD, tuyển sinh) là **dữ liệu bảo mật / quyền riêng tư (Privacy & Sensitive Data)** của Trường Đại học CNTT&TT Việt - Hàn (VKU), không thể lấy trực tiếp dữ liệu thật của sinh viên công khai đem làm bài tập lớn.
- **Cơ chế sinh dữ liệu mô phỏng (`generator/generate_data.py`):**
  - Mô phỏng chính xác hệ thống CSDL tác vụ thực tế (OLTP) của VKU chuẩn hóa 3NF gồm **11 bảng** (`Khoa`, `Nganh`, `PhuongThucXetTuyen`, `GiangVien`, `MonHoc`, `HocKy`, `SinhVien`, `LopHocPhan`, `DangKyHocPhan`, `HoSoTuyenSinh`, `LichSuChuyenNganh`).
  - Dữ liệu sinh theo các phân phối thống kê thực tế: điểm tuyển sinh phân phối chuẩn theo từng tổ hợp; sinh viên điểm đầu vào cao có xác suất điểm học phần cao hơn; phản ánh đúng quy chế tín chỉ của VKU: $TK = 0.4 \times QT + 0.6 \times Thi$.
- **Chèn LỖI CHỦ ĐÍCH vào dữ liệu thô (Dirty Raw Data) để kiểm thử năng lực ETL:**
  - 905 dòng đăng ký học phần trùng lặp (cùng SV, cùng lớp học phần trong kỳ).
  - 905 dòng thiếu điểm (NULL giá trị ở điểm quá trình hoặc điểm thi).
  - 679 dòng có điểm ngoài thang đo hợp lệ (điểm âm như -1 hoặc điểm > 10 như 10.5).
  - 671 dòng có điểm tổng kết ở nguồn bị tính sai lệch so với công thức chuẩn.
  - ~300 bản ghi sinh viên có tên tỉnh/thành phố bị gõ sai chính tả hoặc thừa tiền tố ("Tỉnh TP. Hồ Chí Minh", "T. Đà Nẵng").
  - Toàn bộ vị trí lỗi được ghi nhận minh bạch trong file kiểm chứng: `data/error_manifest.json`.
- **Chu trình lọc dữ liệu đúng chuẩn môn Kho dữ liệu (Data Warehouse & ETL):**
  - **CSDL Nguồn (OLTP - `edu_source`)**: Chứa 227.267 dòng thô bẩn, phân tán ở 11 bảng chuẩn hóa 3NF.
  - **Quy trình ETL (`Code/etl/`)**:
    + **Extract**: Trích xuất toàn bộ từ 11 bảng nguồn vào tầng Staging.
    + **Transform & Cleanse**: Lọc dữ liệu lỗi theo các quy tắc nghiệp vụ. Bắt lỗi và cách ly 2.537 dòng sai vào bảng cách ly `etl_reject` kèm lý do vi phạm (`ly_do_reject`). Chuẩn hóa danh mục (18 tỉnh thành miền Trung - Tây Nguyên, chuẩn hóa mã ngành, tính điểm hệ 4, điểm chữ A/B/C/D/F). Xử lý lịch sử SCD Type 2 cho bảng `dim_sinh_vien`.
    + **Load**: Nạp theo thứ tự Dimensions trước, Facts sau vào CSDL Kho dữ liệu (`edu_dw`).
  - **Kho dữ liệu (DW - `edu_dw`)**: Chứa 2 bảng Fact sạch: `fact_ket_qua_hoc_tap` (224.778 dòng sạch) và `fact_tuyen_sinh` (7.964 dòng sạch); 6 bảng Chiều chuẩn hóa; Tuyệt đối **không còn dữ liệu rác, không còn NULL, không còn trùng lặp**; 10/10 Test Cases kiểm định tính toàn vẹn đạt PASS 100%!

---

## 3. Danh mục sản phẩm bàn giao hoàn chỉnh

1. **Báo cáo Toàn văn Đồ án Môn học (`docs/Bao_cao_Kho_du_lieu_giao_duc_VKU.docx`):**
   - Bản báo cáo tốt nghiệp/cuối kỳ hoàn chỉnh gồm đầy đủ 6 chương chuẩn học thuật: Giới thiệu & Đặt vấn đề, Cơ sở lý thuyết & Khảo sát 5 bài báo quốc tế (có DOI), Phân tích & Thiết kế hệ thống (3NF, Star Schema, Mapping), Cài đặt & Triển khai (Python, Stored Procedures, Web MVC), Thử nghiệm & Đánh giá (10 Test Cases, Benchmark, 5 câu hỏi OLAP), Kết luận & Hướng phát triển, Tài liệu tham khảo chuẩn IEEE và Bảng phân công chi tiết 3 thành viên.
2. **Đề cương nghiên cứu hoàn chỉnh (`docs/Proposal_Kho_du_lieu_giao_duc_hoan_chinh.docx`):**
   - Đã điền đầy đủ tất cả các mục [điền] phục vụ nộp đề cương cho ThS. Mai Lam.
3. **Slide Thuyết trình PowerPoint (`docs/Slide_Thuyet_Trinh_Kho_du_lieu.pptx`):**
   - Bộ 13 slide chuẩn tỷ lệ 16:9 với thiết kế hiện đại, phối màu xanh VKU (`#003366`) và cam nhấn, phân chia rõ ràng kịch bản trình bày cho cả 3 thành viên.
4. **Sơ đồ Kiến trúc đa tab Draw.io (`docs/diagrams/VKU_DataWarehouse_Diagrams.drawio`):**
   - File sơ đồ chuẩn XML gồm 4 tabs: CSDL Nguồn 3NF (11 bảng), Kho dữ liệu Star Schema (2 Fact, 6 Dim), Luồng dữ liệu ETL & Quarantine, và Kiến trúc Web MVC. Có thể mở và xuất ảnh trực tiếp trên [app.diagrams.net](https://app.diagrams.net).
5. **Hướng dẫn Power BI & DAX (`docs/HUONG_DAN_POWERBI_OLAP.md`):**
   - Tài liệu hướng dẫn Tùng kết nối dữ liệu, thiết lập quan hệ Star Schema 1:*, bộ công thức đo lường DAX chuẩn và thiết kế 3 trang Dashboard chuyên nghiệp.
6. **Kịch bản Thuyết trình & Vấn đáp (`docs/KICH_BAN_DEMO_VA_THUYET_TRINH.md`):**
   - Phân chia thời lượng nói chi tiết từng phút cho Hoàng, Long, Tùng; chuẩn bị sẵn câu trả lời xuất sắc cho 5 câu hỏi kinh điển của Hội đồng phản biện.
7. **Bảng ánh xạ dữ liệu (`docs/mapping.md`):**
   - Chi tiết Source-to-Target Data Mapping và mã nguồn Mermaid trực quan.
8. **Ứng dụng Web Dashboard phân tích tương tác (`web_app.py` & `chay_web.bat`):**
   - Cài đặt theo chuẩn kiến trúc MVC tại `Code/mvc/`, chạy trực tiếp tại `http://localhost:8050`.

---

## 4. Kết quả Kiểm thử & Đo hiệu năng thực nghiệm

1. **Kiểm thử chất lượng dữ liệu (`output/test_cases_result.csv`):**
   - Đạt tuyệt đối **10/10 Test Cases = `PASS`** (`TC01` → `TC10`).
   - Đối soát bảo toàn dữ liệu: `227.267 = 224.778 (Fact) + 2.489 (Reject)`.
2. **Kiểm chứng SCD loại 2 (`etl/demo_scd2.py`):**
   - Sinh viên `19IT001` đổi từ ngành `IT` sang `SE` ngày `2021-08-20`: bản ghi cũ được đóng với `ngay_het_han = 2021-08-19, is_current = 0`; bản ghi mới mở với `ngay_hieu_luc = 2021-08-20, ngay_het_han = 9999-12-31, is_current = 1`. Bảo lưu điểm thi quá khứ và đạt tính Idempotent khi chạy lại ETL.
3. **So sánh hiệu năng OLTP (3NF) vs Kho dữ liệu (Star Schema) (`output/benchmark_result.csv`):**
   - `Q1` (Tỷ lệ đạt/rớt theo Khoa, Môn, Năm học): **1.854,66 ms** (3NF) → **919,18 ms** (Star Schema) — nhanh hơn **2,02 lần** (Tăng tốc 102%).
   - `Q2` (Điểm TB hệ 10, hệ 4 theo Khoa, Ngành, Năm học): **4.796,73 ms** (3NF) → **4.280,19 ms** (Star Schema) — nhanh hơn **1,12 lần**.
   - `Q3` (Kết quả theo Khoa, Học vị GV, Loại môn): **3.442,95 ms** (3NF) → **2.515,31 ms** (Star Schema) — nhanh hơn **1,37 lần**.

---

## 2. Trạng thái Môi trường & Cơ sở dữ liệu trên máy

- **Hệ quản trị CSDL:** MariaDB `10.4.32-MariaDB` (XAMPP trên Windows, cổng `3306`, user `root`, mật khẩu rỗng mặc định, cấu hình tại [`.env`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/.env)).
- **Môi trường Python:** Python `3.14.10`, môi trường ảo tại `Code/.venv` (đã cài đặt `pandas`, `numpy`, `Faker`, `SQLAlchemy`, `PyMySQL`, `cryptography`).
- **2 Database đã khởi tạo và nạp đầy đủ dữ liệu trong MariaDB:**

### 2.1. Database nguồn `edu_source` (OLTP – Chuẩn hóa 3NF – 11 bảng)
| Bảng | Số dòng đã nạp | Ghi chú |
|---|---:|---|
| `khoa` | 4 | KHCB, KHMT, KTMT, KTS |
| `nganh` | 10 | IT, CS, SE, CE, ET, IOT, BA, EC, DM, FT (có 2 tên ngành lỗi định dạng chủ đích) |
| `phuongthucxettuyen` | 3 | Học bạ (`HB` – thang 30), Thi THPT (`THPT` – thang 30), ĐGNL (`DGNL` – thang 1200) |
| `giangvien` | 118 | Phân bổ theo 4 khoa (Thạc sĩ, Tiến sĩ, PGS.TS) |
| `monhoc` | 120 | 12 môn đại cương + 108 môn cơ sở ngành, chuyên ngành, thực tập/đồ án |
| `hocky` | 14 | Từ năm học `2019-2020` đến `2025-2026` |
| `sinhvien` | 4.948 | Khoá tuyển sinh 2019–2022 (có lỗi chủ đích ở họ tên, giới tính, tỉnh/thành) |
| `lichsuchuyennganh` | 149 | 148 lượt đổi ngành gốc + 1 lượt demo SCD2 (`19IT001`) |
| `lophocphan` | 3.663 | Mở lớp theo từng môn và học kỳ |
| `dangkyhocphan` | **227.267** | Đạt yêu cầu `>= 100.000` dòng (chứa lỗi trùng lặp, thiếu điểm, ngoài thang, sai điểm TK) |
| `hosotuyensinh` | **8.012** | Hồ sơ 4 năm `2019–2022` (chứa lỗi thiếu điểm, vượt thang, tỉnh/thành không chuẩn) |

### 2.2. Database Kho dữ liệu `edu_dw` (Star Schema – Conformed Dimensions)
| Bảng / View | Loại | Số dòng hiện tại | Mô tả |
|---|---|---:|---|
| `dim_thoi_gian` | Dimension | 3.287 | Lịch từng ngày `2019-01-01` → `2027-12-31` |
| `dim_nganh` | Dimension (SCD1) | 10 | Đã chuẩn hóa tên ngành và phi chuẩn hóa tên khoa |
| `dim_mon_hoc` | Dimension (SCD1) | 120 | Môn học + số tín chỉ + loại môn + tên khoa |
| `dim_giang_vien` | Dimension (SCD1) | 118 | Giảng viên + học vị + tên khoa |
| `dim_phuong_thuc_xet_tuyen` | Dimension (SCD1) | 3 | 3 phương thức xét tuyển |
| `dim_sinh_vien` | **Dimension (SCD2)** | **5.098** | `4.948` bản ghi hiện tại (`is_current=1`) + `149` bản ghi lịch sử (`is_current=0`) + `1` bản ghi Unknown (`-1`) |
| `fact_ket_qua_hoc_tap` | **Fact** | **224.778** | Đã lọc sạch `2.489` dòng lỗi từ `227.267` dòng nguồn; tra khóa `sinh_vien_key` theo ngày học kỳ |
| `fact_tuyen_sinh` | **Fact** | **7.964** | Đã lọc sạch `48` dòng lỗi từ `8.012` dòng nguồn; quy đổi điểm về thang 30 |
| `etl_log` | Metadata Log | Đầy đủ | Ghi lại số dòng đọc, nạp, loại và thời gian chạy từng bảng |
| `etl_data_quality` | Data Quality | 11 tiêu chí | So sánh số dòng lỗi trước & sau khi làm sạch |
| `etl_reject` | Quarantine | 2.537 | Lưu khóa nguồn và lý do từ chối (`TRUNG_LAP`, `THIEU_DIEM`, `DIEM_NGOAI_THANG`...) |

---

## 3. Kết quả Kiểm thử, SCD2 & Đo hiệu năng (Mục 4.3 Đề cương)

1. **Kiểm thử chất lượng dữ liệu ([`output/test_cases_result.csv`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/output/test_cases_result.csv)):**
   - Đạt tuyệt đối **10/10 Test Cases = `PASS`** (`TC01` → `TC10`).
2. **Kiểm chứng SCD loại 2 ([`etl/demo_scd2.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/etl/demo_scd2.py)):**
   - Sinh viên `19IT001` (Phúc Văn Trần) đổi từ ngành `IT` sang `SE` ngày `2021-08-20`: bản ghi cũ (`sinh_vien_key=871`) được đóng với `ngay_het_han = 2021-08-19, is_current = 0`; bản ghi mới (`sinh_vien_key=8192`) mở với `ngay_hieu_luc = 2021-08-20, ngay_het_han = 9999-12-31, is_current = 1`.
   - Điểm 4 học kỳ đầu vẫn thuộc ngành `IT`, 4 học kỳ sau thuộc ngành `SE`. Chạy lặp lại ETL không tạo dòng trùng (Idempotent).
3. **So sánh hiệu năng OLTP (3NF) vs Kho dữ liệu (Star Schema) ([`output/benchmark_result.csv`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/output/benchmark_result.csv)):**
   - `Q1` (Tỷ lệ đạt/rớt theo Khoa, Môn, Năm học): **3.839,78 ms** (3NF) → **2.468,35 ms** (Star Schema) — nhanh hơn **1,56 lần**.
   - `Q2` (Điểm TB hệ 10, hệ 4 theo Khoa, Ngành, Năm học): **8.244,22 ms** (3NF) → **3.855,11 ms** (Star Schema) — nhanh hơn **2,14 lần**.
   - `Q3` (Kết quả theo Khoa, Học vị GV, Loại môn): **3.941,68 ms** (3NF) → **2.457,29 ms** (Star Schema) — nhanh hơn **1,60 lần**.

---

## 4. Danh mục toàn bộ các file trong dự án

- **Cấu hình & Chạy nhanh:**
  - [`.env`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/.env), [`.env.example`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/.env.example), [`requirements.txt`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/requirements.txt)
  - [`run_all.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/run_all.py): Chạy toàn bộ pipeline từ A–Z.
  - [`web_app.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/web_app.py), [`chay_web.bat`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/chay_web.bat): Khởi động Web Server tương tác tại `http://localhost:8050`.
  - [`mvc/`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/mvc): Cấu trúc MVC chuẩn cho ứng dụng Web:
    - `mvc/models/`: `base.py`, `olap_model.py`, `scd2_model.py`, `etl_model.py`, `sql_model.py`
    - `mvc/views/`: `view.py`, `web/index.html`
    - `mvc/controllers/`: `olap_controller.py`, `scd2_controller.py`, `etl_controller.py`, `sql_controller.py`, `router.py`
  - [`web/dashboard_standalone.html`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/web/dashboard_standalone.html), [`web/index.html`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/web/index.html): Giao diện Web Dashboard (hỗ trợ cả chế độ Live Server lẫn mở trực tiếp file HTML offline).
- **Mã nguồn SQL (`sql/`):**
  - [`01_create_source_db.sql`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/sql/01_create_source_db.sql), [`02_create_dw.sql`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/sql/02_create_dw.sql), [`03_procedures.sql`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/sql/03_procedures.sql), [`04_olap_views.sql`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/sql/04_olap_views.sql), [`05_olap_queries.sql`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/sql/05_olap_queries.sql).
- **Mã nguồn Python (`common/`, `etl/`, `tests/`, `analysis/`):**
  - [`common/db.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/common/db.py), [`common/check_connection.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/common/check_connection.py), [`common/grading.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/common/grading.py), [`common/reference.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/common/reference.py)
  - [`etl/import_oulad.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/etl/import_oulad.py)
  - [`etl/extract.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/etl/extract.py), [`etl/transform.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/etl/transform.py), [`etl/load.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/etl/load.py), [`etl/pipeline.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/etl/pipeline.py), [`etl/demo_scd2.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/etl/demo_scd2.py)
  - [`tests/run_dq_tests.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/tests/run_dq_tests.py), [`analysis/benchmark.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/analysis/benchmark.py)
- **Tài liệu thiết kế & Đề cương (`docs/`):**
  - [`docs/mapping.md`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/docs/mapping.md): Sơ đồ ERD 3NF, Star Schema và Bảng Mapping Nguồn → Kho.
  - [`HUONG_DAN_CHAY_VA_SU_DUNG_WEB.md`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/HUONG_DAN_CHAY_VA_SU_DUNG_WEB.md): Hướng dẫn chạy hệ thống và sử dụng Web Dashboard.

