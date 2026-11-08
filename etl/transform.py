"""Bước 2 của ETL: Transform - làm sạch, chuẩn hóa, quy đổi điểm và chuẩn bị dữ liệu SCD2."""
from __future__ import annotations

from datetime import date, datetime
import numpy as np
import pandas as pd
from sqlalchemy.engine import Engine

from common import reference as ref
from common.grading import DIEM_DAT, quy_doi_diem, tinh_diem_tong_ket
from etl.extract import ghi_log

TEN_NGANH_CHUAN = {ma: ten for ma, ten, *_ in ref.NGANH}


def chuan_hoa_chuoi_ten(series: pd.Series) -> pd.Series:
    """Xóa khoảng trắng thừa và viết hoa chữ cái đầu mỗi từ."""
    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )


def chuan_hoa_gioi_tinh(series: pd.Series) -> tuple[pd.Series, int]:
    """Chuẩn hóa giới tính về 'Nam' hoặc 'Nữ'. Trả về (series đã chuẩn hóa, số dòng được sửa)."""
    goc = series.fillna("").astype(str)
    s = goc.str.strip().str.lower()
    chuan = np.where(
        s.isin(["nam", "m", "male"]),
        "Nam",
        np.where(s.isin(["nữ", "nu", "f", "female"]), "Nữ", "Khác"),
    )
    chuan_s = pd.Series(chuan, index=series.index)
    so_sua = int((goc != chuan_s).sum())
    return chuan_s, so_sua


def chuan_hoa_tinh_thanh(series: pd.Series) -> tuple[pd.Series, int]:
    """Chuẩn hóa tên tỉnh/thành về danh mục 18 tỉnh/thành chuẩn."""
    goc = series.fillna("").astype(str)
    chuan = [ref.TINH_THANH_LOOKUP.get(ref.khoa_so_khop(x), x.strip().title()) for x in goc]
    chuan_s = pd.Series(chuan, index=series.index)
    so_sua = int((goc != chuan_s).sum())
    return chuan_s, so_sua


def chuan_hoa_trang_thai_hs(series: pd.Series) -> tuple[pd.Series, int]:
    goc = series.fillna("").astype(str)
    khoa = [ref.khoa_so_khop(x) for x in goc]
    chuan = [
        "Không trúng tuyển" if "khong" in k else ("Trúng tuyển" if "trung" in k else g.strip())
        for g, k in zip(goc, khoa)
    ]
    chuan_s = pd.Series(chuan, index=series.index)
    so_sua = int((goc != chuan_s).sum())
    return chuan_s, so_sua


def tao_dim_thoi_gian(hoc_ky_df: pd.DataFrame, nam_bat_dau: int = 2019, nam_ket_thuc: int = 2027) -> pd.DataFrame:
    """Sinh bảng chiều thời gian theo từng ngày từ nam_bat_dau đến nam_ket_thuc."""
    hk = hoc_ky_df.copy()
    hk["ngay_bat_dau"] = pd.to_datetime(hk["ngay_bat_dau"]).dt.date
    hk["ngay_ket_thuc"] = pd.to_datetime(hk["ngay_ket_thuc"]).dt.date

    dates = pd.date_range(date(nam_bat_dau, 1, 1), date(nam_ket_thuc, 12, 31), freq="D")
    rows = []
    for ts in dates:
        d = ts.date()
        y, m, day = d.year, d.month, d.day
        quy = (m - 1) // 3 + 1
        # Xác định học kỳ theo tháng (HK1: tháng 8-1, HK2: tháng 2-7)
        if m >= 8:
            nam_hoc = f"{y}-{y + 1}"
            hk_so = 1
            ma_hk = f"{y}1"
        elif m == 1:
            nam_hoc = f"{y - 1}-{y}"
            hk_so = 1
            ma_hk = f"{y - 1}1"
        else:
            nam_hoc = f"{y - 1}-{y}"
            hk_so = 2
            ma_hk = f"{y - 1}2"
        rows.append({
            "thoi_gian_key": y * 10000 + m * 100 + day,
            "ngay": d,
            "ngay_trong_thang": day,
            "thang": m,
            "quy": quy,
            "nam": y,
            "hoc_ky": ma_hk,
            "hoc_ky_so": hk_so,
            "nam_hoc": nam_hoc,
            "ten_hoc_ky": f"Học kỳ {hk_so} ({nam_hoc})",
            "la_cuoi_tuan": 1 if ts.weekday() >= 5 else 0,
        })
    return pd.DataFrame(rows)


