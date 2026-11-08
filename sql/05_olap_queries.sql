-- =============================================================================
-- 05_olap_queries.sql
-- 5 câu hỏi phân tích OLAP theo mục 4.2 của Đề cương
-- Tương thích cả MySQL 8 và MariaDB 10.4+ (XAMPP)
-- =============================================================================
USE edu_dw;

-- =============================================================================
-- CÂU HỎI 1A (Roll-up & Drill-down với WITH ROLLUP):
-- Tỷ lệ đạt/rớt theo Khoa -> Môn học; drill-down theo Năm học -> Học kỳ
-- =============================================================================
SELECT
    COALESCE(mh.ten_khoa, 'TỔNG TOÀN TRƯỜNG')   AS ten_khoa,
    COALESCE(mh.ten_mon,  'TỔNG THEO KHOA')     AS ten_mon,
    COUNT(kq.ket_qua_id)                        AS tong_luot_hoc,
    SUM(kq.ket_qua_dat)                         AS so_luot_dat,
    SUM(1 - kq.ket_qua_dat)                     AS so_luot_rot,
    ROUND(100.0 * AVG(kq.ket_qua_dat), 2)       AS ty_le_dat_pct,
    ROUND(100.0 * AVG(1 - kq.ket_qua_dat), 2)   AS ty_le_rot_pct,
    ROUND(AVG(kq.diem_tong_ket), 2)             AS diem_tb_he_10
FROM fact_ket_qua_hoc_tap kq
INNER JOIN dim_mon_hoc mh ON kq.mon_hoc_key = mh.mon_hoc_key
GROUP BY mh.ten_khoa, mh.ten_mon WITH ROLLUP;

-- =============================================================================
-- CÂU HỎI 1B: Top 15 môn học có tỷ lệ rớt cao bất thường (so với trung bình khoa)
-- =============================================================================
SELECT
    mh.ma_mon,
    mh.ten_mon,
    mh.ten_khoa,
    mh.loai_mon,
    COUNT(kq.ket_qua_id)                        AS tong_luot_hoc,
    SUM(1 - kq.ket_qua_dat)                     AS so_luot_rot,
    ROUND(100.0 * AVG(1 - kq.ket_qua_dat), 2)   AS ty_le_rot_pct,
    ROUND(AVG(kq.diem_tong_ket), 2)             AS diem_tb_mon
FROM fact_ket_qua_hoc_tap kq
INNER JOIN dim_mon_hoc mh ON kq.mon_hoc_key = mh.mon_hoc_key
GROUP BY mh.ma_mon, mh.ten_mon, mh.ten_khoa, mh.loai_mon
ORDER BY ty_le_rot_pct DESC
LIMIT 15;

-- =============================================================================
-- CÂU HỎI 1C (Drill-down Năm học -> Học kỳ): Tỷ lệ đạt/rớt qua các năm học & học kỳ
-- =============================================================================
SELECT
    COALESCE(tg.nam_hoc, 'TỔNG CÁC NĂM')        AS nam_hoc,
    COALESCE(CAST(tg.hoc_ky_so AS CHAR), 'CẢ NĂM') AS hoc_ky_so,
    COUNT(kq.ket_qua_id)                        AS tong_luot_hoc,
    ROUND(100.0 * AVG(kq.ket_qua_dat), 2)       AS ty_le_dat_pct,
    ROUND(100.0 * AVG(1 - kq.ket_qua_dat), 2)   AS ty_le_rot_pct,
    ROUND(AVG(kq.diem_tong_ket), 2)             AS diem_tb_he_10
FROM fact_ket_qua_hoc_tap kq
INNER JOIN dim_thoi_gian tg ON kq.thoi_gian_key = tg.thoi_gian_key
GROUP BY tg.nam_hoc, tg.hoc_ky_so WITH ROLLUP;

-- =============================================================================
-- CÂU HỎI 2 (Dice: Ngành x Phương thức xét tuyển):
-- Điểm trung bình khác nhau thế nào giữa các phương thức xét tuyển?
-- =============================================================================
SELECT
    ten_nganh,
    ten_phuong_thuc,
    so_sinh_vien,
    so_luot_hoc_phan,
    diem_tb_he_10,
    diem_tb_he_4,
    ty_le_dat_pct
FROM vw_olap_cube_nganh_phuongthuc
ORDER BY
    (ten_nganh = 'ALL_NGANH'),
    ten_nganh,
    (ten_phuong_thuc = 'ALL_PHUONG_THUC'),
    diem_tb_he_10 DESC;

