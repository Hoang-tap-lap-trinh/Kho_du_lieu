# HƯỚNG DẪN CHẠY HỆ THỐNG VÀ SỬ DỤNG WEB DASHBOARD

Tài liệu này hướng dẫn chi tiết cách khởi chạy đồ án **Kho dữ liệu giáo dục VKU** và cách thao tác tương tác trên **Web Dashboard** (dùng khi kiểm tra bài hoặc khi thuyết trình / demo trước giảng viên).

---

## PHẦN 1: CÁCH MỞ VÀ CHẠY TRANG WEB DASHBOARD

Bạn có **2 cách** để mở trang Web Dashboard (cả 2 cách đều đã có sẵn toàn bộ dữ liệu 224.778 dòng kết quả học tập và 7.964 hồ sơ tuyển sinh):

### Cách 1: Chạy Web Server kết nối trực tiếp MariaDB (Khuyên dùng khi Demo)
Chế độ này kết nối trực tiếp tới 2 database `edu_dw` và `edu_source` trong MariaDB (XAMPP), cho phép bạn lọc dữ liệu theo thời gian thực, bấm nút đổi ngành sinh viên (SCD2) trực tiếp vào CSDL và gõ câu lệnh SQL tuỳ ý.

1. Mở **XAMPP Control Panel** → đảm bảo dòng **MySQL** đang ở trạng thái **Running (màu xanh)**.
2. Mở thư mục `d:\Nam_Hoc\Nam_3\Kho du lieu\Bai_tap_lon\Code`, **nhấp đúp chuột** vào file:
   👉 [`chay_web.bat`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/chay_web.bat)
   *(Hoặc mở Terminal tại thư mục `Code` và chạy lệnh: `.venv\Scripts\python.exe web_app.py`)*
3. Trình duyệt sẽ tự động mở địa chỉ: **http://localhost:8050**

> [!NOTE]
> Hệ thống Web đã được tái cấu trúc hoàn chỉnh theo chuẩn kiến trúc **MVC (Model - View - Controller)** trong thư mục `mvc/`:
> - **Model (`mvc/models/`)**: Quản lý truy vấn dữ liệu Kho `edu_dw` và CSDL nguồn `edu_source` (`olap_model.py`, `scd2_model.py`, `etl_model.py`, `sql_model.py`).
> - **View (`mvc/views/`, `web/`)**: Định dạng giao diện Web (`web/index.html`) và phản hồi (`view.py`).
> - **Controller (`mvc/controllers/`)**: Tiếp nhận yêu cầu, kiểm tra dữ liệu và phân luồng nghiệp vụ (`router.py`, `olap_controller.py`, `scd2_controller.py`, `etl_controller.py`, `sql_controller.py`).

---

### Cách 2: Mở trực tiếp file HTML độc lập (Không cần bật Server hay XAMPP)
Nếu bạn mang sang máy khác chưa cài Python/XAMPP hoặc gửi file cho các bạn trong nhóm xem nhanh:

