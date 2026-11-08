# KỊCH BẢN THUYẾT TRÌNH & DEMO BẢO VỆ BÀI TẬP LỚN KHO DỮ LIỆU

**Đề tài:** Xây dựng kho dữ liệu giáo dục phục vụ phân tích điểm số, tuyển sinh và kết quả học tập  
**Giảng viên hướng dẫn:** ThS. Mai Lam  
**Thời lượng dự kiến:** 10 – 15 phút trình bày + 5 phút trả lời câu hỏi phản biện  
**Người trình bày chính (Nhóm trưởng):** Cao Huy Hoàng (cùng Long và Tùng)

---

## PHẦN 1: KỊCH BẢN NÓI CHI TIẾT THEO TỪNG PHÚT

### 1. Mở đầu & Đặt vấn đề (1 – 2 phút)
> *"Kính thưa cô Mai Lam và các bạn, hôm nay nhóm em xin phép báo cáo bài tập lớn môn Kho dữ liệu với đề tài: **'Xây dựng kho dữ liệu giáo dục phục vụ phân tích điểm số, tuyển sinh và kết quả học tập'**.*  
>
> *Trong các trường đại học hiện nay, dữ liệu quản trị đào tạo thường bị phân mảnh ở nhiều phân hệ tác vụ (OLTP) rời rạc: phân hệ tuyển sinh quản lý hồ sơ và điểm đầu vào, phân hệ đăng ký học phần quản lý lớp, và phân hệ đào tạo quản lý điểm số. Việc nằm rải rác ở dạng chuẩn hóa 3NF khiến ban giám hiệu và phòng đào tạo rất khó trả lời các câu hỏi quản lý xuyên suốt mang tính quyết định, ví dụ như: 'Điểm đầu vào và phương thức xét tuyển có thực sự dự báo được kết quả học tập học kỳ đầu hay không?', 'Môn học nào đang là điểm nghẽn với tỷ lệ rớt cao bất thường?', hay 'Khi sinh viên chuyển ngành ở năm thứ hai thì lịch sử điểm số của các học kỳ trước được bảo toàn như thế nào?'.*  
>
> *Mục tiêu của nhóm em là thiết kế và triển khai một Kho dữ liệu giáo dục hoàn chỉnh trên nền tảng lược đồ hình sao (Star Schema), xây dựng pipeline ETL tự động làm sạch dữ liệu lỗi, cài đặt Stored Procedure xử lý Slowly Changing Dimension loại 2 (SCD2) và xây dựng giao diện Dashboard tương tác theo mô hình MVC để trực quan hóa toàn bộ câu trả lời."*

---

### 2. Thiết kế Kiến trúc Dữ liệu & Quy trình ETL (3 – 4 phút)
> *"Về mặt kiến trúc, dự án của nhóm bao gồm 3 tầng rõ rệt:*
>
> 1. ***Tầng CSDL nguồn (OLTP 3NF):*** *Gồm 11 bảng chuẩn hóa cao độ (`Khoa`, `Nganh`, `GiangVien`, `MonHoc`, `HocKy`, `SinhVien`, `LichSuChuyenNganh`, `LopHocPhan`, `DangKyHocPhan`, `PhuongThucXetTuyen`, `HoSoTuyenSinh`). Dữ liệu được sinh giả lập phản ánh quy luật thực tế với quy mô hơn **227.000 dòng** đăng ký học phần và hơn **8.000 dòng** hồ sơ tuyển sinh, đồng thời nhóm đã cố ý cài cắm hơn **2.500 bản ghi lỗi** (trùng lặp, thiếu điểm, điểm vượt thang, lệch công thức, tên tỉnh/giới tính không đồng nhất).*
> 2. ***Tầng Kho dữ liệu (Star Schema):*** *Nhóm thiết kế 2 bảng sự kiện dùng chung các chiều chuẩn hóa (**Conformed Dimensions**):*
>    - *`Fact_KetQuaHocTap` (Grain: một sinh viên trong một lớp học phần) lưu trữ điểm quá trình, điểm thi, điểm tổng kết, điểm hệ 4, điểm chữ và kết quả đạt/rớt.*
>    - *`Fact_TuyenSinh` (Grain: một hồ sơ xét tuyển) lưu điểm xét tuyển quy đổi thang 30, trạng thái trúng tuyển và nhập học.*
>    - *Điểm đặc biệt nhất trong mô hình là chiều `Dim_SinhVien` được áp dụng **SCD loại 2** để theo dõi lịch sử chuyển ngành và chuyển lớp.*
> 3. ***Quy trình ETL bằng Python (pandas, SQLAlchemy, PyMySQL) & Stored Procedure:***
>    - *Bước Extract đọc dữ liệu từ CSDL nguồn.*
>    - *Bước Transform loại bỏ 905 bản ghi trùng lặp, 905 bản ghi thiếu điểm, 679 bản ghi điểm ngoài thang [0,10], tính lại 671 điểm tổng kết bị sai lệch công thức, chuẩn hóa 18 tỉnh/thành và tách các phiên bản lịch sử sinh viên.*
>    - *Bước Load nạp toàn bộ Dimension trước, sau đó gọi Stored Procedure `sp_scd2_dim_sinh_vien` đóng bản ghi cũ, mở bản ghi mới và tra cứu `sinh_vien_key` vào Fact theo đúng khoảng thời gian hiệu lực của học kỳ.*

