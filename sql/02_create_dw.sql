-- =============================================================================
-- 02_create_dw.sql
-- Kho dữ liệu giáo dục (star schema, 2 fact dùng chung dimension) + staging + log
-- Tương thích MySQL 8 và MariaDB 10.4+ (XAMPP)
-- CẢNH BÁO: script XÓA và tạo lại database edu_dw
-- =============================================================================
DROP DATABASE IF EXISTS edu_dw;
CREATE DATABASE edu_dw CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE edu_dw;

-- -----------------------------------------------------------------------------
-- DIMENSION
-- -----------------------------------------------------------------------------
CREATE TABLE dim_thoi_gian (
    thoi_gian_key     INT          NOT NULL,
    ngay              DATE         NOT NULL,
    ngay_trong_thang  TINYINT      NOT NULL,
    thang             TINYINT      NOT NULL,
    quy               TINYINT      NOT NULL,
    nam               SMALLINT     NOT NULL,
    hoc_ky            VARCHAR(10)  NOT NULL,
    hoc_ky_so         TINYINT      NOT NULL,
    nam_hoc           VARCHAR(9)   NOT NULL,
    ten_hoc_ky        VARCHAR(25)  NOT NULL,
    la_cuoi_tuan      TINYINT      NOT NULL,
    PRIMARY KEY (thoi_gian_key),
    UNIQUE KEY uq_ngay (ngay),
    KEY idx_tg_namhoc (nam_hoc, hoc_ky_so)
) ENGINE=InnoDB;

CREATE TABLE dim_nganh (
    nganh_key   INT          NOT NULL AUTO_INCREMENT,
    ma_nganh    VARCHAR(10)  NOT NULL,
    ten_nganh   VARCHAR(150) NOT NULL,
    ma_khoa     VARCHAR(10)  NOT NULL,
    ten_khoa    VARCHAR(150) NOT NULL,
    he_dao_tao  VARCHAR(50)  NOT NULL,
    PRIMARY KEY (nganh_key),
    UNIQUE KEY uq_ma_nganh (ma_nganh)
) ENGINE=InnoDB;

CREATE TABLE dim_mon_hoc (
    mon_hoc_key  INT          NOT NULL AUTO_INCREMENT,
    ma_mon       VARCHAR(12)  NOT NULL,
    ten_mon      VARCHAR(150) NOT NULL,
    so_tin_chi   TINYINT      NOT NULL,
    loai_mon     VARCHAR(30)  NOT NULL,
    ma_khoa      VARCHAR(10)  NOT NULL,
    ten_khoa     VARCHAR(150) NOT NULL,
    PRIMARY KEY (mon_hoc_key),
    UNIQUE KEY uq_ma_mon (ma_mon)
) ENGINE=InnoDB;

CREATE TABLE dim_giang_vien (
    giang_vien_key  INT          NOT NULL AUTO_INCREMENT,
    ma_gv           VARCHAR(10)  NOT NULL,
    ho_ten          VARCHAR(100) NOT NULL,
    hoc_vi          VARCHAR(50)  NOT NULL,
    ma_khoa         VARCHAR(10)  NOT NULL,
    ten_khoa        VARCHAR(150) NOT NULL,
    PRIMARY KEY (giang_vien_key),
    UNIQUE KEY uq_ma_gv (ma_gv)
) ENGINE=InnoDB;

CREATE TABLE dim_phuong_thuc_xet_tuyen (
    ptxt_key         INT          NOT NULL AUTO_INCREMENT,
    ma_ptxt          VARCHAR(10)  NOT NULL,
    ten_phuong_thuc  VARCHAR(100) NOT NULL,
    thang_diem       DECIMAL(6,1) NOT NULL,
    mo_ta            VARCHAR(255) NULL,
    PRIMARY KEY (ptxt_key),
    UNIQUE KEY uq_ma_ptxt (ma_ptxt)
) ENGINE=InnoDB;

