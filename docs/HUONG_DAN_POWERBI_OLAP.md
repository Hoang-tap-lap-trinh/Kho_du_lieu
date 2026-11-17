# HƯỚNG DẪN XÂY DỰNG BÁO CÁO POWER BI & OLAP
**Đề tài:** Xây dựng kho dữ liệu giáo dục phục vụ phân tích điểm số, tuyển sinh và kết quả học tập  
**Thành viên phụ trách:** Nguyễn Thanh Tùng (24ITB220)  
**Đơn vị:** Trường Đại học CNTT&TT Việt - Hàn (VKU)

---

## 1. TỔNG QUAN VÀ MỤC TIÊU
Tài liệu này hướng dẫn chi tiết cách xây dựng bộ Báo cáo Quản trị Thông minh (Power BI Dashboard) kết nối trực tiếp với Kho dữ liệu `edu_dw` (hoặc các tệp dữ liệu sạch CSV trong thư mục `Code/output/`). Báo cáo giúp Ban Giám hiệu, Phòng Đào tạo và các Khoa phân tích đa chiều về:
1. Xu hướng và tỷ lệ tuyển sinh - nhập học qua các năm (2019 - 2024).
2. Tỷ lệ đạt/rớt theo Khoa, Ngành và từng Môn học.
3. Mối tương quan giữa điểm tuyển sinh đầu vào và kết quả học tập đại học.
4. Phân bổ học lực và tỷ lệ sinh viên Giỏi/Xuất sắc theo 18 tỉnh/thành miền Trung - Tây Nguyên.

---

## 2. KẾT NỐI DỮ LIỆU VÀO POWER BI DESKTOP

Có **2 phương thức kết nối** linh hoạt:

### Phương thức A: Kết nối trực tiếp CSDL MariaDB / MySQL (Khuyến nghị khi demo trực tiếp)
1. Mở **Power BI Desktop**.
2. Chọn **Get Data** -> Chọn **MySQL database** (hoặc **ODBC** nếu dùng DSN).
3. Nhập thông tin kết nối:
   - **Server:** `localhost:3306`
   - **Database:** `edu_dw`
   - **Data Connectivity mode:** Chọn `Import` (để tối ưu tốc độ và dùng đầy đủ tính năng DAX).
4. Tại cửa sổ **Navigator**, tích chọn các bảng và view:
   - `fact_ket_qua_hoc_tap`
   - `fact_tuyen_sinh`
   - `dim_sinh_vien`
   - `dim_hoc_phan`
   - `dim_giang_vien`
   - `dim_thoi_gian`
   - `dim_nganh`
   - `dim_tinh_thanh`
   - `dim_phuong_thuc_xt`
5. Nhấn **Load**.

### Phương thức B: Nhập trực tiếp từ các file CSV đã xuất (Nhanh và độc lập)
Nếu máy chấm bài hoặc máy giảng viên không cài sẵn MariaDB, bạn có thể nạp trực tiếp các file CSV trong thư mục `Code/output/`:
- `Code/output/olap_q1_ty_le_rot_mon.csv`
- `Code/output/olap_q2_diem_tb_theo_nganh.csv`
- `Code/output/olap_q3_diem_dau_vao_vs_kqht.csv`
- `Code/output/olap_q4_xu_huong_tuyen_sinh.csv`
- `Code/output/olap_q5_ket_qua_theo_tinh_thanh.csv`
- `Code/output/benchmark_result.csv`
- `Code/output/test_cases_result.csv`

---

## 3. THIẾT KẾ DATA MODEL (LƯỢC ĐỒ HÌNH SAO - STAR SCHEMA)

Chuyển sang tab **Model View** trong Power BI để kiểm tra và thiết lập các mối quan hệ (Relationships) theo chuẩn **1 - Nhiều (1:*)** với chiều lọc đơn (Single Direction):

```
       [dim_sinh_vien] (1) --------- (*) [fact_ket_qua_hoc_tap]
       [dim_hoc_phan]  (1) --------- (*) [fact_ket_qua_hoc_tap]
       [dim_giang_vien](1) --------- (*) [fact_ket_qua_hoc_tap]
       [dim_thoi_gian] (1) --------- (*) [fact_ket_qua_hoc_tap]

       [dim_sinh_vien] (1) --------- (*) [fact_tuyen_sinh]
       [dim_nganh]     (1) --------- (*) [fact_tuyen_sinh]
       [dim_ptxt]      (1) --------- (*) [fact_tuyen_sinh]
       [dim_thoi_gian] (1) --------- (*) [fact_tuyen_sinh]
       [dim_tinh_thanh](1) --------- (*) [fact_tuyen_sinh]
```

*Lưu ý quan trọng:* Khóa liên kết giữa Fact và Dim là các khóa thay thế (Surrogate Keys): `sinh_vien_key`, `hoc_phan_key`, `giang_vien_key`, `date_key`, `nganh_key`, `tinh_thanh_key`.

---

## 4. TẬP HỢP CÔNG THỨC ĐO LƯỜNG (DAX MEASURES)

Tạo một bảng rỗng đặt tên là `_Measures` để gom nhóm toàn bộ các độ đo quản trị:

### 4.1. Độ đo Tuyển sinh
```dax
-- Tổng số hồ sơ đăng ký
TongHoSo = COUNTROWS(fact_tuyen_sinh)

-- Số thí sinh trúng tuyển
SoTrungTuyen = CALCULATE(
    COUNTROWS(fact_tuyen_sinh),
    fact_tuyen_sinh[trang_thai] = "Trúng tuyển"
)

-- Số thí sinh đã thực tế nhập học
SoNhapHoc = CALCULATE(
    COUNTROWS(fact_tuyen_sinh),
    fact_tuyen_sinh[da_nhap_hoc] = 1
)

-- Tỷ lệ trúng tuyển (%)
TyLeTrungTuyen = DIVIDE([SoTrungTuyen], [TongHoSo], 0)

-- Tỷ lệ nhập học trên số trúng tuyển (%)
TyLeNhapHoc = DIVIDE([SoNhapHoc], [SoTrungTuyen], 0)

-- Điểm xét tuyển trung bình
DiemXetTuyenTB = AVERAGE(fact_tuyen_sinh[diem_xet_tuyen])
```