---

### 3. Demo Trực Tiếp Trên Web Dashboard (5 phút)
*(Chuyển sang màn hình trình duyệt tại `http://localhost:8050`)*

#### Màn 1: Trực quan hóa 5 câu hỏi quản lý OLAP (Tab 1)
> - *"Tại Tab 1, nhóm đã xây dựng Dashboard hoàn chỉnh trả lời 5 câu hỏi của Đề cương:*
>   - ***Câu hỏi 1A (Môn rớt cao bất thường):** Biểu đồ ngang chỉ ra ngay các môn vượt ngưỡng cảnh báo 5%: Toán cao cấp A1 rớt 10.23%, Kinh tế lượng 7.30%, Xử lý tín hiệu số 6.59%, Lập trình Java 6.47%.*
>   - ***Câu hỏi 1B (Drill-down Thời gian):** Điểm trung bình và tỷ lệ rớt qua từng học kỳ cho thấy các học kỳ đầu luôn có tỷ lệ rớt cao hơn do sinh viên chưa quen phương pháp học đại học.*
>   - ***Câu hỏi 2 (Dice Ngành × Phương thức):** So sánh điểm trung bình giữa xét Học bạ, thi THPT và ĐGNL ở từng ngành — nhóm ĐGNL và thi THPT luôn duy trì GPA tích lũy cao hơn nhóm xét học bạ.*
>   - ***Câu hỏi 3 (Biểu đồ phân tán Scatter):** Trục hoành là điểm đầu vào thang 30, trục tung là GPA kỳ 1. Các điểm dữ liệu phân bố dốc lên rõ rệt chứng minh điểm đầu vào có tương quan thuận mạnh mẽ với kết quả học tập ban đầu.*
>   - ***Câu hỏi 4 (Xu hướng tuyển sinh):** Các ngành CNTT, Kỹ thuật phần mềm, Marketing số có xu hướng nhập học tăng mạnh qua 4 năm, trong khi Điện tử viễn thông có xu hướng đi ngang.*
>   - ***Bộ lọc tương tác:** Em có thể chọn Khoa KHMT, lọc ngành IT, toàn bộ 6 thẻ KPI và các biểu đồ sẽ tự động lát cắt (Slice/Dice) theo thời gian thực."*

#### Màn 2: Chứng minh nghiệp vụ SCD loại 2 (Tab 2)
> - *"Bây giờ em xin chứng minh nghiệp vụ kỹ thuật quan trọng nhất: **Slowly Changing Dimension loại 2** tại Tab 2.*
> - *Trên màn hình là sinh viên `19IT001 – Phúc Văn Trần`. Ban đầu bạn học ngành Công nghệ thông tin (`IT`, lớp `19IT1`). Đến ngày `2021-08-20` (đầu năm thứ 3), bạn chuyển sang ngành Kỹ thuật phần mềm (`SE`, lớp `19SE1`).*
> - *Kho dữ liệu lưu giữ chính xác 2 phiên bản:*
>   - *Dòng cũ (`sinh_vien_key = 871`): `ngay_het_han` được đóng vào `2021-08-19`, cờ `is_current = 0`.*
>   - *Dòng mới (`sinh_vien_key = 8192`): `ngay_hieu_luc` từ `2021-08-20`, `ngay_het_han = 9999-12-31`, `is_current = 1`.*
> - *Ở bảng bên dưới, kết quả học tập 4 học kỳ đầu (2019–2021) vẫn gắn với ngành `IT`, còn 4 học kỳ sau (2021–2023) gắn với ngành `SE`.*
> - *Đặc biệt, giao diện cho phép em nhập mã SV bất kỳ, chọn ngành mới và bấm nút **Đổi ngành trực tiếp**: server sẽ ghi vào CSDL nguồn, chạy ETL Stored Procedure và cập nhật phiên bản mới ngay lập tức mà không nhân đôi dữ liệu (Idempotent)."*

