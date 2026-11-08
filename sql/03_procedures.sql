-- =============================================================================
-- 03_procedures.sql
-- Stored procedures xử lý Slowly Changing Dimension loại 2 (SCD2) cho
-- dim_sinh_vien và nạp 2 bảng fact với tra cứu khóa thay thế (surrogate key)
-- Tương thích cả MySQL 8 và MariaDB 10.4+ (XAMPP)
-- =============================================================================
USE edu_dw;

DROP PROCEDURE IF EXISTS sp_scd2_dim_sinh_vien;
DROP PROCEDURE IF EXISTS sp_load_fact_ket_qua_hoc_tap;
DROP PROCEDURE IF EXISTS sp_load_fact_tuyen_sinh;

DELIMITER $$

-- -----------------------------------------------------------------------------
-- 1. Stored Procedure SCD2 cho dim_sinh_vien
-- Nguồn đầu vào: bảng stg_sinh_vien_version (đã được bước Transform chuẩn bị,
-- mỗi dòng là 1 phiên bản (ma_sv, ngay_hieu_luc) theo thứ tự thời gian).
-- Quy tắc:
--   - Nếu phiên bản (ma_sv, ngay_hieu_luc) chưa tồn tại và sinh viên đã có bản ghi
--     hiện hành (is_current = 1) nhưng khác ngành hoặc lớp (ma_nganh, ma_lop) ->
--     đóng bản ghi cũ (ngay_het_han = DATE_SUB(ngay_hieu_luc_moi, INTERVAL 1 DAY),
--     is_current = 0), sau đó chèn bản ghi mới với is_current = 1.
--   - Nếu sinh viên chưa có trong dim_sinh_vien -> chèn bản ghi đầu tiên.
--   - Nếu chỉ thay đổi thuộc tính SCD1 (ho_ten, gioi_tinh, tinh_thanh, trang_thai...)
--     trên cùng phiên bản -> cập nhật tại chỗ, không nhân đôi dòng.
--   - Tính lại ngay_het_han và is_current giữa các phiên bản của cùng ma_sv để
--     đảm bảo chạy lặp (idempotent) không tạo bản ghi trùng.
-- -----------------------------------------------------------------------------
CREATE PROCEDURE sp_scd2_dim_sinh_vien()
BEGIN
    DECLARE v_inserted INT DEFAULT 0;
    DECLARE v_updated  INT DEFAULT 0;
    DECLARE v_closed   INT DEFAULT 0;

    -- B1: Đóng các bản ghi hiện hành khi có phiên bản mới hơn khác ngành/lớp
    UPDATE dim_sinh_vien d
    INNER JOIN stg_sinh_vien_version s
        ON d.ma_sv = s.ma_sv
       AND s.ngay_hieu_luc > d.ngay_hieu_luc
    SET d.ngay_het_han = DATE_SUB(s.ngay_hieu_luc, INTERVAL 1 DAY),
        d.is_current   = 0
    WHERE d.is_current = 1
      AND d.sinh_vien_key > 0
      AND (IFNULL(d.ma_nganh, '') <> IFNULL(s.ma_nganh, '')
           OR IFNULL(d.ma_lop, '') <> IFNULL(s.ma_lop, ''));

    SET v_closed = ROW_COUNT();

    -- B2: Cập nhật thuộc tính SCD1 cho các phiên bản đã tồn tại cùng (ma_sv, ngay_hieu_luc)
    UPDATE dim_sinh_vien d
    INNER JOIN stg_sinh_vien_version s
        ON d.ma_sv = s.ma_sv
       AND d.ngay_hieu_luc = s.ngay_hieu_luc
    SET d.ho_ten       = s.ho_ten,
        d.gioi_tinh    = s.gioi_tinh,
        d.nam_sinh     = s.nam_sinh,
        d.tinh_thanh   = s.tinh_thanh,
        d.vung_mien    = s.vung_mien,
        d.nam_nhap_hoc = s.nam_nhap_hoc,
        d.trang_thai   = s.trang_thai,
        d.ma_nganh     = s.ma_nganh,
        d.ten_nganh    = s.ten_nganh,
        d.ma_khoa      = s.ma_khoa,
        d.ten_khoa     = s.ten_khoa,
        d.ma_lop       = s.ma_lop
    WHERE d.sinh_vien_key > 0;

    SET v_updated = ROW_COUNT();

    -- B3: Chèn các phiên bản mới chưa có trong dim_sinh_vien
    INSERT INTO dim_sinh_vien (
        ma_sv, ho_ten, gioi_tinh, nam_sinh, tinh_thanh, vung_mien,
        nam_nhap_hoc, trang_thai, ma_nganh, ten_nganh, ma_khoa, ten_khoa,
        ma_lop, ngay_hieu_luc, ngay_het_han, is_current
    )
    SELECT
        s.ma_sv, s.ho_ten, s.gioi_tinh, s.nam_sinh, s.tinh_thanh, s.vung_mien,
        s.nam_nhap_hoc, s.trang_thai, s.ma_nganh, s.ten_nganh, s.ma_khoa, s.ten_khoa,
        s.ma_lop, s.ngay_hieu_luc, '9999-12-31', 1
    FROM stg_sinh_vien_version s
    LEFT JOIN dim_sinh_vien d
        ON d.ma_sv = s.ma_sv
       AND d.ngay_hieu_luc = s.ngay_hieu_luc
    WHERE d.sinh_vien_key IS NULL
    ORDER BY s.ma_sv, s.ngay_hieu_luc;

    SET v_inserted = ROW_COUNT();

    -- B4: Đồng bộ lại chuỗi ngay_het_han và is_current cho mọi sinh viên có >= 2 phiên bản
    UPDATE dim_sinh_vien d
    LEFT JOIN (
        SELECT
            d1.sinh_vien_key,
            MIN(d2.ngay_hieu_luc) AS next_hieu_luc
        FROM dim_sinh_vien d1
        LEFT JOIN dim_sinh_vien d2
            ON d1.ma_sv = d2.ma_sv
           AND d2.ngay_hieu_luc > d1.ngay_hieu_luc
        WHERE d1.sinh_vien_key > 0
        GROUP BY d1.sinh_vien_key
    ) nxt ON d.sinh_vien_key = nxt.sinh_vien_key
    SET d.ngay_het_han = IF(nxt.next_hieu_luc IS NULL, '9999-12-31', DATE_SUB(nxt.next_hieu_luc, INTERVAL 1 DAY)),
        d.is_current   = IF(nxt.next_hieu_luc IS NULL, 1, 0)
    WHERE d.sinh_vien_key > 0;

    SELECT v_inserted AS so_dong_them_moi,
           v_updated  AS so_dong_cap_nhat,
           v_closed   AS so_dong_dong_lich_su;