- Chỉ cần **nhấp đúp chuột** vào file:
  👉 [`web/dashboard_standalone.html`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/web/dashboard_standalone.html) (hoặc [`web/index.html`](file:///d:/Nam_Hoc/Nam_3/Kho%20du%20lieu/Bai_tap_lon/Code/web/index.html))
- File này đã nhúng sẵn toàn bộ số liệu thống kê, biểu đồ OLAP, lịch sử SCD2, log ETL và 10 Test Cases nên hoạt động ngay trên mọi trình duyệt (Chrome, Edge, Firefox).

---

## PHẦN 2: HƯỚNG DẪN SỬ DỤNG 4 TAB TRÊN TRANG WEB

Giao diện trang Web được chia thành **4 Tab chức năng** trên thanh menu góc trên bên phải, bám sát toàn bộ yêu cầu trong Đề cương:

---

### TAB 1: `1. Dashboard 5 Câu hỏi OLAP`
Tab này dùng để trả lời trực quan **5 câu hỏi quản lý đào tạo** ở mục 4.2 của Đề cương.

1. **Thanh bộ lọc đa chiều (Slice / Dice / Roll-up / Drill-down) ở trên cùng:**
   - Chọn **Khoa** (ví dụ `KHMT – Khoa Khoa học máy tính`), **Ngành đào tạo** (ví dụ `IT – Công nghệ thông tin`), **Năm học** (`2019-2020` → `2025-2026`), hoặc **Vùng miền**.
   - Ngay khi bạn chọn, **6 thẻ KPI** và **6 biểu đồ** bên dưới sẽ tự động tính toán và vẽ lại theo đúng lát cắt (Slice/Dice) bạn chọn.
   - Bấm nút **"Đặt lại bộ lọc"** để quay về toàn trường.
2. **6 Thẻ chỉ số KPI tổng quan:**
   - Hiển thị: Tổng lượt kết quả học tập (`224.778`), Số sinh viên (`4.948`), Điểm trung bình hệ 10 & hệ 4 (`7.18 / 2.79`), Tỷ lệ Đạt/Rớt (`98.76% / 1.24%`), Hồ sơ tuyển sinh (`7.964`), và Số bản ghi lịch sử SCD2 (`149`) cùng số bản ghi lỗi đã lọc (`2.537`).
3. **6 Biểu đồ phân tích OLAP:**
   - **Câu hỏi 1A (Top 15 môn có tỷ lệ rớt cao bất thường):** Các môn vượt ngưỡng 5% được tô **màu đỏ** nổi bật (*Toán cao cấp A1: 10.23%*, *Kinh tế lượng: 7.30%*, *Xử lý tín hiệu số: 6.59%*, *Lập trình Java: 6.47%*).
   - **Câu hỏi 1B (Drill-down theo Năm học → Học kỳ):** Biểu đồ đường kép thể hiện diễn biến Điểm trung bình và Tỷ lệ rớt qua từng học kỳ.
   - **Câu hỏi 2 (Dice Ngành × Phương thức xét tuyển):** Biểu đồ cột nhóm so sánh điểm trung bình của sinh viên trúng tuyển theo 3 phương thức (*Học bạ THPT*, *Thi tốt nghiệp THPT*, *Đánh giá năng lực*) ở từng ngành.
   - **Câu hỏi 3 (Slice Học kỳ 1 – Biểu đồ phân tán Scatter):** Trục ngang là *Điểm xét tuyển quy đổi thang 30*, trục dọc là *GPA Học kỳ 1*. Các đám mây điểm dốc lên từ trái sang phải chứng minh điểm đầu vào có tương quan thuận rõ rệt với kết quả học kỳ đầu.
   - **Câu hỏi 4 (Roll-up theo Năm tuyển sinh 2019–2022):** Biểu đồ đường cho thấy các ngành tăng trưởng mạnh (*Công nghệ thông tin, Khoa học máy tính, Marketing số, Thương mại điện tử*) và các ngành giảm nhẹ (*Quản trị kinh doanh, Điện tử viễn thông*).
   - **Câu hỏi 5 (Slice theo Tỉnh/Thành phố):** So sánh tỷ lệ sinh viên đạt loại Giỏi/Xuất sắc giữa 18 tỉnh/thành phố.

---

### TAB 2: `2. Tương tác SCD Loại 2 (Đổi ngành)`
Tab này dùng để **minh họa trực tiếp Slowly Changing Dimension loại 2 (`SCD2`)** khi giảng viên hỏi *"Kho dữ liệu xử lý sinh viên đổi ngành như thế nào?"*.

1. **Tra cứu sinh viên đã đổi ngành:**
   - Chọn một sinh viên trong danh sách thả xuống **"Chọn nhanh sinh viên đã có lịch sử đổi ngành"** (mặc định đang chọn `19IT001 – Phúc Văn Trần`), hoặc gõ mã sinh viên bất kỳ (ví dụ `20IT002`) vào ô tìm kiếm rồi bấm **Tìm**.
2. **Quan sát 2 bảng kết quả bên phải:**
   - **Bảng trên (`dim_sinh_vien`):** Hiển thị các dòng phiên bản lịch sử của sinh viên đó:
     - Dòng cũ (`sinh_vien_key = 871`, ngành `IT`): đã được đóng bằng `ngay_het_han = 2021-08-19` và cờ `is_current = 0 (Lịch sử)`.
     - Dòng mới (`sinh_vien_key = 8192`, ngành `SE`): có hiệu lực từ `2021-08-20`, `ngay_het_han = 9999-12-31` và cờ `is_current = 1 (Hiện tại)`.
   - **Bảng dưới (`fact_ket_qua_hoc_tap`):** Hiển thị điểm trung bình từng học kỳ của sinh viên đó — bạn chỉ cho giảng viên thấy các học kỳ năm `2019-2020` và `2020-2021` vẫn gắn với `sinh_vien_key = 871` (ngành **Công nghệ thông tin**), còn từ `2021-2022` trở đi mới gắn với `sinh_vien_key = 8192` (ngành **Kỹ thuật phần mềm**).
3. **Demo đổi ngành trực tiếp ngay trên Web:**
   - Ở khung bên trái, nhập **Mã sinh viên** (ví dụ `19CS001`), chọn **Ngày hiệu lực chuyển ngành** (ví dụ `2021-08-20`), chọn **Ngành chuyển đến** (ví dụ `IT – Công nghệ thông tin`).
   - Bấm nút **"Cập nhật Đổi ngành ở Nguồn & Chạy SCD2 vào Kho"**.
   - Hệ thống sẽ tự động cập nhật bảng `SinhVien` + `LichSuChuyenNganh` ở `edu_source`, chạy Stored Procedure `sp_scd2_dim_sinh_vien` trong `edu_dw`, và làm mới ngay bảng phiên bản lịch sử bên phải!

---

### TAB 3: `3. ETL Log, Làm sạch & 10 Test Cases`
Tab này dùng để chứng minh **Quy trình ETL làm sạch dữ liệu lỗi** và **Tiêu chí đánh giá mục 4.3 của Đề cương**:

1. **Bảng 10 Test Cases Kiểm thử Chất lượng Dữ liệu:**
   - Hiển thị đầy đủ 10 mã kiểm thử (`TC01` → `TC10`) cùng kết quả kỳ vọng, kết quả thực tế và nhãn `PASS` màu xanh.
   - Có nút **"Chạy lại 10 Test Cases"** để kiểm tra trực tiếp trước mặt giảng viên.
2. **Biểu đồ & Bảng So sánh Hiệu năng (Benchmark OLTP 3NF vs DW Star Schema):**
   - Thể hiện trực quan thời gian chạy truy vấn trên Kho dữ liệu Star Schema (cột màu xanh) nhanh gấp **1,56x – 2,14x** so với truy vấn trực tiếp trên CSDL nguồn 3NF (cột màu đỏ).
3. **Bảng so sánh Trước & Sau khi làm sạch (`etl_data_quality`):**
   - Liệt kê từng loại lỗi chủ đích đã phát hiện ở nguồn (`905` dòng trùng, `905` dòng thiếu điểm, `679` dòng ngoài thang `0–10`, `671` dòng lệch điểm tổng kết, `590` họ tên lỗi, `292` tỉnh/thành lỗi...) đưa về **`0` lỗi** sau ETL.
4. **Bảng Nhật ký ETL (`etl_log`):**
   - Hiển thị từng bước `EXTRACT` → `TRANSFORM` → `LOAD` với số dòng đọc, số dòng nạp và số dòng bị loại.

---

### TAB 4: `4. Truy vấn SQL Trực tiếp`
Tab này là công cụ **SQL Playground** ngay trên trình duyệt:

1. Chọn CSDL cần truy vấn (`edu_dw` hoặc `edu_source`).
2. Chọn nhanh một trong **7 câu truy vấn mẫu** ở thanh thả xuống (Câu hỏi 1 đến Câu hỏi 5 có dùng `WITH ROLLUP`, `CUBE`, truy vấn kiểm tra SCD2, hoặc xem 50 bản ghi lỗi bị loại trong `etl_reject`).
3. Hoặc tự gõ bất kỳ câu lệnh `SELECT ...` nào vào ô soạn thảo rồi bấm **"Chạy Truy Vấn (Execute SQL)"** — bảng kết quả và thời gian chạy (ms) sẽ hiện ngay bên dưới.

---

## PHẦN 3: CÁC LỆNH TERMINAL DỰ PHÒNG (KHI CẦN CHẠY LẠI TỪ ĐẦU)

Nếu muốn chạy lại từng phần bằng dòng lệnh trong thư mục `d:\Nam_Hoc\Nam_3\Kho du lieu\Bai_tap_lon\Code`:

```powershell
# 1. Chạy lại toàn bộ từ A đến Z (Kiểm tra kết nối -> ETL -> SCD2 -> Test -> Benchmark)
.venv\Scripts\python.exe run_all.py

# 2. Sinh lại toàn bộ dữ liệu giả lập từ đầu vào edu_source (nếu muốn làm mới hoàn toàn)
.venv\Scripts\python.exe run_all.py --force-generate

# 3. Chỉ chạy quy trình ETL
.venv\Scripts\python.exe -m etl.pipeline

# 4. Chỉ chạy kịch bản demo đổi ngành SCD2 trên terminal
.venv\Scripts\python.exe -m etl.demo_scd2

# 5. Chỉ chạy 10 Test Cases kiểm thử chất lượng dữ liệu
.venv\Scripts\python.exe -m tests.run_dq_tests

# 6. Khởi động Web Dashboard tại http://localhost:8050
.venv\Scripts\python.exe web_app.py
```