-- SCD loại 2 trên (ma_nganh, ma_lop); các thuộc tính còn lại xử lý SCD loại 1 (ghi đè)
CREATE TABLE dim_sinh_vien (
    sinh_vien_key  INT          NOT NULL AUTO_INCREMENT,
    ma_sv          VARCHAR(12)  NOT NULL,
    ho_ten         VARCHAR(100) NULL,
    gioi_tinh      VARCHAR(10)  NULL,
    nam_sinh       SMALLINT     NULL,
    tinh_thanh     VARCHAR(60)  NULL,
    vung_mien      VARCHAR(60)  NULL,
    nam_nhap_hoc   SMALLINT     NULL,
    trang_thai     VARCHAR(20)  NULL,
    ma_nganh       VARCHAR(10)  NULL,
    ten_nganh      VARCHAR(150) NULL,
    ma_khoa        VARCHAR(10)  NULL,
    ten_khoa       VARCHAR(150) NULL,
    ma_lop         VARCHAR(20)  NULL,
    ngay_hieu_luc  DATE         NOT NULL,
    ngay_het_han   DATE         NOT NULL DEFAULT '9999-12-31',
    is_current     TINYINT      NOT NULL DEFAULT 1,
    PRIMARY KEY (sinh_vien_key),
    UNIQUE KEY uq_sv_phien_ban (ma_sv, ngay_hieu_luc),
    KEY idx_sv_current (ma_sv, is_current),
    KEY idx_sv_tinh (tinh_thanh)
) ENGINE=InnoDB;

-- Thành viên "không xác định" (unknown member) cho hồ sơ chưa nhập học
INSERT INTO dim_sinh_vien (sinh_vien_key, ma_sv, ho_ten, ngay_hieu_luc, ngay_het_han, is_current)
VALUES (-1, 'N/A', 'Không xác định', '1900-01-01', '9999-12-31', 1);

-- -----------------------------------------------------------------------------
-- FACT
-- -----------------------------------------------------------------------------
-- Grain: một sinh viên trong một lớp học phần
CREATE TABLE fact_ket_qua_hoc_tap (
    ket_qua_id      BIGINT       NOT NULL AUTO_INCREMENT,
    ma_dang_ky      BIGINT       NOT NULL,
    ma_lhp          VARCHAR(25)  NOT NULL,
    sinh_vien_key   INT          NOT NULL,
    mon_hoc_key     INT          NOT NULL,
    giang_vien_key  INT          NOT NULL,
    nganh_key       INT          NOT NULL,
    thoi_gian_key   INT          NOT NULL,
    diem_qua_trinh  DECIMAL(4,2) NOT NULL,
    diem_thi        DECIMAL(4,2) NOT NULL,
    diem_tong_ket   DECIMAL(4,2) NOT NULL,
    diem_chu        VARCHAR(2)   NOT NULL,
    diem_he_4       DECIMAL(3,1) NOT NULL,
    ket_qua_dat     TINYINT      NOT NULL,
    so_tin_chi      TINYINT      NOT NULL,
    PRIMARY KEY (ket_qua_id),
    UNIQUE KEY uq_kq_dang_ky (ma_dang_ky),
    KEY idx_kq_sv (sinh_vien_key, diem_tong_ket, ket_qua_dat),
    KEY idx_kq_mon (mon_hoc_key, thoi_gian_key, diem_tong_ket, ket_qua_dat),
    KEY idx_kq_gv (giang_vien_key, diem_tong_ket, ket_qua_dat),
    KEY idx_kq_nganh (nganh_key, sinh_vien_key, diem_tong_ket, ket_qua_dat),
    KEY idx_kq_tg (thoi_gian_key, mon_hoc_key, diem_tong_ket, ket_qua_dat),
    CONSTRAINT fk_kq_sv    FOREIGN KEY (sinh_vien_key)  REFERENCES dim_sinh_vien (sinh_vien_key),
    CONSTRAINT fk_kq_mon   FOREIGN KEY (mon_hoc_key)    REFERENCES dim_mon_hoc (mon_hoc_key),
    CONSTRAINT fk_kq_gv    FOREIGN KEY (giang_vien_key) REFERENCES dim_giang_vien (giang_vien_key),
    CONSTRAINT fk_kq_nganh FOREIGN KEY (nganh_key)      REFERENCES dim_nganh (nganh_key),
    CONSTRAINT fk_kq_tg    FOREIGN KEY (thoi_gian_key)  REFERENCES dim_thoi_gian (thoi_gian_key)
) ENGINE=InnoDB;

