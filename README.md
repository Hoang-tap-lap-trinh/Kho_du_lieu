# Kho Dữ Liệu Giáo Dục (Education Data Warehouse) – VKU

Đồ án môn **Kho dữ liệu**: *Xây dựng kho dữ liệu giáo dục phục vụ phân tích điểm số, tuyển sinh và kết quả học tập*.

- **Giảng viên hướng dẫn**: ThS. Mai Lam
- **Nhóm thực hiện**:
  1. **Cao Huy Hoàng** – 24ITB050 (Nhóm trưởng – CSDL nguồn, Sinh dữ liệu, Kho dữ liệu, ETL & SCD2)
  2. **Võ Nguyễn Thành Long** – 24ITB105 (Khảo sát tài liệu, Sơ đồ thiết kế ERD/Class/Star Schema, Từ điển dữ liệu)
  3. **Nguyễn Thanh Tùng** – 24ITB220 (Kiểm thử chất lượng dữ liệu, Truy vấn OLAP, Dashboard Power BI, Slide & Demo)

---

## 1. Cấu trúc thư mục `Code/`

```text
Code/
├── .env                        # Cấu hình kết nối MariaDB/MySQL (điền mật khẩu vào đây)
├── .env.example                # Mẫu cấu hình .env
├── requirements.txt            # Các thư viện Python cần thiết
├── run_all.py                  # Chạy trọn gói từ đầu đến cuối bằng 1 lệnh
├── common/
│   ├── db.py                   # Kết nối SQLAlchemy/PyMySQL + thực thi file .sql
│   ├── check_connection.py     # Kiểm tra kết nối MariaDB/MySQL
│   ├── grading.py              # Quy tắc tính điểm tổng kết & quy đổi điểm chữ/thang 4
│   └── reference.py            # Danh mục chuẩn (Khoa, Ngành, 18 Tỉnh/Thành, 120 Môn học)
├── sql/
│   ├── 01_create_source_db.sql # Tạo CSDL nguồn edu_source (OLTP 3NF - 11 bảng)
│   ├── 02_create_dw.sql        # Tạo Kho dữ liệu edu_dw (Star Schema + Staging + Log)
│   ├── 03_procedures.sql       # Stored Procedures xử lý SCD2 & nạp 2 bảng Fact
│   ├── 04_olap_views.sql       # Views mô phỏng CUBE và Views phẳng cho Power BI
│   └── 05_olap_queries.sql     # 5 câu truy vấn OLAP trả lời 5 câu hỏi quản lý
├── generator/
│   └── generate_data.py        # Sinh ~240.000 dòng kết quả học tập + ~8.000 hồ sơ + lỗi chủ đích
├── etl/
│   ├── extract.py              # Bước Extract từ edu_source sang staging
│   ├── transform.py            # Bước Transform làm sạch, chuẩn hóa, tạo phiên bản SCD2
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

### Bước 2: Chạy toàn bộ hệ thống bằng 1 lệnh
Mở terminal tại thư mục `d:\Nam_Hoc\Nam_3\Kho du lieu\Bai_tap_lon\Code` và chạy:

```powershell
.venv\Scripts\python.exe run_all.py
```

Hoặc chạy riêng từng bước khi muốn demo cho giảng viên:
```powershell
# 1. Kiểm tra kết nối MariaDB
.venv\Scripts\python.exe -m common.check_connection

# 2. Sinh dữ liệu giả lập (~240.000 dòng) và nạp vào edu_source
.venv\Scripts\python.exe -m generator.generate_data

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

