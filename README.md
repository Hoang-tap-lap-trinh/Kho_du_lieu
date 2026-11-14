# Kho Dữ Liệu Giáo Dục (Education Data Warehouse) – VKU

Đồ án môn **Kho dữ liệu**: *Xây dựng kho dữ liệu giáo dục phục vụ phân tích điểm số, tuyển sinh và kết quả học tập*.

- **Giảng viên hướng dẫn**: ThS. Mai Lam
- **Nhóm thực hiện**:
  1. **Cao Huy Hoàng** – 24ITB050 (Nhóm trưởng – CSDL nguồn, Kho dữ liệu Star Schema, Pipeline ETL Python & SCD2, Web Dashboard MVC)
  2. **Võ Nguyễn Thành Long** – 24ITB105 (Khảo sát tài liệu, Sơ đồ thiết kế ERD/Class/Star Schema trên Draw.io, Từ điển dữ liệu & Mapping, Báo cáo toàn văn)
  3. **Nguyễn Thanh Tùng** – 24ITB220 (Kiểm thử chất lượng dữ liệu 10 Test Cases, Đo hiệu năng Benchmark, Truy vấn OLAP, Dashboard Power BI & DAX, Slide thuyết trình)

---

## 1. Cấu trúc thư mục `Code/`

```text
Code/
├── .env                        # Cấu hình kết nối MariaDB/MySQL (điền mật khẩu vào đây)
├── .env.example                # Mẫu cấu hình .env
├── requirements.txt            # Các thư viện Python cần thiết (Pandas, SQLAlchemy, python-docx, python-pptx...)
├── run_all.py                  # Chạy trọn gói toàn bộ pipeline từ đầu đến cuối bằng 1 lệnh
├── chay_web.bat                # Khởi động nhanh Web Dashboard tại http://localhost:8050
├── web_app.py                  # Server HTTP khởi chạy Web Dashboard
├── generator/
│   └── generate_data.py        # Sinh CSDL tác vụ nguồn 3NF (> 240.000 dòng) có kiểm soát lỗi chủ đích
├── common/
│   ├── db.py                   # Kết nối SQLAlchemy/PyMySQL + thực thi file .sql
│   ├── check_connection.py     # Kiểm tra kết nối MariaDB/MySQL
│   ├── grading.py              # Quy tắc tính điểm tổng kết & quy đổi điểm chữ/thang 4
│   └── reference.py            # Danh mục chuẩn (Khoa, Ngành, 18 Tỉnh/Thành miền Trung, 120 Môn học)
├── sql/
│   ├── 01_create_source_db.sql # Tạo CSDL nguồn edu_source (OLTP 3NF - 11 bảng)
│   ├── 02_create_dw.sql        # Tạo Kho dữ liệu edu_dw (Star Schema + Staging + Log + Reject)
│   ├── 03_procedures.sql       # Stored Procedures xử lý SCD2 & nạp 2 bảng Fact
│   ├── 04_olap_views.sql       # Views mô phỏng CUBE và Views phẳng cho Power BI
│   └── 05_olap_queries.sql     # 5 câu truy vấn OLAP trả lời 5 câu hỏi quản lý
├── etl/
│   ├── extract.py              # Bước Extract từ edu_source sang staging
│   ├── transform.py            # Bước Transform làm sạch, chuẩn hóa, tạo phiên bản SCD2, cách ly etl_reject
│   ├── load.py                 # Bước Load nạp Dimension và Fact vào edu_dw
│   ├── pipeline.py             # Điều phối toàn bộ pipeline ETL
│   └── demo_scd2.py            # Kịch bản demo kiểm chứng SCD Loại 2 cho SV đổi ngành
├── mvc/                        # Cấu trúc Web Dashboard theo chuẩn MVC
│   ├── models/                 # OlapModel, Scd2Model, EtlModel, SqlModel
│   ├── views/                  # View renderer và API JSON
│   └── controllers/            # OlapController, Scd2Controller, EtlController, SqlController, Router
├── tests/
│   └── run_dq_tests.py         # Bộ 10 kịch bản kiểm thử chất lượng dữ liệu (10/10 PASS)
├── analysis/
│   └── benchmark.py            # Đo và so sánh hiệu năng truy vấn: OLTP (3NF) vs Kho (Star Schema)
├── output/                     # Kết quả xuất ra các file CSV báo cáo OLAP, benchmark, test cases
└── docs/                       # Toàn bộ tài liệu, slide, sơ đồ giao nộp đồ án
    ├── Bao_cao_Kho_du_lieu_giao_duc_VKU.docx         # Báo cáo toàn văn hoàn chỉnh (Full Final Report)
    ├── Proposal_Kho_du_lieu_giao_duc_hoan_chinh.docx # Đề cương BTL hoàn chỉnh
    ├── Slide_Thuyet_Trinh_Kho_du_lieu.pptx           # Slide thuyết trình PowerPoint 13 slides
    ├── diagrams/VKU_DataWarehouse_Diagrams.drawio     # Sơ đồ 4 tabs cho Draw.io (3NF, Star Schema, ETL, MVC)
    ├── HUONG_DAN_POWERBI_OLAP.md                     # Hướng dẫn chi tiết Power BI & DAX cho Tùng
    ├── KICH_BAN_DEMO_VA_THUYET_TRINH.md              # Kịch bản thuyết trình chi tiết & 5 câu hỏi Q&A
    └── mapping.md                                    # Bảng ánh xạ Source-to-Target Data Mapping
```
│   ├── load.py                 # Bước Load vào Dimension và Fact
│   ├── pipeline.py             # Điều phối ETL và xuất bảng log / chất lượng dữ liệu
│   └── demo_scd2.py            # Kịch bản minh họa đổi ngành SCD2 & kiểm tra chạy lặp
├── tests/
│   └── run_dq_tests.py         # 10 Test Cases đối soát dữ liệu & kiểm tra SCD2
├── analysis/
│   └── benchmark.py            # Xuất kết quả 5 câu hỏi OLAP & đo hiệu năng OLTP vs DW
├── docs/
│   └── mapping.md              # Sơ đồ ERD, Star Schema và Bảng Mapping Nguồn -> Kho
├── data/                       # (Tự tạo khi chạy) CSV dữ liệu nguồn + error_manifest.json
└── output/                     # (Tự tạo khi chạy) CSV log ETL, test cases, OLAP, benchmark
```

---

## 2. Hướng dẫn chạy cho Cao Huy Hoàng (Chỉ cần 2 bước)

### Bước 1: Bật MariaDB trong XAMPP và điền mật khẩu vào `.env`
1. Mở **XAMPP Control Panel** → bấm **Start** ở dòng **MySQL** (cổng mặc định `3306`).
2. Mở file [`.env`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/.env) và điền mật khẩu tài khoản `root` của bạn vào dòng:
   ```ini
   DB_PASSWORD=mat_khau_cua_ban
   ```

### Bước 2: Tải OULAD và chạy toàn bộ hệ thống
Đặt 7 file CSV OULAD vào `data/oulad/`, sau đó chạy:

```powershell
.venv\Scripts\python.exe run_all.py --import-oulad
```

Hoặc chạy riêng từng bước khi muốn demo cho giảng viên:
```powershell
# 1. Kiểm tra kết nối MariaDB
.venv\Scripts\python.exe -m common.check_connection