-- =============================================================================
-- CÂU HỎI 3 (Slice theo học kỳ đầu):
-- Điểm đầu vào có tương quan với điểm học kỳ đầu không?
-- Tổng hợp theo dải điểm đầu vào (quy đổi thang 30) & phương thức xét tuyển
-- =============================================================================
SELECT
    ten_phuong_thuc,
    CASE
        WHEN diem_quy_doi_30 < 18 THEN '1. Dưới 18'
        WHEN diem_quy_doi_30 < 21 THEN '2. Từ 18 đến <21'
        WHEN diem_quy_doi_30 < 24 THEN '3. Từ 21 đến <24'
        WHEN diem_quy_doi_30 < 27 THEN '4. Từ 24 đến <27'
        ELSE '5. Từ 27 trở lên'
    END                                         AS nhom_diem_dau_vao_30,
    COUNT(*)                                    AS so_sinh_vien,
    ROUND(AVG(diem_quy_doi_30), 2)              AS diem_dau_vao_tb_30,
    ROUND(AVG(gpa_hk1_he_10), 2)                AS gpa_hk1_tb_he_10,
    ROUND(AVG(gpa_hk1_he_4), 2)                 AS gpa_hk1_tb_he_4,
    ROUND(AVG(so_mon_rot_hk1), 2)               AS so_mon_rot_tb_hk1
FROM vw_olap_tuong_quan_dau_vao_hk1
GROUP BY ten_phuong_thuc, nhom_diem_dau_vao_30
ORDER BY ten_phuong_thuc, nhom_diem_dau_vao_30;

-- =============================================================================
-- CÂU HỎI 4 (Roll-up theo năm tuyển sinh):
-- Ngành nào có lượng hồ sơ, trúng tuyển và nhập học tăng/giảm qua các năm?
-- =============================================================================
SELECT
    COALESCE(ng.ten_nganh, 'TỔNG TOÀN TRƯỜNG')  AS ten_nganh,
    COALESCE(CAST(tg.nam AS CHAR), 'TẤT CẢ NĂM') AS nam_tuyen_sinh,
    COUNT(ts.tuyen_sinh_id)                     AS so_ho_so,
    SUM(ts.is_trung_tuyen)                      AS so_trung_tuyen,
    SUM(ts.is_nhap_hoc)                         AS so_nhap_hoc,
    ROUND(100.0 * AVG(ts.is_trung_tuyen), 2)    AS ty_le_trung_tuyen_pct,
    ROUND(100.0 * SUM(ts.is_nhap_hoc) / NULLIF(SUM(ts.is_trung_tuyen), 0), 2) AS ty_le_nhap_hoc_pct,
    ROUND(AVG(ts.diem_quy_doi_30), 2)           AS diem_xt_tb_thang_30
FROM fact_tuyen_sinh ts
INNER JOIN dim_nganh     ng ON ts.nganh_key     = ng.nganh_key
INNER JOIN dim_thoi_gian tg ON ts.thoi_gian_key = tg.thoi_gian_key
GROUP BY ng.ten_nganh, tg.nam WITH ROLLUP;

-- =============================================================================
-- CÂU HỎI 5 (Slice & Roll-up theo Vùng miền -> Tỉnh/thành):
-- Sinh viên theo tỉnh/thành nào có kết quả học tập nổi bật?
-- =============================================================================
SELECT
    COALESCE(sv.vung_mien,  'TỔNG CẢ NƯỚC')     AS vung_mien,
    COALESCE(sv.tinh_thanh, 'TỔNG VÙNG MIỀN')   AS tinh_thanh,
    COUNT(DISTINCT sv.ma_sv)                    AS so_sinh_vien,
    COUNT(kq.ket_qua_id)                        AS so_luot_hoc_phan,
    ROUND(AVG(kq.diem_tong_ket), 2)             AS diem_tb_he_10,
    ROUND(AVG(kq.diem_he_4), 2)                 AS diem_tb_he_4,
    ROUND(100.0 * AVG(kq.ket_qua_dat), 2)       AS ty_le_dat_pct,
    ROUND(100.0 * AVG(CASE WHEN kq.diem_tong_ket >= 8.0 THEN 1 ELSE 0 END), 2) AS ty_le_gioi_xuat_sac_pct
FROM fact_ket_qua_hoc_tap kq
INNER JOIN dim_sinh_vien sv ON kq.sinh_vien_key = sv.sinh_vien_key
GROUP BY sv.vung_mien, sv.tinh_thanh WITH ROLLUP;