-- Grain: một hồ sơ tuyển sinh
CREATE TABLE fact_tuyen_sinh (
    tuyen_sinh_id    BIGINT       NOT NULL AUTO_INCREMENT,
    ma_ho_so         VARCHAR(15)  NOT NULL,
    nganh_key        INT          NOT NULL,
    ptxt_key         INT          NOT NULL,
    thoi_gian_key    INT          NOT NULL,
    sinh_vien_key    INT          NOT NULL DEFAULT -1,
    gioi_tinh        VARCHAR(10)  NULL,
    tinh_thanh       VARCHAR(60)  NULL,
    diem_xet_tuyen   DECIMAL(7,2) NOT NULL,
    diem_quy_doi_30  DECIMAL(5,2) NOT NULL,
    is_trung_tuyen   TINYINT      NOT NULL,
    is_nhap_hoc      TINYINT      NOT NULL,
    so_luong_ho_so   TINYINT      NOT NULL DEFAULT 1,
    PRIMARY KEY (tuyen_sinh_id),
    UNIQUE KEY uq_ts_ho_so (ma_ho_so),
    KEY idx_ts_nganh (nganh_key),
    KEY idx_ts_ptxt (ptxt_key),
    KEY idx_ts_tg (thoi_gian_key),
    KEY idx_ts_sv (sinh_vien_key),
    CONSTRAINT fk_ts_nganh FOREIGN KEY (nganh_key)     REFERENCES dim_nganh (nganh_key),
    CONSTRAINT fk_ts_ptxt  FOREIGN KEY (ptxt_key)      REFERENCES dim_phuong_thuc_xet_tuyen (ptxt_key),
    CONSTRAINT fk_ts_tg    FOREIGN KEY (thoi_gian_key) REFERENCES dim_thoi_gian (thoi_gian_key),
    CONSTRAINT fk_ts_sv    FOREIGN KEY (sinh_vien_key) REFERENCES dim_sinh_vien (sinh_vien_key)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- STAGING (dữ liệu đã làm sạch, trước khi tra khóa thay thế)
-- Các bảng stg_raw_* (bản sao thô từ nguồn) do ETL tự tạo khi Extract.
-- -----------------------------------------------------------------------------
CREATE TABLE stg_sinh_vien_version (
    ma_sv          VARCHAR(12)  NOT NULL,
    ho_ten         VARCHAR(100) NULL,
    gioi_tinh      VARCHAR(10)  NULL,
    nam_sinh       SMALLINT     NULL,
    tinh_thanh     VARCHAR(60)  NULL,
    vung_mien      VARCHAR(60)  NULL,
    nam_nhap_hoc   SMALLINT     NULL,
    trang_thai     VARCHAR(20)  NULL,
    ma_nganh       VARCHAR(10)  NULL,
    ten_nganh      VARCHAR(150) NULL,
    ma_khoa        VARCHAR(10)  NULL,
    ten_khoa       VARCHAR(150) NULL,
    ma_lop         VARCHAR(20)  NULL,
    ngay_hieu_luc  DATE         NOT NULL,
    PRIMARY KEY (ma_sv, ngay_hieu_luc)
) ENGINE=InnoDB;

CREATE TABLE stg_fact_ket_qua_hoc_tap (
    ma_dang_ky       BIGINT       NOT NULL,
    ma_sv            VARCHAR(12)  NOT NULL,
    ma_lhp           VARCHAR(25)  NOT NULL,
    ma_mon           VARCHAR(12)  NOT NULL,
    ma_gv            VARCHAR(10)  NOT NULL,
    ngay_tham_chieu  DATE         NOT NULL,
    thoi_gian_key    INT          NOT NULL,
    diem_qua_trinh   DECIMAL(4,2) NOT NULL,
    diem_thi         DECIMAL(4,2) NOT NULL,
    diem_tong_ket    DECIMAL(4,2) NOT NULL,
    diem_chu         VARCHAR(2)   NOT NULL,
    diem_he_4        DECIMAL(3,1) NOT NULL,
    ket_qua_dat      TINYINT      NOT NULL,
    so_tin_chi       TINYINT      NOT NULL,
    PRIMARY KEY (ma_dang_ky)
) ENGINE=InnoDB;

CREATE TABLE stg_fact_tuyen_sinh (
    ma_ho_so         VARCHAR(15)  NOT NULL,
    ma_nganh         VARCHAR(10)  NOT NULL,
    ma_ptxt          VARCHAR(10)  NOT NULL,
    ma_sv            VARCHAR(12)  NULL,
    ngay_nop         DATE         NOT NULL,
    thoi_gian_key    INT          NOT NULL,
    gioi_tinh        VARCHAR(10)  NULL,
    tinh_thanh       VARCHAR(60)  NULL,
    diem_xet_tuyen   DECIMAL(7,2) NOT NULL,
    diem_quy_doi_30  DECIMAL(5,2) NOT NULL,
    is_trung_tuyen   TINYINT      NOT NULL,
    is_nhap_hoc      TINYINT      NOT NULL,
    PRIMARY KEY (ma_ho_so)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- LOG & KIỂM SOÁT CHẤT LƯỢNG ETL
-- -----------------------------------------------------------------------------
CREATE TABLE etl_log (
    log_id        BIGINT       NOT NULL AUTO_INCREMENT,
    run_id        VARCHAR(36)  NOT NULL,
    buoc          VARCHAR(20)  NOT NULL,
    bang          VARCHAR(64)  NOT NULL,
    so_dong_doc   INT          NULL,
    so_dong_nap   INT          NULL,
    so_dong_loai  INT          NULL,
    ghi_chu       VARCHAR(500) NULL,
    bat_dau       DATETIME     NOT NULL,
    ket_thuc      DATETIME     NOT NULL,
    PRIMARY KEY (log_id),
    KEY idx_log_run (run_id)
) ENGINE=InnoDB;

CREATE TABLE etl_reject (
    reject_id   BIGINT       NOT NULL AUTO_INCREMENT,
    run_id      VARCHAR(36)  NOT NULL,
    bang        VARCHAR(64)  NOT NULL,
    khoa_nguon  VARCHAR(100) NOT NULL,
    ma_loi      VARCHAR(30)  NOT NULL,
    mo_ta       VARCHAR(500) NULL,
    PRIMARY KEY (reject_id),
    KEY idx_reject_run (run_id, bang, ma_loi)
) ENGINE=InnoDB;

-- So sánh dữ liệu trước và sau khi làm sạch
CREATE TABLE etl_data_quality (
    dq_id          BIGINT       NOT NULL AUTO_INCREMENT,
    run_id         VARCHAR(36)  NOT NULL,
    bang           VARCHAR(64)  NOT NULL,
    loai_kiem_tra  VARCHAR(100) NOT NULL,
    so_dong_truoc  INT          NOT NULL,
    so_dong_sau    INT          NOT NULL,
    cach_xu_ly     VARCHAR(255) NULL,
    PRIMARY KEY (dq_id),
    KEY idx_dq_run (run_id)
) ENGINE=InnoDB;

