-- =============================================================================
-- 04_olap_views.sql
-- Các View tổng hợp OLAP (mô phỏng CUBE và ROLLUP) và View phẳng phục vụ Power BI
-- Tương thích cả MySQL 8 và MariaDB 10.4+ (XAMPP)
-- =============================================================================
USE edu_dw;

-- -----------------------------------------------------------------------------
-- 1. View phẳng kết quả học tập (dùng kéo-thả trực tiếp trong Power BI / Metabase)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_ket_qua_hoc_tap_chi_tiet AS
SELECT
    kq.ket_qua_id,
    kq.ma_dang_ky,
    kq.ma_lhp,
    sv.sinh_vien_key,
    sv.ma_sv,
    sv.ho_ten           AS ho_ten_sv,
    sv.gioi_tinh,
    sv.tinh_thanh,
    sv.vung_mien,
    sv.nam_nhap_hoc,
    sv.ma_lop,
    sv.is_current       AS phien_ban_sv_hien_tai,
    ng.nganh_key,
    ng.ma_nganh,
    ng.ten_nganh,
    ng.ma_khoa          AS ma_khoa_sinh_vien,
    ng.ten_khoa         AS ten_khoa_sinh_vien,
    ng.he_dao_tao,
    mh.mon_hoc_key,
    mh.ma_mon,
    mh.ten_mon,
    mh.so_tin_chi,
    mh.loai_mon,
    mh.ma_khoa          AS ma_khoa_mon_hoc,
    mh.ten_khoa         AS ten_khoa_mon_hoc,
    gv.giang_vien_key,
    gv.ma_gv,
    gv.ho_ten           AS ho_ten_gv,
    gv.hoc_vi,
    tg.thoi_gian_key,
    tg.hoc_ky,
    tg.hoc_ky_so,
    tg.nam_hoc,
    tg.ten_hoc_ky,
    kq.diem_qua_trinh,
    kq.diem_thi,
    kq.diem_tong_ket,
    kq.diem_chu,
    kq.diem_he_4,
    kq.ket_qua_dat,
    (1 - kq.ket_qua_dat) AS ket_qua_rot
FROM fact_ket_qua_hoc_tap kq
INNER JOIN dim_sinh_vien  sv ON kq.sinh_vien_key  = sv.sinh_vien_key
INNER JOIN dim_nganh      ng ON kq.nganh_key      = ng.nganh_key
INNER JOIN dim_mon_hoc    mh ON kq.mon_hoc_key    = mh.mon_hoc_key
INNER JOIN dim_giang_vien gv ON kq.giang_vien_key = gv.giang_vien_key
INNER JOIN dim_thoi_gian  tg ON kq.thoi_gian_key  = tg.thoi_gian_key;

-- -----------------------------------------------------------------------------
-- 2. View phẳng tuyển sinh (phục vụ Power BI)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_tuyen_sinh_chi_tiet AS
SELECT
    ts.tuyen_sinh_id,
    ts.ma_ho_so,
    ng.nganh_key,
    ng.ma_nganh,
    ng.ten_nganh,
    ng.ma_khoa,
    ng.ten_khoa,
    ng.he_dao_tao,
    pt.ptxt_key,
    pt.ma_ptxt,
    pt.ten_phuong_thuc,
    pt.thang_diem,
    tg.nam              AS nam_tuyen_sinh,
    tg.quy              AS quy_nop_ho_so,
    tg.thang            AS thang_nop_ho_so,
    ts.gioi_tinh,
    ts.tinh_thanh,
    ts.diem_xet_tuyen,
    ts.diem_quy_doi_30,
    ts.is_trung_tuyen,
    ts.is_nhap_hoc,
    ts.sinh_vien_key
FROM fact_tuyen_sinh ts
INNER JOIN dim_nganh                 ng ON ts.nganh_key     = ng.nganh_key
INNER JOIN dim_phuong_thuc_xet_tuyen pt ON ts.ptxt_key      = pt.ptxt_key
INNER JOIN dim_thoi_gian             tg ON ts.thoi_gian_key = tg.thoi_gian_key;

-- -----------------------------------------------------------------------------
-- 3. View mô phỏng CUBE (Ngành x Phương thức xét tuyển x Học kỳ)
-- Vì MySQL / MariaDB không có toán tử CUBE, ta mô phỏng bằng UNION ALL các tổ hợp
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_olap_cube_nganh_phuongthuc AS
-- Chi tiết: Ngành x Phương thức
SELECT
    ng.ten_nganh                                     AS ten_nganh,
    pt.ten_phuong_thuc                               AS ten_phuong_thuc,
    COUNT(DISTINCT sv.ma_sv)                         AS so_sinh_vien,
    COUNT(kq.ket_qua_id)                             AS so_luot_hoc_phan,
    ROUND(AVG(kq.diem_tong_ket), 2)                  AS diem_tb_he_10,
    ROUND(AVG(kq.diem_he_4), 2)                      AS diem_tb_he_4,
    ROUND(100.0 * AVG(kq.ket_qua_dat), 2)            AS ty_le_dat_pct
FROM fact_ket_qua_hoc_tap kq
INNER JOIN dim_sinh_vien             sv ON kq.sinh_vien_key = sv.sinh_vien_key
INNER JOIN dim_nganh                 ng ON kq.nganh_key     = ng.nganh_key
INNER JOIN fact_tuyen_sinh           ts ON ts.sinh_vien_key = sv.sinh_vien_key
INNER JOIN dim_phuong_thuc_xet_tuyen pt ON ts.ptxt_key      = pt.ptxt_key
GROUP BY ng.ten_nganh, pt.ten_phuong_thuc