### 4.2. Độ đo Học tập & Đào tạo
```dax
-- Tổng số lượt học phần đăng ký
TongLuotHocPhan = COUNTROWS(fact_ket_qua_hoc_tap)

-- Tổng số sinh viên duy nhất
TongSinhVien = DISTINCTCOUNT(fact_ket_qua_hoc_tap[sinh_vien_key])

-- Điểm trung bình hệ 10
DiemTB_He10 = AVERAGE(fact_ket_qua_hoc_tap[diem_tong_ket])

-- Điểm trung bình hệ 4
DiemTB_He4 = AVERAGE(fact_ket_qua_hoc_tap[diem_he_4])

-- Số lượt qua môn (Đạt)
SoLuotDat = CALCULATE(
    COUNTROWS(fact_ket_qua_hoc_tap),
    fact_ket_qua_hoc_tap[ket_qua] = "Đạt"
)

-- Số lượt rớt môn (Học lại)
SoLuotRot = CALCULATE(
    COUNTROWS(fact_ket_qua_hoc_tap),
    fact_ket_qua_hoc_tap[ket_qua] = "Rớt"
)

-- Tỷ lệ đạt (%)
TyLeDat = DIVIDE([SoLuotDat], [TongLuotHocPhan], 0)

-- Tỷ lệ rớt môn (%)
TyLeRot = DIVIDE([SoLuotRot], [TongLuotHocPhan], 0)

-- Tỷ lệ sinh viên loại Giỏi và Xuất sắc (Điểm chữ A, A+)
TyLeGioiXuatSac = DIVIDE(
    CALCULATE(
        COUNTROWS(fact_ket_qua_hoc_tap),
        fact_ket_qua_hoc_tap[diem_chu] IN {"A", "A+"}
    ),
    [TongLuotHocPhan],
    0
)
```

---

## 5. THIẾT KẾ CÁC TRANG BÁO CÁO (DASHBOARD PAGES)

### Trang 1: Tổng quan Tuyển sinh & Địa lý (Admissions & Geography)
- **Thẻ Card KPI hàng trên:** `Tổng hồ sơ`, `Trúng tuyển`, `Nhập học`, `Tỷ lệ nhập học (%)`, `Điểm xét tuyển TB`.
- **Biểu đồ Cột nhóm (Clustered Column Chart):** Số lượng hồ sơ và nhập học theo từng Năm học và Ngành đào tạo.
- **Biểu đồ Tròn/Vành khăn (Donut Chart):** Tỷ trọng hồ sơ theo Phương thức xét tuyển (Điểm THPT vs Đánh giá năng lực vs Tuyển thẳng).
- **Bản đồ / Phân bổ (Map/Bar Chart):** Số lượng thí sinh theo Tỉnh/thành và Vùng miền (Bắc Trung Bộ vs Duyên hải Nam Trung Bộ).
- **Bộ lọc (Slicers):** Năm tuyển sinh, Ngành học, Tỉnh/thành.

### Trang 2: Kết quả Học tập & Phân tích Rớt môn (Academic & Failure Analysis)
- **Thẻ Card KPI hàng trên:** `Tổng lượt học phần`, `Điểm TB Hệ 10`, `Điểm TB Hệ 4`, `Tỷ lệ qua môn (%)`, `Tỷ lệ Giỏi/Xuất sắc (%)`.
- **Biểu đồ Cột xếp chồng (100% Stacked Bar Chart):** Tỷ lệ Đạt vs Rớt theo từng Ngành và Khóa học.
- **Bảng ma trận (Matrix Table):** Top 10 môn học có tỷ lệ rớt cao nhất (Mã môn, Tên môn, Số tín chỉ, Tỷ lệ rớt %, Điểm TB).
- **Biểu đồ phân tán (Scatter Plot):** Mối tương quan giữa Điểm thi tuyển sinh đầu vào và Điểm trung bình tích lũy GPA.
- **Bộ lọc (Slicers):** Khoa, Ngành, Năm học, Học kỳ, Loại môn học.

### Trang 3: Giảng viên & Đổi ngành SCD Type 2 (Faculty & SCD2 Audit)
- **Biểu đồ Thanh ngang:** Điểm trung bình và tỷ lệ qua môn theo Học vị giảng viên (Tiến sĩ, Thạc sĩ, Cử nhân).
- **Bảng đối soát SCD2:** Danh sách sinh viên chuyển ngành (Mã SV, Họ tên, Ngành cũ, Ngành mới, Ngày hiệu lực, Ngày hết hạn, Cờ hiện tại `is_current`).
- **Thẻ đo lường chất lượng:** 10/10 Test Cases PASS, Tỷ lệ nạp kho thành công 98.9%.

---

## 6. XUẤT BẢN VÀ LƯU TRỮ SẢN PHẨM
1. Lưu file thiết kế thành: `docs/Bao_cao_OLAP_VKU.pbix`.
2. Xuất file PDF phục vụ in ấn nộp bài: **File** -> **Export** -> **Export to PDF** -> Lưu thành `docs/Bao_cao_OLAP_VKU.pdf`.
3. Chụp các ảnh chụp màn hình đẹp (1920x1080) để bạn Hoàng và bạn Long chèn vào Slide thuyết trình PowerPoint và Báo cáo Word.