def xay_dung_phien_ban_scd2(
    sv_clean: pd.DataFrame,
    lich_su_df: pd.DataFrame,
    dim_nganh: pd.DataFrame,
) -> pd.DataFrame:
    """Tạo các phiên bản lịch sử (ma_sv, ngay_hieu_luc) cho dim_sinh_vien (SCD2).

    Kết hợp bảng SinhVien và bảng LichSuChuyenNganh để tái dựng toàn bộ chuỗi
    ngành/lớp của từng sinh viên theo thời gian.
    """
    nganh_info = dim_nganh.set_index("ma_nganh")[["ten_nganh", "ma_khoa", "ten_khoa"]].to_dict("index")
    ls = lich_su_df.copy()
    if len(ls) > 0:
        ls["ngay_chuyen"] = pd.to_datetime(ls["ngay_chuyen"]).dt.date
        sort_cols = ["ma_sv", "ngay_chuyen"] + (["id"] if "id" in ls.columns else [])
        ls = ls.sort_values(sort_cols)
    ls_by_sv = {}
    for row in ls.itertuples(index=False):
        ls_by_sv.setdefault(row.ma_sv, []).append(row)

    versions = []
    for sv in sv_clean.itertuples(index=False):
        ngay_nhap_hoc = date(int(sv.nam_nhap_hoc), 9, 1)
        changes = ls_by_sv.get(sv.ma_sv, [])
        if not changes:
            chain = [(ngay_nhap_hoc, sv.ma_nganh, sv.ma_lop)]
        else:
            # Phiên bản gốc lúc nhập học lấy từ ma_nganh_cu, ma_lop_cu của lần chuyển đầu tiên
            chain = [(ngay_nhap_hoc, changes[0].ma_nganh_cu, changes[0].ma_lop_cu)]
            for ch in changes:
                chain.append((ch.ngay_chuyen, ch.ma_nganh_moi, ch.ma_lop_moi))
            # Nếu bảng SinhVien hiện tại lại được đổi trực tiếp mà chưa ghi vào LichSuChuyenNganh
            last_dt, last_nganh, last_lop = chain[-1]
            if (sv.ma_nganh != last_nganh) or (sv.ma_lop != last_lop):
                ngay_cn = pd.to_datetime(sv.ngay_cap_nhat).date()
                if ngay_cn <= last_dt:
                    ngay_cn = date.today()
                chain.append((ngay_cn, sv.ma_nganh, sv.ma_lop))

        for ngay_hl, ma_ng, ma_lop in chain:
            info = nganh_info.get(ma_ng, {"ten_nganh": ma_ng, "ma_khoa": "N/A", "ten_khoa": "N/A"})
            versions.append({
                "ma_sv": sv.ma_sv,
                "ho_ten": sv.ho_ten,
                "gioi_tinh": sv.gioi_tinh,
                "nam_sinh": int(sv.nam_sinh),
                "tinh_thanh": sv.tinh_thanh,
                "vung_mien": sv.vung_mien,
                "nam_nhap_hoc": int(sv.nam_nhap_hoc),
                "trang_thai": sv.trang_thai,
                "ma_nganh": ma_ng,
                "ten_nganh": info["ten_nganh"],
                "ma_khoa": info["ma_khoa"],
                "ten_khoa": info["ten_khoa"],
                "ma_lop": ma_lop,
                "ngay_hieu_luc": ngay_hl,
            })

    df_ver = pd.DataFrame(versions)
    df_ver = df_ver.drop_duplicates(subset=["ma_sv", "ngay_hieu_luc"], keep="last")
    return df_ver.sort_values(["ma_sv", "ngay_hieu_luc"]).reset_index(drop=True)