UNION ALL

-- Tổng theo Ngành (mọi phương thức)
SELECT
    ng.ten_nganh                                     AS ten_nganh,
    'ALL_PHUONG_THUC'                                AS ten_phuong_thuc,
    COUNT(DISTINCT sv.ma_sv)                         AS so_sinh_vien,
    COUNT(kq.ket_qua_id)                             AS so_luot_hoc_phan,
    ROUND(AVG(kq.diem_tong_ket), 2)                  AS diem_tb_he_10,
    ROUND(AVG(kq.diem_he_4), 2)                      AS diem_tb_he_4,
    ROUND(100.0 * AVG(kq.ket_qua_dat), 2)            AS ty_le_dat_pct
FROM fact_ket_qua_hoc_tap kq
INNER JOIN dim_sinh_vien   sv ON kq.sinh_vien_key = sv.sinh_vien_key
INNER JOIN dim_nganh       ng ON kq.nganh_key     = ng.nganh_key
INNER JOIN fact_tuyen_sinh ts ON ts.sinh_vien_key = sv.sinh_vien_key
GROUP BY ng.ten_nganh

UNION ALL

-- Tổng theo Phương thức (mọi ngành)
SELECT
    'ALL_NGANH'                                      AS ten_nganh,
    pt.ten_phuong_thuc                               AS ten_phuong_thuc,
    COUNT(DISTINCT sv.ma_sv)                         AS so_sinh_vien,
    COUNT(kq.ket_qua_id)                             AS so_luot_hoc_phan,
    ROUND(AVG(kq.diem_tong_ket), 2)                  AS diem_tb_he_10,
    ROUND(AVG(kq.diem_he_4), 2)                      AS diem_tb_he_4,
    ROUND(100.0 * AVG(kq.ket_qua_dat), 2)            AS ty_le_dat_pct
FROM fact_ket_qua_hoc_tap kq
INNER JOIN dim_sinh_vien             sv ON kq.sinh_vien_key = sv.sinh_vien_key
INNER JOIN fact_tuyen_sinh           ts ON ts.sinh_vien_key = sv.sinh_vien_key
INNER JOIN dim_phuong_thuc_xet_tuyen pt ON ts.ptxt_key      = pt.ptxt_key
GROUP BY pt.ten_phuong_thuc

UNION ALL

-- Tổng toàn trường (Grand Total)
SELECT
    'ALL_NGANH'                                      AS ten_nganh,
    'ALL_PHUONG_THUC'                                AS ten_phuong_thuc,
    COUNT(DISTINCT sv.ma_sv)                         AS so_sinh_vien,
    COUNT(kq.ket_qua_id)                             AS so_luot_hoc_phan,
    ROUND(AVG(kq.diem_tong_ket), 2)                  AS diem_tb_he_10,
    ROUND(AVG(kq.diem_he_4), 2)                      AS diem_tb_he_4,
    ROUND(100.0 * AVG(kq.ket_qua_dat), 2)            AS ty_le_dat_pct
FROM fact_ket_qua_hoc_tap kq
INNER JOIN dim_sinh_vien   sv ON kq.sinh_vien_key = sv.sinh_vien_key
INNER JOIN fact_tuyen_sinh ts ON ts.sinh_vien_key = sv.sinh_vien_key;

-- -----------------------------------------------------------------------------
-- 4. View tương quan điểm xét tuyển đầu vào và kết quả học tập học kỳ 1
-- (Phục vụ Câu hỏi phân tích 3 - biểu đồ Scatter)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_olap_tuong_quan_dau_vao_hk1 AS
SELECT
    sv.ma_sv,
    sv.ho_ten,
    sv.nam_nhap_hoc,
    ng.ma_nganh,
    ng.ten_nganh,
    pt.ma_ptxt,
    pt.ten_phuong_thuc,
    ts.diem_xet_tuyen,
    ts.diem_quy_doi_30,
    COUNT(kq.ket_qua_id)                            AS so_mon_hk1,
    ROUND(SUM(kq.diem_tong_ket * kq.so_tin_chi) / SUM(kq.so_tin_chi), 2) AS gpa_hk1_he_10,
    ROUND(SUM(kq.diem_he_4 * kq.so_tin_chi) / SUM(kq.so_tin_chi), 2)     AS gpa_hk1_he_4,
    SUM(1 - kq.ket_qua_dat)                         AS so_mon_rot_hk1
FROM fact_tuyen_sinh ts
INNER JOIN dim_sinh_vien             sv ON ts.sinh_vien_key = sv.sinh_vien_key
INNER JOIN dim_nganh                 ng ON ts.nganh_key     = ng.nganh_key
INNER JOIN dim_phuong_thuc_xet_tuyen pt ON ts.ptxt_key      = pt.ptxt_key
INNER JOIN fact_ket_qua_hoc_tap      kq ON kq.sinh_vien_key = sv.sinh_vien_key
INNER JOIN dim_thoi_gian             tg ON kq.thoi_gian_key = tg.thoi_gian_key
WHERE ts.is_nhap_hoc = 1
  AND tg.hoc_ky = CONCAT(sv.nam_nhap_hoc, '1')
GROUP BY
    sv.ma_sv, sv.ho_ten, sv.nam_nhap_hoc,
    ng.ma_nganh, ng.ten_nganh,
    pt.ma_ptxt, pt.ten_phuong_thuc,
    ts.diem_xet_tuyen, ts.diem_quy_doi_30;