END$$

-- -----------------------------------------------------------------------------
-- 2. Stored Procedure nạp fact_ket_qua_hoc_tap
-- Tra cứu sinh_vien_key theo khoảng hiệu lực SCD2:
--   ngay_tham_chieu BETWEEN d.ngay_hieu_luc AND d.ngay_het_han
-- Và lấy nganh_key từ đúng phiên bản lịch sử của sinh viên tại thời điểm học!
-- -----------------------------------------------------------------------------
CREATE PROCEDURE sp_load_fact_ket_qua_hoc_tap()
BEGIN
    INSERT INTO fact_ket_qua_hoc_tap (
        ma_dang_ky, ma_lhp, sinh_vien_key, mon_hoc_key, giang_vien_key,
        nganh_key, thoi_gian_key, diem_qua_trinh, diem_thi, diem_tong_ket,
        diem_chu, diem_he_4, ket_qua_dat, so_tin_chi
    )
    SELECT
        s.ma_dang_ky,
        s.ma_lhp,
        sv.sinh_vien_key,
        mh.mon_hoc_key,
        gv.giang_vien_key,
        ng.nganh_key,
        s.thoi_gian_key,
        s.diem_qua_trinh,
        s.diem_thi,
        s.diem_tong_ket,
        s.diem_chu,
        s.diem_he_4,
        s.ket_qua_dat,
        s.so_tin_chi
    FROM stg_fact_ket_qua_hoc_tap s
    INNER JOIN dim_sinh_vien sv
        ON sv.ma_sv = s.ma_sv
       AND s.ngay_tham_chieu BETWEEN sv.ngay_hieu_luc AND sv.ngay_het_han
    INNER JOIN dim_mon_hoc mh
        ON mh.ma_mon = s.ma_mon
    INNER JOIN dim_giang_vien gv
        ON gv.ma_gv = s.ma_gv
    INNER JOIN dim_nganh ng
        ON ng.ma_nganh = sv.ma_nganh
    ON DUPLICATE KEY UPDATE
        sinh_vien_key  = VALUES(sinh_vien_key),
        mon_hoc_key    = VALUES(mon_hoc_key),
        giang_vien_key = VALUES(giang_vien_key),
        nganh_key      = VALUES(nganh_key),
        thoi_gian_key  = VALUES(thoi_gian_key),
        diem_qua_trinh = VALUES(diem_qua_trinh),
        diem_thi       = VALUES(diem_thi),
        diem_tong_ket  = VALUES(diem_tong_ket),
        diem_chu       = VALUES(diem_chu),
        diem_he_4      = VALUES(diem_he_4),
        ket_qua_dat    = VALUES(ket_qua_dat),
        so_tin_chi     = VALUES(so_tin_chi);

    SELECT COUNT(*) AS tong_dong_fact_ket_qua FROM fact_ket_qua_hoc_tap;