#### Màn 3: Kiểm thử dữ liệu & Đo lường hiệu năng (Tab 3)
> - *"Tại Tab 3, nhóm chứng minh các tiêu chí đánh giá ở mục 4.3 của Đề cương:*
>   - ***10 Test Cases tự động:** Đối soát số dòng khớp tuyệt đối (227.267 nguồn = 224.778 Fact + 2.489 Reject), không có khóa ngoại mồ côi, không có điểm ngoài thang [0,10], chuẩn hóa 100% tỉnh thành. Kết quả **10/10 PASS**.*
>   - ***Đo hiệu năng (Benchmark):** Nhóm đã so sánh thời gian thực thi truy vấn tổng hợp trên quy mô 225.000 dòng. Kho dữ liệu Star Schema chạy nhanh hơn CSDL nguồn 3NF từ **1,56 lần đến 2,14 lần** do khóa thay thế là kiểu số nguyên nguyên bản và các chỉ số đã được phi chuẩn hóa sẵn."*

---

### 4. Kết luận & Hướng phát triển (1 phút)
> *"Tóm lại, đề tài của nhóm đã hoàn thành 100% mục tiêu: xây dựng kho dữ liệu giáo dục chuẩn Star Schema, giải quyết bài toán lịch sử bằng SCD loại 2, làm sạch hơn 2.500 lỗi dữ liệu, chứng minh hiệu năng vượt trội và cung cấp giao diện trực quan hóa theo mô hình MVC.  
> Hướng phát triển tiếp theo là kết nối luồng dữ liệu thời gian thực và áp dụng thuật toán học máy (Machine Learning) để dự báo sớm sinh viên có nguy cơ rớt môn ngay từ giữa học kỳ.  
> Nhóm em xin chân thành cảm ơn cô và sẵn sàng lắng nghe ý kiến đóng góp cùng các câu hỏi của cô ạ!"*

---

## PHẦN 2: BỘ CÂU HỎI PHẢN BIỆN GIẢNG VIÊN HAY HỎI & CÁCH TRẢ LỜI (CHEAT-SHEET)

### Câu hỏi 1: *"Tại sao nhóm lại dùng SCD loại 2 cho sinh viên mà không dùng SCD loại 1 hay loại 3?"*
- **Cách trả lời:**  
  *"Thưa cô, nếu dùng **SCD loại 1 (ghi đè)**, khi sinh viên đổi từ ngành IT sang SE thì toàn bộ điểm số các năm trước của sinh viên đó sẽ bị đổi thành ngành SE. Điều này làm sai lệch báo cáo lịch sử của Khoa CNTT (mất dữ liệu sinh viên cũ) và làm sai phân tích chương trình đào tạo.  
  Nếu dùng **SCD loại 3 (thêm cột ngành cũ/ngành mới)**, ta chỉ lưu được 1 lần thay đổi gần nhất và không thể gắn kết quả học tập của từng học kỳ vào đúng chiều không gian thời gian tương ứng.  
  Chỉ có **SCD loại 2** (tạo dòng mới, quản lý khoảng ngày hiệu lực và khóa thay thế `sinh_vien_key`) mới giải quyết triệt để bài toán: học kỳ nào thì tính điểm cho ngành đó, đồng thời vẫn biết được ngành hiện tại của sinh viên là gì."*

