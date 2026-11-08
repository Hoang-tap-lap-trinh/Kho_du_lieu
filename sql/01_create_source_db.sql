-- =============================================================================
-- 01_create_source_db.sql
-- CSDL nguồn (OLTP) của hệ thống quản lý đào tạo - chuẩn hóa 3NF
-- Tương thích MySQL 8 và MariaDB 10.4+ (XAMPP)
-- CẢNH BÁO: script XÓA và tạo lại database edu_source
-- =============================================================================
DROP DATABASE IF EXISTS edu_source;
CREATE DATABASE edu_source CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE edu_source;

CREATE TABLE Khoa (
    ma_khoa     VARCHAR(10)  NOT NULL,
    ten_khoa    VARCHAR(150) NOT NULL,
    PRIMARY KEY (ma_khoa)
) ENGINE=InnoDB;

CREATE TABLE Nganh (
    ma_nganh    VARCHAR(10)  NOT NULL,
    ten_nganh   VARCHAR(150) NOT NULL,
    ma_khoa     VARCHAR(10)  NOT NULL,
    he_dao_tao  VARCHAR(50)  NOT NULL,
    PRIMARY KEY (ma_nganh),
    CONSTRAINT fk_nganh_khoa FOREIGN KEY (ma_khoa) REFERENCES Khoa (ma_khoa)
) ENGINE=InnoDB;

CREATE TABLE PhuongThucXetTuyen (
    ma_ptxt          VARCHAR(10)  NOT NULL,
    ten_phuong_thuc  VARCHAR(100) NOT NULL,
    thang_diem       DECIMAL(6,1) NOT NULL,
    mo_ta            VARCHAR(255) NULL,
    PRIMARY KEY (ma_ptxt)
) ENGINE=InnoDB;

CREATE TABLE GiangVien (
    ma_gv     VARCHAR(10)  NOT NULL,
    ho_ten    VARCHAR(100) NOT NULL,
    hoc_vi    VARCHAR(50)  NOT NULL,
    ma_khoa   VARCHAR(10)  NOT NULL,
    PRIMARY KEY (ma_gv),
    CONSTRAINT fk_gv_khoa FOREIGN KEY (ma_khoa) REFERENCES Khoa (ma_khoa)
) ENGINE=InnoDB;

CREATE TABLE MonHoc (
    ma_mon      VARCHAR(12)  NOT NULL,
    ten_mon     VARCHAR(150) NOT NULL,
    so_tin_chi  TINYINT      NOT NULL,
    loai_mon    VARCHAR(30)  NOT NULL,
    ma_khoa     VARCHAR(10)  NOT NULL,
    PRIMARY KEY (ma_mon),
    CONSTRAINT fk_mon_khoa FOREIGN KEY (ma_khoa) REFERENCES Khoa (ma_khoa)
) ENGINE=InnoDB;

CREATE TABLE HocKy (
    ma_hoc_ky      VARCHAR(10) NOT NULL,
    nam_hoc        VARCHAR(9)  NOT NULL,
    hoc_ky_so      TINYINT     NOT NULL,
    ngay_bat_dau   DATE        NOT NULL,
    ngay_ket_thuc  DATE        NOT NULL,
    PRIMARY KEY (ma_hoc_ky)
) ENGINE=InnoDB;

CREATE TABLE SinhVien (
    ma_sv          VARCHAR(12)  NOT NULL,
    ho_ten         VARCHAR(100) NOT NULL,
    gioi_tinh      VARCHAR(10)  NULL,
    ngay_sinh      DATE         NULL,
    tinh_thanh     VARCHAR(60)  NULL,
    ma_nganh       VARCHAR(10)  NOT NULL,
    ma_lop         VARCHAR(20)  NOT NULL,
    nam_nhap_hoc   SMALLINT     NOT NULL,
    trang_thai     VARCHAR(20)  NOT NULL,
    ngay_cap_nhat  DATETIME     NOT NULL,
    PRIMARY KEY (ma_sv),
    CONSTRAINT fk_sv_nganh FOREIGN KEY (ma_nganh) REFERENCES Nganh (ma_nganh)
) ENGINE=InnoDB;