END$$

-- -----------------------------------------------------------------------------
-- 3. Stored Procedure nạp fact_tuyen_sinh
-- Hồ sơ đã nhập học được gắn với phiên bản đầu tiên của sinh viên trong dim_sinh_vien;
-- hồ sơ chưa nhập học gắn sinh_vien_key = -1 (Unknown member).
-- -----------------------------------------------------------------------------
CREATE PROCEDURE sp_load_fact_tuyen_sinh()
BEGIN
    INSERT INTO fact_tuyen_sinh (
        ma_ho_so, nganh_key, ptxt_key, thoi_gian_key, sinh_vien_key,
        gioi_tinh, tinh_thanh, diem_xet_tuyen, diem_quy_doi_30,
        is_trung_tuyen, is_nhap_hoc, so_luong_ho_so
    )
    SELECT
        s.ma_ho_so,
        ng.nganh_key,
        pt.ptxt_key,
        s.thoi_gian_key,
        IFNULL(sv_first.sinh_vien_key, -1) AS sinh_vien_key,
        s.gioi_tinh,
        s.tinh_thanh,
        s.diem_xet_tuyen,
        s.diem_quy_doi_30,
        s.is_trung_tuyen,
        s.is_nhap_hoc,
        1
    FROM stg_fact_tuyen_sinh s
    INNER JOIN dim_nganh ng
        ON ng.ma_nganh = s.ma_nganh
    INNER JOIN dim_phuong_thuc_xet_tuyen pt
        ON pt.ma_ptxt = s.ma_ptxt
    LEFT JOIN (
        SELECT d1.ma_sv, MIN(d1.sinh_vien_key) AS sinh_vien_key
        FROM dim_sinh_vien d1
        WHERE d1.sinh_vien_key > 0
        GROUP BY d1.ma_sv
    ) sv_first
        ON sv_first.ma_sv = s.ma_sv
    ON DUPLICATE KEY UPDATE
        nganh_key       = VALUES(nganh_key),
        ptxt_key        = VALUES(ptxt_key),
        thoi_gian_key   = VALUES(thoi_gian_key),
        sinh_vien_key   = VALUES(sinh_vien_key),
        gioi_tinh       = VALUES(gioi_tinh),
        tinh_thanh      = VALUES(tinh_thanh),
        diem_xet_tuyen  = VALUES(diem_xet_tuyen),
        diem_quy_doi_30 = VALUES(diem_quy_doi_30),
        is_trung_tuyen  = VALUES(is_trung_tuyen),
        is_nhap_hoc     = VALUES(is_nhap_hoc);

    SELECT COUNT(*) AS tong_dong_fact_tuyen_sinh FROM fact_tuyen_sinh;
END$$

DELIMITER ;