def transform_all(raw: dict[str, pd.DataFrame], dw_engine: Engine, run_id: str) -> dict[str, pd.DataFrame]:
    """Thực hiện toàn bộ bước Transform, ghi bảng chất lượng dữ liệu và danh sách bản ghi lỗi."""
    dq_rows: list[dict] = []
    reject_rows: list[dict] = []

    # 1. Khoa & Ngành (chuẩn hóa tên ngành bị sai định dạng ở nguồn)
    t0 = datetime.now()
    khoa = raw["Khoa"].copy()
    khoa["ma_khoa"] = khoa["ma_khoa"].str.strip().str.upper()
    khoa["ten_khoa"] = khoa["ten_khoa"].str.strip()

    nganh = raw["Nganh"].copy()
    nganh["ma_nganh"] = nganh["ma_nganh"].str.strip().str.upper()
    nganh["ma_khoa"] = nganh["ma_khoa"].str.strip().str.upper()
    ten_goc = nganh["ten_nganh"].astype(str)
    nganh["ten_nganh"] = [
        TEN_NGANH_CHUAN.get(m, " ".join(t.strip().split()))
        for m, t in zip(nganh["ma_nganh"], ten_goc)
    ]
    so_nganh_sua = int((ten_goc != nganh["ten_nganh"]).sum())
    dq_rows.append({
        "run_id": run_id,
        "bang": "Nganh",
        "loai_kiem_tra": "Tên ngành sai chuẩn chữ hoa/khoảng trắng",
        "so_dong_truoc": so_nganh_sua,
        "so_dong_sau": 0,
        "cach_xu_ly": "Chuẩn hóa về danh mục tên ngành thống nhất",
    })
    dim_nganh = nganh.merge(khoa, on="ma_khoa", how="left")[
        ["ma_nganh", "ten_nganh", "ma_khoa", "ten_khoa", "he_dao_tao"]
    ]
    ghi_log(dw_engine, run_id, "TRANSFORM", "dim_nganh", len(nganh), len(dim_nganh), 0, t0,
            f"Đã chuẩn hóa {so_nganh_sua} tên ngành")

    # 2. Môn học & Giảng viên & Phương thức xét tuyển & Thời gian
    t0 = datetime.now()
    mon = raw["MonHoc"].copy()
    mon["ma_mon"] = mon["ma_mon"].str.strip().str.upper()
    mon["ma_khoa"] = mon["ma_khoa"].str.strip().str.upper()
    dim_mon_hoc = mon.merge(khoa, on="ma_khoa", how="left")[
        ["ma_mon", "ten_mon", "so_tin_chi", "loai_mon", "ma_khoa", "ten_khoa"]
    ]

    gv = raw["GiangVien"].copy()
    gv["ma_gv"] = gv["ma_gv"].str.strip().str.upper()
    gv["ho_ten"] = chuan_hoa_chuoi_ten(gv["ho_ten"])
    gv["ma_khoa"] = gv["ma_khoa"].str.strip().str.upper()
    dim_giang_vien = gv.merge(khoa, on="ma_khoa", how="left")[
        ["ma_gv", "ho_ten", "hoc_vi", "ma_khoa", "ten_khoa"]
    ]

    dim_ptxt = raw["PhuongThucXetTuyen"].copy()
    dim_ptxt["ma_ptxt"] = dim_ptxt["ma_ptxt"].str.strip().str.upper()

    dim_thoi_gian = tao_dim_thoi_gian(raw["HocKy"])
    ghi_log(dw_engine, run_id, "TRANSFORM", "dim_thoi_gian", len(raw["HocKy"]), len(dim_thoi_gian), 0, t0,
            "Sinh lịch ngày 2019-2027")

    # 3. Sinh viên + phiên bản SCD2
    t0 = datetime.now()
    sv = raw["SinhVien"].copy()
    sv["ma_sv"] = sv["ma_sv"].str.strip().str.upper()
    sv["ma_nganh"] = sv["ma_nganh"].str.strip().str.upper()
    sv["ma_lop"] = sv["ma_lop"].str.strip().str.upper()

    ho_ten_goc = sv["ho_ten"].astype(str)
    sv["ho_ten"] = chuan_hoa_chuoi_ten(sv["ho_ten"])
    so_ten_sv_sua = int((ho_ten_goc != sv["ho_ten"]).sum())

    sv["gioi_tinh"], so_gt_sv_sua = chuan_hoa_gioi_tinh(sv["gioi_tinh"])
    sv["tinh_thanh"], so_tinh_sv_sua = chuan_hoa_tinh_thanh(sv["tinh_thanh"])
    sv["vung_mien"] = sv["tinh_thanh"].map(ref.VUNG_MIEN).fillna("Khác")
    sv["nam_sinh"] = pd.to_datetime(sv["ngay_sinh"]).dt.year

    dq_rows.extend([
        {
            "run_id": run_id,
            "bang": "SinhVien",
            "loai_kiem_tra": "Họ tên viết thường / dư khoảng trắng",
            "so_dong_truoc": so_ten_sv_sua,
            "so_dong_sau": 0,
            "cach_xu_ly": "Trim + chuẩn hóa Title Case tiếng Việt",
        },
        {
            "run_id": run_id,
            "bang": "SinhVien",
            "loai_kiem_tra": "Giới tính không đồng nhất (M/F/Male/Female/nam/nu)",
            "so_dong_truoc": so_gt_sv_sua,
            "so_dong_sau": 0,
            "cach_xu_ly": "Chuẩn hóa về Nam / Nữ",
        },
        {
            "run_id": run_id,
            "bang": "SinhVien",
            "loai_kiem_tra": "Tên tỉnh/thành không chuẩn (không dấu, viết tắt, tiền tố)",
            "so_dong_truoc": so_tinh_sv_sua,
            "so_dong_sau": 0,
            "cach_xu_ly": "Ánh xạ về 18 tỉnh/thành chuẩn + bổ sung vùng miền",
        },
    ])

    stg_sv_version = xay_dung_phien_ban_scd2(sv, raw["LichSuChuyenNganh"], dim_nganh)
    ghi_log(
        dw_engine, run_id, "TRANSFORM", "dim_sinh_vien", len(sv), len(stg_sv_version), 0, t0,
        f"SCD2: {len(sv)} SV -> {len(stg_sv_version)} phiên bản ({len(stg_sv_version) - len(sv)} dòng lịch sử đổi ngành/lớp)",
    )

    # 4. Đăng ký học phần -> stg_fact_ket_qua_hoc_tap
    t0 = datetime.now()
    dk = raw["DangKyHocPhan"].copy()
    tong_dk_goc = len(dk)
    dk["ma_sv"] = dk["ma_sv"].str.strip().str.upper()
    dk["ma_lhp"] = dk["ma_lhp"].str.strip().str.upper()
    dk = dk.sort_values("ma_dang_ky").reset_index(drop=True)

    # 4a. Loại bản ghi trùng (ma_sv, ma_lhp), giữ bản ghi đầu tiên
    mask_trung = dk.duplicated(subset=["ma_sv", "ma_lhp"], keep="first")
    for r in dk.loc[mask_trung, ["ma_dang_ky", "ma_sv", "ma_lhp"]].itertuples(index=False):
        reject_rows.append({
            "run_id": run_id,
            "bang": "DangKyHocPhan",
            "khoa_nguon": f"ma_dang_ky={r.ma_dang_ky} ({r.ma_sv},{r.ma_lhp})",
            "ma_loi": "TRUNG_LAP",
            "mo_ta": "Trùng cặp (ma_sv, ma_lhp), giữ bản ghi đăng ký đầu tiên",
        })
    so_trung = int(mask_trung.sum())
    dk = dk.loc[~mask_trung].copy()

    # 4b. Loại bản ghi thiếu điểm quá trình hoặc điểm thi
    mask_thieu = dk["diem_qua_trinh"].isna() | dk["diem_thi"].isna()
    for r in dk.loc[mask_thieu, ["ma_dang_ky", "ma_sv", "ma_lhp"]].itertuples(index=False):
        reject_rows.append({
            "run_id": run_id,
            "bang": "DangKyHocPhan",
            "khoa_nguon": f"ma_dang_ky={r.ma_dang_ky}",
            "ma_loi": "THIEU_DIEM",
            "mo_ta": f"Thiếu điểm quá trình hoặc điểm thi ({r.ma_sv}, {r.ma_lhp})",
        })
    so_thieu = int(mask_thieu.sum())
    dk = dk.loc[~mask_thieu].copy()

    # 4c. Loại bản ghi điểm ngoài thang 0 - 10
    qt = dk["diem_qua_trinh"].astype(float)
    thi = dk["diem_thi"].astype(float)
    mask_ngoai = (qt < 0.0) | (qt > 10.0) | (thi < 0.0) | (thi > 10.0)
    for r in dk.loc[mask_ngoai, ["ma_dang_ky", "diem_qua_trinh", "diem_thi"]].itertuples(index=False):
        reject_rows.append({
            "run_id": run_id,
            "bang": "DangKyHocPhan",
            "khoa_nguon": f"ma_dang_ky={r.ma_dang_ky}",
            "ma_loi": "DIEM_NGOAI_THANG",
            "mo_ta": f"Điểm ngoài khoảng [0,10]: QT={r.diem_qua_trinh}, Thi={r.diem_thi}",
        })
    so_ngoai = int(mask_ngoai.sum())
    dk = dk.loc[~mask_ngoai].copy()

    # 4d. Tính lại điểm tổng kết chuẩn và kiểm tra sai lệch công thức
    tk_tinh_lai = tinh_diem_tong_ket(dk["diem_qua_trinh"].to_numpy(), dk["diem_thi"].to_numpy())
    tk_nguon = dk["diem_tong_ket"].astype(float).to_numpy()
    mask_sai_tk = np.isnan(tk_nguon) | (np.abs(tk_nguon - tk_tinh_lai) > 1e-5)
    so_sai_tk = int(mask_sai_tk.sum())
    dk["diem_tong_ket"] = tk_tinh_lai
    diem_chu, diem_he_4 = quy_doi_diem(tk_tinh_lai)
    dk["diem_chu"] = diem_chu
    dk["diem_he_4"] = diem_he_4
    dk["ket_qua_dat"] = (tk_tinh_lai >= DIEM_DAT).astype(int)

    # Kết nối LopHocPhan, HocKy, MonHoc để lấy ngày tham chiếu học kỳ và số tín chỉ
    lhp = raw["LopHocPhan"][["ma_lhp", "ma_mon", "ma_hoc_ky", "ma_gv"]].copy()
    hk = raw["HocKy"][["ma_hoc_ky", "ngay_bat_dau"]].copy()
    hk["ngay_bat_dau"] = pd.to_datetime(hk["ngay_bat_dau"]).dt.date
    mon_tc = dim_mon_hoc[["ma_mon", "so_tin_chi"]].copy()

    dk = dk.merge(lhp, on="ma_lhp", how="inner")
    dk = dk.merge(hk, on="ma_hoc_ky", how="inner")
    dk = dk.merge(mon_tc, on="ma_mon", how="inner")
    dk["ngay_tham_chieu"] = dk["ngay_bat_dau"]
    dk["thoi_gian_key"] = [d.year * 10000 + d.month * 100 + d.day for d in dk["ngay_tham_chieu"]]

    stg_fact_kq = dk[[
        "ma_dang_ky", "ma_sv", "ma_lhp", "ma_mon", "ma_gv",
        "ngay_tham_chieu", "thoi_gian_key",
        "diem_qua_trinh", "diem_thi", "diem_tong_ket",
        "diem_chu", "diem_he_4", "ket_qua_dat", "so_tin_chi",
    ]].copy()

    dq_rows.extend([
        {
            "run_id": run_id,
            "bang": "DangKyHocPhan",
            "loai_kiem_tra": "Bản ghi đăng ký trùng (ma_sv, ma_lhp)",
            "so_dong_truoc": so_trung,
            "so_dong_sau": 0,
            "cach_xu_ly": "Loại bản sao trùng, ghi vào etl_reject (TRUNG_LAP)",
        },
        {
            "run_id": run_id,
            "bang": "DangKyHocPhan",
            "loai_kiem_tra": "Thiếu điểm quá trình hoặc điểm thi (NULL)",
            "so_dong_truoc": so_thieu,
            "so_dong_sau": 0,
            "cach_xu_ly": "Loại bản ghi thiếu điểm, ghi vào etl_reject (THIEU_DIEM)",
        },
        {
            "run_id": run_id,
            "bang": "DangKyHocPhan",
            "loai_kiem_tra": "Điểm quá trình/thi ngoài thang [0, 10]",
            "so_dong_truoc": so_ngoai,
            "so_dong_sau": 0,
            "cach_xu_ly": "Loại bản ghi điểm lỗi, ghi vào etl_reject (DIEM_NGOAI_THANG)",
        },
        {
            "run_id": run_id,
            "bang": "DangKyHocPhan",
            "loai_kiem_tra": "Điểm tổng kết lệch công thức 0.4*QT + 0.6*Thi",
            "so_dong_truoc": so_sai_tk,
            "so_dong_sau": 0,
            "cach_xu_ly": "Tính lại điểm tổng kết, quy đổi điểm chữ và thang 4",
        },
    ])
    tong_loai_dk = so_trung + so_thieu + so_ngoai
    ghi_log(
        dw_engine, run_id, "TRANSFORM", "fact_ket_qua_hoc_tap",
        tong_dk_goc, len(stg_fact_kq), tong_loai_dk, t0,
        f"Loại {so_trung} trùng, {so_thieu} thiếu điểm, {so_ngoai} ngoài thang; sửa {so_sai_tk} điểm TK",
    )

    # 5. Hồ sơ tuyển sinh -> stg_fact_tuyen_sinh
    t0 = datetime.now()
    hs = raw["HoSoTuyenSinh"].copy()
    tong_hs_goc = len(hs)
    hs["ma_ho_so"] = hs["ma_ho_so"].str.strip().str.upper()
    hs["ma_nganh"] = hs["ma_nganh"].str.strip().str.upper()
    hs["ma_ptxt"] = hs["ma_ptxt"].str.strip().str.upper()
    hs["gioi_tinh"], so_gt_hs_sua = chuan_hoa_gioi_tinh(hs["gioi_tinh"])
    hs["tinh_thanh"], so_tinh_hs_sua = chuan_hoa_tinh_thanh(hs["tinh_thanh"])
    hs["trang_thai"], so_tt_hs_sua = chuan_hoa_trang_thai_hs(hs["trang_thai"])

    thang_map = dim_ptxt.set_index("ma_ptxt")["thang_diem"].astype(float).to_dict()
    thang_col = hs["ma_ptxt"].map(thang_map)

    mask_hs_null = hs["diem_xet_tuyen"].isna()
    for r in hs.loc[mask_hs_null, ["ma_ho_so", "ma_ptxt"]].itertuples(index=False):
        reject_rows.append({
            "run_id": run_id,
            "bang": "HoSoTuyenSinh",
            "khoa_nguon": f"ma_ho_so={r.ma_ho_so}",
            "ma_loi": "THIEU_DIEM_XT",
            "mo_ta": f"Thiếu điểm xét tuyển ({r.ma_ptxt})",
        })
    so_hs_null = int(mask_hs_null.sum())
    hs = hs.loc[~mask_hs_null].copy()
    thang_col = hs["ma_ptxt"].map(thang_map)

    diem_xt = hs["diem_xet_tuyen"].astype(float)
    mask_hs_ngoai = (diem_xt <= 0.0) | (diem_xt > thang_col)
    for r in hs.loc[mask_hs_ngoai, ["ma_ho_so", "ma_ptxt", "diem_xet_tuyen"]].itertuples(index=False):
        reject_rows.append({
            "run_id": run_id,
            "bang": "HoSoTuyenSinh",
            "khoa_nguon": f"ma_ho_so={r.ma_ho_so}",
            "ma_loi": "DIEM_XT_NGOAI_THANG",
            "mo_ta": f"Điểm xét tuyển ngoài thang ({r.ma_ptxt}): {r.diem_xet_tuyen}",
        })
    so_hs_ngoai = int(mask_hs_ngoai.sum())
    hs = hs.loc[~mask_hs_ngoai].copy()

    thang_col = hs["ma_ptxt"].map(thang_map)
    hs["diem_quy_doi_30"] = np.round(hs["diem_xet_tuyen"].astype(float) * 30.0 / thang_col, 2)
    hs["ngay_nop"] = pd.to_datetime(hs["ngay_nop"]).dt.date
    hs["thoi_gian_key"] = [d.year * 10000 + d.month * 100 + d.day for d in hs["ngay_nop"]]
    hs["is_trung_tuyen"] = (hs["trang_thai"] == "Trúng tuyển").astype(int)
    hs["is_nhap_hoc"] = hs["da_nhap_hoc"].astype(int)

    stg_fact_ts = hs[[
        "ma_ho_so", "ma_nganh", "ma_ptxt", "ma_sv",
        "ngay_nop", "thoi_gian_key", "gioi_tinh", "tinh_thanh",
        "diem_xet_tuyen", "diem_quy_doi_30", "is_trung_tuyen", "is_nhap_hoc",
    ]].copy()

    dq_rows.extend([
        {
            "run_id": run_id,
            "bang": "HoSoTuyenSinh",
            "loai_kiem_tra": "Thiếu điểm xét tuyển (NULL)",
            "so_dong_truoc": so_hs_null,
            "so_dong_sau": 0,
            "cach_xu_ly": "Loại hồ sơ thiếu điểm, ghi vào etl_reject (THIEU_DIEM_XT)",
        },
        {
            "run_id": run_id,
            "bang": "HoSoTuyenSinh",
            "loai_kiem_tra": "Điểm xét tuyển vượt thang (30 hoặc 1200) / âm",
            "so_dong_truoc": so_hs_ngoai,
            "so_dong_sau": 0,
            "cach_xu_ly": "Loại hồ sơ điểm ngoài thang, ghi vào etl_reject (DIEM_XT_NGOAI_THANG)",
        },
        {
            "run_id": run_id,
            "bang": "HoSoTuyenSinh",
            "loai_kiem_tra": "Tỉnh/thành, giới tính, trạng thái không thống nhất",
            "so_dong_truoc": so_tinh_hs_sua + so_gt_hs_sua + so_tt_hs_sua,
            "so_dong_sau": 0,
            "cach_xu_ly": "Chuẩn hóa về danh mục chuẩn và quy đổi điểm về thang 30",
        },
    ])
    ghi_log(
        dw_engine, run_id, "TRANSFORM", "fact_tuyen_sinh",
        tong_hs_goc, len(stg_fact_ts), so_hs_null + so_hs_ngoai, t0,
        f"Loại {so_hs_null} thiếu điểm, {so_hs_ngoai} ngoài thang; chuẩn hóa {so_tinh_hs_sua} tỉnh/thành",
    )

    if reject_rows:
        pd.DataFrame(reject_rows).to_sql(
            "etl_reject", dw_engine, if_exists="append", index=False, chunksize=1000, method="multi"
        )
    if dq_rows:
        pd.DataFrame(dq_rows).to_sql(
            "etl_data_quality", dw_engine, if_exists="append", index=False, chunksize=1000, method="multi"
        )

    return {
        "dim_thoi_gian": dim_thoi_gian,
        "dim_nganh": dim_nganh,
        "dim_mon_hoc": dim_mon_hoc,
        "dim_giang_vien": dim_giang_vien,
        "dim_ptxt": dim_ptxt,
        "stg_sinh_vien_version": stg_sv_version,
        "stg_fact_ket_qua_hoc_tap": stg_fact_kq,
        "stg_fact_tuyen_sinh": stg_fact_ts,
    }