### Câu hỏi 2: *"Khi nạp Fact, làm sao em biết một dòng điểm học phần thuộc về phiên bản cũ hay phiên bản mới của sinh viên?"*
- **Cách trả lời:**  
  *"Dạ thưa cô, trong quy trình ETL và Stored Procedure `sp_load_fact_ket_qua_hoc_tap`, nhóm sử dụng điều kiện nối theo khoảng thời gian hiệu lực:  
  `WHERE HocKy.ngay_bat_dau BETWEEN Dim_SinhVien.ngay_hieu_luc AND Dim_SinhVien.ngay_het_han`.  
  Nhờ đó, mỗi học kỳ sẽ tự động nối với đúng `sinh_vien_key` của phiên bản đang có hiệu lực tại thời điểm sinh viên đó học môn học."*

### Câu hỏi 3: *"Tại sao truy vấn trên Kho dữ liệu (Star Schema) lại chạy nhanh hơn CSDL nguồn (OLTP 3NF)?"*
- **Cách trả lời:**  
  *"Dạ có 3 nguyên nhân chính:  
  1. **Giảm thiểu số lượng JOIN:** Ở OLTP 3NF để thống kê điểm theo Khoa, Ngành và Học kỳ phải JOIN qua 5-6 bảng trung gian (`DangKyHocPhan` -> `LopHocPhan` -> `MonHoc` -> `Khoa`...). Trong khi ở Star Schema, bảng Fact nối trực tiếp tới các Dimension chỉ qua 1 bước JOIN.  
  2. **Tối ưu hóa khóa liên kết:** Star Schema sử dụng khóa thay thế số nguyên (`INT surrogate key`) có đánh chỉ mục, việc so khớp số nguyên trong bộ nhớ nhanh hơn nhiều so với việc JOIN trên các chuỗi ký tự (`VARCHAR`) của mã sinh viên, mã môn học.  
  3. **Tiền tính toán (Pre-computation):** Điểm chữ, điểm hệ 4, và cờ đạt/rớt (`ket_qua_dat`) đã được tính sẵn trong bước ETL, truy vấn trên kho chỉ việc `SUM` và `AVG` trực tiếp mà không phải chạy hàm `CASE WHEN` tính toán lại trên từng dòng."*

### Câu hỏi 4: *"Trong đề cương dùng MySQL nhưng trong thực tế nhóm dùng MariaDB của XAMPP, có khác biệt gì về kỹ thuật không?"*
- **Cách trả lời:**  
  *"Dạ thưa cô, MariaDB 10.4 tương thích hoàn toàn với MySQL về chuẩn cú pháp SQL, stored procedure và kiểu dữ liệu. Điểm khác biệt duy nhất là MariaDB 10.4 chưa hỗ trợ hàm `GROUPING()` như MySQL 8. Nhóm đã xử lý tương thích bằng cách dùng hàm `COALESCE(cột, 'TỔNG TOÀN TRƯỜNG')` kết hợp với mệnh đề `GROUP BY ... WITH ROLLUP`, đảm bảo câu lệnh chạy đúng chuẩn trên cả MySQL 8 và MariaDB."*

### Câu hỏi 5: *"Kiến trúc MVC trong ứng dụng Web của nhóm được tổ chức như thế nào?"*
- **Cách trả lời:**  
  *"Dạ thưa cô, nhóm tách bạch mã nguồn thành 3 tầng rõ rệt:  
  - **Tầng Model (`mvc/models/`):** Chứa các module nghiệp vụ CSDL độc lập (`olap_model.py`, `scd2_model.py`, `etl_model.py`, `sql_model.py`). Tầng này không phụ thuộc vào giao diện hay giao thức HTTP.  
  - **Tầng View (`mvc/views/`, `web/index.html`):** Phụ trách định dạng hiển thị, gồm giao diện Web SPA trực quan hóa bằng Chart.js và module `view.py` đóng gói phản hồi JSON/HTML.  
  - **Tầng Controller (`mvc/controllers/`):** Tiếp nhận yêu cầu từ client, kiểm tra tính hợp lệ của tham số, gọi Model tương ứng và chuyển kết quả cho View (`router.py`, `olap_controller.py`, `scd2_controller.py`...).  
  Nhờ kiến trúc MVC, code rất dễ bảo trì, dễ mở rộng và có thể kết nối với bất kỳ frontend nào mà không cần viết lại logic truy vấn kho."*