# 2. Chuyển OULAD thành CSV nguồn (không nạp database)
.venv\Scripts\python.exe -m etl.import_oulad --csv-only

# 3. Tạo kho edu_dw và chạy quy trình ETL
.venv\Scripts\python.exe -m etl.pipeline --init-dw

# 4. Demo đổi ngành sinh viên (SCD2) và chạy lặp ETL
.venv\Scripts\python.exe -m etl.demo_scd2

# 5. Chạy 10 Test Cases kiểm thử chất lượng dữ liệu
.venv\Scripts\python.exe -m tests.run_dq_tests

# 6. Chạy 5 câu hỏi OLAP và đo hiệu năng Star Schema vs OLTP 3NF
.venv\Scripts\python.exe -m analysis.benchmark
```

---

## 3. Giải thích nhanh: Power BI là gì và cách dựng Dashboard (cho Tùng & Hoàng)

- **Power BI Desktop** là phần mềm trực quan hóa dữ liệu (Business Intelligence) **miễn phí của Microsoft** trên Windows (tải tại Microsoft Store gõ `Power BI Desktop`).
- Thay vì phải tự lập trình giao diện biểu đồ, bạn chỉ cần kết nối Power BI tới database `edu_dw` (hoặc đọc trực tiếp các file CSV đã xuất sẵn trong thư mục `Code/output/` và các View trong `04_olap_views.sql`), sau đó **kéo – thả** cột để tạo 5 biểu đồ theo đúng mục 4.2 của Đề cương:
  1. **Biểu đồ cột / Heatmap tỷ lệ rớt theo Khoa & Môn học**: dùng bảng `vw_ket_qua_hoc_tap_chi_tiet` hoặc file `output/olap_q1b_top15_mon_rot_cao.csv`.
  2. **Biểu đồ cột nhóm (Grouped Bar) Điểm TB theo Ngành × Phương thức xét tuyển**: dùng view `vw_olap_cube_nganh_phuongthuc` hoặc `output/olap_q2_dice_nganh_phuongthuc.csv`.
  3. **Biểu đồ phân tán (Scatter Plot) Điểm đầu vào vs GPA Học kỳ 1**: dùng view `vw_olap_tuong_quan_dau_vao_hk1` (trục X = `diem_quy_doi_30`, trục Y = `gpa_hk1_he_10`, màu sắc = `ten_phuong_thuc`).
  4. **Biểu đồ đường (Line Chart) Xu hướng nhập học các ngành qua các năm**: dùng bảng `vw_tuyen_sinh_chi_tiet` hoặc `output/olap_q4_xu_huong_tuyen_sinh.csv`.
  5. **Biểu đồ cột / Bản đồ Kết quả học tập theo Tỉnh/Thành phố**: dùng `output/olap_q5_ket_qua_theo_tinh_thanh.csv`.

