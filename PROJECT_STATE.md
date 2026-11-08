# PROJECT_STATE.md – Trạng Thái Đồ Án Kho Dữ Liệu Giáo Dục (VKU)

**Cập nhật lần cuối:** 09/11/2026  
**Đề tài:** Xây dựng kho dữ liệu giáo dục phục vụ phân tích điểm số, tuyển sinh và kết quả học tập  
*(Building an Education Data Warehouse for Analyzing Grades, Admissions and Academic Performance)*  
**Giảng viên hướng dẫn:** ThS. Mai Lam  

---

## 1. Thông tin nhóm & Trạng thái phân công

| Thành viên | Mã SV | Vai trò | Nhiệm vụ | Trạng thái |
|---|---|---|---|---|
| **Cao Huy Hoàng** | 24ITB050 | Nhóm trưởng – Data Engineer | Thiết kế & tạo CSDL nguồn `edu_source` (3NF), sinh dữ liệu giả lập (~230.000 dòng + lỗi chủ đích), thiết kế & tạo Kho dữ liệu `edu_dw` (Star Schema), quy trình ETL Python, Stored Procedure SCD loại 2, kiểm thử tự động, đo hiệu năng, xây dựng Web Dashboard tương tác | **HOÀN THÀNH 100%** |
| **Võ Nguyễn Thành Long** | 24ITB105 | Thiết kế & Khảo sát | Vẽ Class Diagram, ERD 3NF, Star Schema trên draw.io / MySQL Workbench (dựa trên [`docs/mapping.md`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/docs/mapping.md) và [`sql/`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/sql)); hoàn thiện bảng khảo sát tài liệu và chương Thiết kế trong báo cáo | **Đã có sẵn tài liệu nguồn, sơ đồ mẫu & bản đề cương hoàn chỉnh** |
| **Nguyễn Thanh Tùng** | 24ITB220 | Phân tích OLAP & Trình bày | Dựng báo cáo Power BI (từ các view trong [`04_olap_views.sql`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/sql/04_olap_views.sql) hoặc CSV trong [`output/`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/output)), tổng hợp bảng Test Cases, chuẩn bị Slide & kịch bản Demo trên Web Dashboard | **Đã có sẵn 10/10 Test Cases PASS, 7 file CSV OLAP & Web Dashboard chạy sẵn** |

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
- **Mã nguồn Python (`common/`, `generator/`, `etl/`, `tests/`, `analysis/`):**
  - [`common/db.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/common/db.py), [`common/check_connection.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/common/check_connection.py), [`common/grading.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/common/grading.py), [`common/reference.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/common/reference.py)
  - [`generator/generate_data.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/generator/generate_data.py)
  - [`etl/extract.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/etl/extract.py), [`etl/transform.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/etl/transform.py), [`etl/load.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/etl/load.py), [`etl/pipeline.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/etl/pipeline.py), [`etl/demo_scd2.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/etl/demo_scd2.py)
  - [`tests/run_dq_tests.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/tests/run_dq_tests.py), [`analysis/benchmark.py`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/analysis/benchmark.py)
- **Tài liệu thiết kế & Đề cương (`docs/`):**
  - [`docs/mapping.md`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/docs/mapping.md): Sơ đồ ERD 3NF, Star Schema và Bảng Mapping Nguồn → Kho.
  - [`HUONG_DAN_CHAY_VA_SU_DUNG_WEB.md`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/HUONG_DAN_CHAY_VA_SU_DUNG_WEB.md): Hướng dẫn chạy hệ thống và sử dụng Web Dashboard.