-- Nhật ký chuyển ngành/lớp (audit trail của hệ thống nguồn) - đầu vào cho SCD2
CREATE TABLE LichSuChuyenNganh (
    id            INT          NOT NULL AUTO_INCREMENT,
    ma_sv         VARCHAR(12)  NOT NULL,
    ma_nganh_cu   VARCHAR(10)  NOT NULL,
    ma_nganh_moi  VARCHAR(10)  NOT NULL,
    ma_lop_cu     VARCHAR(20)  NOT NULL,
    ma_lop_moi    VARCHAR(20)  NOT NULL,
    ngay_chuyen   DATE         NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_ls_sv       FOREIGN KEY (ma_sv)        REFERENCES SinhVien (ma_sv),
    CONSTRAINT fk_ls_nganh_cu FOREIGN KEY (ma_nganh_cu)  REFERENCES Nganh (ma_nganh),
    CONSTRAINT fk_ls_nganh_moi FOREIGN KEY (ma_nganh_moi) REFERENCES Nganh (ma_nganh)
) ENGINE=InnoDB;

CREATE TABLE LopHocPhan (
    ma_lhp        VARCHAR(25) NOT NULL,
    ma_mon        VARCHAR(12) NOT NULL,
    ma_hoc_ky     VARCHAR(10) NOT NULL,
    ma_gv         VARCHAR(10) NOT NULL,
    si_so_toi_da  SMALLINT    NOT NULL,
    PRIMARY KEY (ma_lhp),
    CONSTRAINT fk_lhp_mon   FOREIGN KEY (ma_mon)    REFERENCES MonHoc (ma_mon),
    CONSTRAINT fk_lhp_hocky FOREIGN KEY (ma_hoc_ky) REFERENCES HocKy (ma_hoc_ky),
    CONSTRAINT fk_lhp_gv    FOREIGN KEY (ma_gv)     REFERENCES GiangVien (ma_gv)
) ENGINE=InnoDB;

-- Bảng kết hợp N-N giữa SinhVien và LopHocPhan, lưu điểm.
-- Không đặt UNIQUE(ma_sv, ma_lhp) để mô phỏng dữ liệu trùng do nhập liệu (minh họa làm sạch).
CREATE TABLE DangKyHocPhan (
    ma_dang_ky      BIGINT       NOT NULL AUTO_INCREMENT,
    ma_sv           VARCHAR(12)  NOT NULL,
    ma_lhp          VARCHAR(25)  NOT NULL,
    ngay_dang_ky    DATE         NOT NULL,
    diem_qua_trinh  DECIMAL(5,2) NULL,
    diem_thi        DECIMAL(5,2) NULL,
    diem_tong_ket   DECIMAL(5,2) NULL,
    PRIMARY KEY (ma_dang_ky),
    KEY idx_dk_sv (ma_sv),
    KEY idx_dk_lhp (ma_lhp),
    CONSTRAINT fk_dk_sv  FOREIGN KEY (ma_sv)  REFERENCES SinhVien (ma_sv),
    CONSTRAINT fk_dk_lhp FOREIGN KEY (ma_lhp) REFERENCES LopHocPhan (ma_lhp)
) ENGINE=InnoDB;

CREATE TABLE HoSoTuyenSinh (
    ma_ho_so        VARCHAR(15)  NOT NULL,
    ho_ten          VARCHAR(100) NOT NULL,
    gioi_tinh       VARCHAR(10)  NULL,
    ngay_sinh       DATE         NULL,
    tinh_thanh      VARCHAR(60)  NULL,
    ma_nganh        VARCHAR(10)  NOT NULL,
    ma_ptxt         VARCHAR(10)  NOT NULL,
    nam_tuyen_sinh  SMALLINT     NOT NULL,
    ngay_nop        DATE         NOT NULL,
    diem_xet_tuyen  DECIMAL(7,2) NULL,
    trang_thai      VARCHAR(30)  NOT NULL,
    da_nhap_hoc     TINYINT      NOT NULL DEFAULT 0,
    ma_sv           VARCHAR(12)  NULL,
    PRIMARY KEY (ma_ho_so),
    KEY idx_hs_sv (ma_sv),
    CONSTRAINT fk_hs_nganh FOREIGN KEY (ma_nganh) REFERENCES Nganh (ma_nganh),
    CONSTRAINT fk_hs_ptxt  FOREIGN KEY (ma_ptxt)  REFERENCES PhuongThucXetTuyen (ma_ptxt),
    CONSTRAINT fk_hs_sv    FOREIGN KEY (ma_sv)    REFERENCES SinhVien (ma_sv)
) ENGINE=InnoDB;

