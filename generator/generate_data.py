"""Sinh dữ liệu giả lập (đã ẩn danh) cho CSDL nguồn edu_source.

Quy luật được mô phỏng:
  * Điểm đầu vào cao  -> học lực cao -> điểm học phần cao hơn.
  * Phương thức xét tuyển và tỉnh/thành có ảnh hưởng nhỏ tới học lực.
  * Một số môn "khó" có tỷ lệ rớt cao bất thường.
  * Nhu cầu các ngành tăng/giảm khác nhau qua các năm.
  * Khoảng 3% sinh viên đổi ngành ở đầu năm 2 (phục vụ SCD2).
  * Có chủ đích chèn một tỷ lệ nhỏ dữ liệu lỗi (ghi lại trong data/error_manifest.json).

Cách chạy (từ thư mục Code):
    python -m generator.generate_data            # sinh + nạp vào MySQL/MariaDB
    python -m generator.generate_data --csv-only # chỉ xuất CSV ra thư mục data/
"""
from __future__ import annotations

import argparse
import json
import math
import time
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

from common import reference as ref
from common.db import DATA_DIR, SQL_DIR, SOURCE_DB, get_engine, run_sql_file
from common.grading import round_half_up, tinh_diem_tong_ket

SEED = 2026
NAM_TUYEN_SINH = [2019, 2020, 2021, 2022]
HO_SO_MOI_NAM = 2000
TY_LE_TRUNG_TUYEN = 0.70
TY_LE_NHAP_HOC = 0.89
TY_LE_DOI_NGANH = 0.03
SO_HOC_KY = 8
MON_MOI_HOC_KY = 6
SI_SO_LHP = 70

TY_LE_LOI = {
    "dkhp_trung_lap": 0.004,
    "dkhp_thieu_diem": 0.004,
    "dkhp_ngoai_thang": 0.003,
    "dkhp_sai_tong_ket": 0.003,
    "sv_gioi_tinh": 0.05,
    "sv_tinh_thanh": 0.06,
    "sv_ho_ten": 0.03,
    "hs_diem_null": 0.003,
    "hs_diem_ngoai_thang": 0.003,
    "hs_tinh_thanh": 0.05,
    "hs_gioi_tinh": 0.04,
    "hs_trang_thai": 0.03,
}

rng = np.random.default_rng(SEED)
fake = Faker("vi_VN")
Faker.seed(SEED)


# ---------------------------------------------------------------------------
# Danh mục
# ---------------------------------------------------------------------------
def tao_danh_muc():
    khoa = pd.DataFrame(ref.KHOA, columns=["ma_khoa", "ten_khoa"])
    nganh = pd.DataFrame(
        [(m, t, k, h) for m, t, k, h, *_ in ref.NGANH],
        columns=["ma_nganh", "ten_nganh", "ma_khoa", "he_dao_tao"],
    )
    ptxt = pd.DataFrame(
        [(m, t, s, d) for m, t, s, d, *_ in ref.PHUONG_THUC],
        columns=["ma_ptxt", "ten_phuong_thuc", "thang_diem", "mo_ta"],
    )

    hoc_ky = []
    for y in range(min(NAM_TUYEN_SINH), max(NAM_TUYEN_SINH) + SO_HOC_KY // 2):
        hoc_ky.append((f"{y}1", f"{y}-{y + 1}", 1, date(y, 9, 5), date(y + 1, 1, 15)))
        hoc_ky.append((f"{y}2", f"{y}-{y + 1}", 2, date(y + 1, 2, 10), date(y + 1, 6, 30)))
    hoc_ky = pd.DataFrame(
        hoc_ky, columns=["ma_hoc_ky", "nam_hoc", "hoc_ky_so", "ngay_bat_dau", "ngay_ket_thuc"]
    )

    # Môn học
    mon = []
    for i, (ten, tc) in enumerate(ref.MON_DAI_CUONG, start=1):
        mon.append((f"KHCB{i:03d}", ten, tc, "Đại cương", "KHCB"))
    for ma_khoa, ds in ref.MON_THEO_KHOA.items():
        assert len(ds) == 36, f"Khoa {ma_khoa} cần đúng 36 môn, hiện có {len(ds)}"
        for i, ten in enumerate(ds, start=1):
            if i <= 12:
                loai, tc = "Cơ sở ngành", 3
            elif i <= 33:
                loai, tc = "Chuyên ngành", int(rng.choice([2, 3, 3, 4]))
            else:
                loai = "Thực tập/Đồ án"
                tc = 6 if "Khóa luận" in ten else (4 if "Thực tập" in ten else 3)
            mon.append((f"{ma_khoa}{i:03d}", ten, tc, loai, ma_khoa))
    mon_hoc = pd.DataFrame(mon, columns=["ma_mon", "ten_mon", "so_tin_chi", "loai_mon", "ma_khoa"])
    # Độ khó (ẩn, chỉ dùng để sinh điểm)
    do_kho = rng.normal(0, 0.45, len(mon_hoc))
    do_kho += np.where(mon_hoc["ten_mon"].isin(ref.MON_KHO), 1.7, 0.0)
    do_kho = dict(zip(mon_hoc["ma_mon"], do_kho))

    # Giảng viên
    gv = []
    so_gv = {"KHCB": 24, "KHMT": 36, "KTMT": 28, "KTS": 30}
    stt = 1
    hoc_vi_ten = [h for h, _ in ref.HOC_VI]
    hoc_vi_p = [p for _, p in ref.HOC_VI]
    for ma_khoa, n in so_gv.items():
        for _ in range(n):
            gv.append((f"GV{stt:04d}", fake.name(), str(rng.choice(hoc_vi_ten, p=hoc_vi_p)), ma_khoa))
            stt += 1
    giang_vien = pd.DataFrame(gv, columns=["ma_gv", "ho_ten", "hoc_vi", "ma_khoa"])
    hieu_ung_gv = dict(zip(giang_vien["ma_gv"], rng.normal(0, 0.25, len(giang_vien))))

    # Mỗi môn có 2-4 giảng viên phụ trách (cùng khoa)
    gv_theo_mon = {}
    for _, m in mon_hoc.iterrows():
        ds = giang_vien.loc[giang_vien["ma_khoa"] == m["ma_khoa"], "ma_gv"].to_numpy()
        gv_theo_mon[m["ma_mon"]] = rng.choice(ds, size=int(rng.integers(2, 5)), replace=False)

    # Chương trình đào tạo: HK1-2 đại cương; HK3-4 cơ sở ngành; HK5-8 chuyên ngành + tốt nghiệp
    dai_cuong = [f"KHCB{i:03d}" for i in range(1, 13)]
    ctdt = {}
    for idx, (ma_nganh, _, ma_khoa, *_) in enumerate(ref.NGANH):
        r = np.random.default_rng(SEED + idx)  # mỗi ngành một thứ tự môn khác nhau
        co_so = [f"{ma_khoa}{i:03d}" for i in range(1, 13)]
        chuyen = [f"{ma_khoa}{i:03d}" for i in range(13, 34)]
        tot_nghiep = [f"{ma_khoa}{i:03d}" for i in range(34, 37)]
        r.shuffle(co_so)
        r.shuffle(chuyen)
        hk = {1: dai_cuong[:6], 2: dai_cuong[6:], 3: co_so[:6], 4: co_so[6:]}
        for k in range(5, 8):
            hk[k] = chuyen[(k - 5) * 6:(k - 4) * 6]
        hk[8] = chuyen[18:] + tot_nghiep
        ctdt[ma_nganh] = hk

    return dict(
        khoa=khoa, nganh=nganh, ptxt=ptxt, hoc_ky=hoc_ky, mon_hoc=mon_hoc, giang_vien=giang_vien,
        do_kho=do_kho, hieu_ung_gv=hieu_ung_gv, gv_theo_mon=gv_theo_mon, ctdt=ctdt,
    )


# ---------------------------------------------------------------------------
# Tuyển sinh & sinh viên
# ---------------------------------------------------------------------------
def tao_tuyen_sinh():
    ma_nganh = np.array([n[0] for n in ref.NGANH])
    nhu_cau = np.array([n[4] for n in ref.NGANH])
    tang_truong = np.array([n[5] for n in ref.NGANH])
    pt = {p[0]: p for p in ref.PHUONG_THUC}
    tinh = np.array([t[0] for t in ref.TINH_THANH])
    tinh_p = np.array([t[2] for t in ref.TINH_THANH], dtype=float)
    tinh_p /= tinh_p.sum()

    rows = []
    for i, nam in enumerate(NAM_TUYEN_SINH):
        n = int(HO_SO_MOI_NAM * rng.uniform(0.95, 1.05))
        w = nhu_cau * (1 + tang_truong) ** i
        w /= w.sum()
        p_pt = np.array([0.45 - 0.03 * i, 0.40 - 0.02 * i, 0.15 + 0.05 * i])
        nganh_hs = rng.choice(ma_nganh, size=n, p=w)
        pt_hs = rng.choice(["HB", "THPT", "DGNL"], size=n, p=p_pt / p_pt.sum())
        gioi = rng.choice(["Nam", "Nữ"], size=n, p=[0.62, 0.38])
        tinh_hs = rng.choice(tinh, size=n, p=tinh_p)
        for j in range(n):
            _, _, thang, _, mu, sd, _ = pt[pt_hs[j]]
            z = rng.normal()
            diem = float(np.clip(mu + sd * z, thang * 0.5, thang))
            diem = round(diem, 2) if thang <= 30 else float(round(diem))
            tuoi = 18 if rng.random() < 0.94 else int(rng.integers(19, 21))
            ngay_sinh = date(nam - tuoi, 1, 1) + timedelta(days=int(rng.integers(0, 365)))
            ho_ten = fake.name_male() if gioi[j] == "Nam" else fake.name_female()
            ngay_nop = date(nam, 3, 1) + timedelta(days=int(rng.integers(0, 150)))
            rows.append(dict(
                ma_ho_so=f"HS{nam}{j + 1:05d}", ho_ten=ho_ten, gioi_tinh=gioi[j], ngay_sinh=ngay_sinh,
                tinh_thanh=tinh_hs[j], ma_nganh=nganh_hs[j], ma_ptxt=pt_hs[j], nam_tuyen_sinh=nam,
                ngay_nop=ngay_nop, diem_xet_tuyen=diem, z_dau_vao=z,
            ))
    hs = pd.DataFrame(rows)

    # Trúng tuyển: top 70% theo từng (năm, ngành, phương thức)
    hs["hang"] = hs.groupby(["nam_tuyen_sinh", "ma_nganh", "ma_ptxt"])["diem_xet_tuyen"].rank(
        ascending=False, pct=True, method="first"
    )
    hs["trung_tuyen"] = hs["hang"] <= TY_LE_TRUNG_TUYEN
    hs["da_nhap_hoc"] = (hs["trung_tuyen"] & (rng.random(len(hs)) < TY_LE_NHAP_HOC)).astype(int)
    hs["trang_thai"] = np.where(hs["trung_tuyen"], "Trúng tuyển", "Không trúng tuyển")
    return hs


def tao_sinh_vien(hs: pd.DataFrame, dm: dict):
    pt_effect = {p[0]: p[6] for p in ref.PHUONG_THUC}
    tinh_effect = {t[0]: t[3] for t in ref.TINH_THANH}
    nhap_hoc = hs[hs["da_nhap_hoc"] == 1].sort_values(["nam_tuyen_sinh", "ma_nganh", "ma_ho_so"]).copy()

    nhap_hoc["stt"] = nhap_hoc.groupby(["nam_tuyen_sinh", "ma_nganh"]).cumcount()
    yy = (nhap_hoc["nam_tuyen_sinh"] % 100).astype(str).str.zfill(2)
    nhap_hoc["ma_sv"] = yy + nhap_hoc["ma_nganh"] + (nhap_hoc["stt"] + 1).astype(str).str.zfill(3)
    nhap_hoc["ma_lop"] = yy + nhap_hoc["ma_nganh"] + (nhap_hoc["stt"] // 60 + 1).astype(str)

    # Học lực ẩn
    nhap_hoc["hoc_luc"] = (
        0.65 * nhap_hoc["z_dau_vao"]
        + nhap_hoc["ma_ptxt"].map(pt_effect)
        + nhap_hoc["tinh_thanh"].map(tinh_effect)
        + rng.normal(0, 0.75, len(nhap_hoc))
    )

    sv = nhap_hoc[["ma_sv", "ho_ten", "gioi_tinh", "ngay_sinh", "tinh_thanh", "ma_nganh", "ma_lop",
                   "nam_tuyen_sinh", "hoc_luc", "ma_ho_so"]].rename(columns={"nam_tuyen_sinh": "nam_nhap_hoc"})
    sv = sv.reset_index(drop=True)
    sv["ma_nganh_ban_dau"] = sv["ma_nganh"]
    sv["ma_lop_ban_dau"] = sv["ma_lop"]

    # Đổi ngành (cùng khoa) đầu năm thứ 2
    khoa_cua_nganh = {n[0]: n[2] for n in ref.NGANH}
    nganh_cung_khoa = {
        m: [n[0] for n in ref.NGANH if n[2] == khoa_cua_nganh[m] and n[0] != m] for m in khoa_cua_nganh
    }
    lich_su = []
    idx_doi = rng.choice(len(sv), size=int(len(sv) * TY_LE_DOI_NGANH), replace=False)
    for i in idx_doi:
        cu = sv.at[i, "ma_nganh"]
        moi = str(rng.choice(nganh_cung_khoa[cu]))
        nam = int(sv.at[i, "nam_nhap_hoc"])
        lop_moi_ds = sv.loc[(sv["ma_nganh_ban_dau"] == moi) & (sv["nam_nhap_hoc"] == nam), "ma_lop_ban_dau"].unique()
        lop_moi = str(rng.choice(lop_moi_ds)) if len(lop_moi_ds) else f"{nam % 100:02d}{moi}1"
        lich_su.append(dict(ma_sv=sv.at[i, "ma_sv"], ma_nganh_cu=cu, ma_nganh_moi=moi,
                            ma_lop_cu=sv.at[i, "ma_lop"], ma_lop_moi=lop_moi,
                            ngay_chuyen=date(nam + 1, 8, 25)))
        sv.at[i, "ma_nganh"] = moi
        sv.at[i, "ma_lop"] = lop_moi
    lich_su = pd.DataFrame(lich_su)
    return sv, lich_su


# ---------------------------------------------------------------------------
# Lớp học phần & đăng ký học phần (bảng fact nguồn)
# ---------------------------------------------------------------------------
def tao_dang_ky(sv: pd.DataFrame, dm: dict):
    hk_info = dm["hoc_ky"].set_index("ma_hoc_ky")
    rows = []
    trang_thai = {}
    for r in sv.itertuples(index=False):
        bo_hoc = False
        for k in range(1, SO_HOC_KY + 1):
            if k >= 2:
                hazard = 0.012 + (0.03 if r.hoc_luc < -1.2 else 0.0)
                if rng.random() < hazard:
                    bo_hoc = True
                    break
            nganh_hk = r.ma_nganh if k >= 3 else r.ma_nganh_ban_dau
            ma_hk = f"{r.nam_nhap_hoc + (k - 1) // 2}{(k - 1) % 2 + 1}"
            for ma_mon in dm["ctdt"][nganh_hk][k]:
                rows.append((r.ma_sv, ma_mon, ma_hk, k, r.hoc_luc))
        trang_thai[r.ma_sv] = "Thôi học" if bo_hoc else "Đã tốt nghiệp"
    dk = pd.DataFrame(rows, columns=["ma_sv", "ma_mon", "ma_hoc_ky", "hoc_ky_thu", "hoc_luc"])

    # Chia lớp học phần
    dk = dk.sample(frac=1.0, random_state=SEED).reset_index(drop=True)
    dk["thu_tu"] = dk.groupby(["ma_mon", "ma_hoc_ky"]).cumcount()
    dk["so_luong"] = dk.groupby(["ma_mon", "ma_hoc_ky"])["ma_sv"].transform("size")
    dk["so_lop"] = np.ceil(dk["so_luong"] / SI_SO_LHP).astype(int)
    dk["nhom"] = dk["thu_tu"] % dk["so_lop"] + 1
    dk["ma_lhp"] = dk["ma_mon"] + "_" + dk["ma_hoc_ky"] + "_" + dk["nhom"].astype(str).str.zfill(2)

    lhp = dk[["ma_lhp", "ma_mon", "ma_hoc_ky"]].drop_duplicates().sort_values("ma_lhp").reset_index(drop=True)
    lhp["ma_gv"] = [str(rng.choice(dm["gv_theo_mon"][m])) for m in lhp["ma_mon"]]
    lhp["si_so_toi_da"] = SI_SO_LHP + 10
    dk = dk.merge(lhp[["ma_lhp", "ma_gv"]], on="ma_lhp")

    # Sinh điểm
    n = len(dk)
    nen = (
        6.7 + 1.0 * dk["hoc_luc"].to_numpy()
        - dk["ma_mon"].map(dm["do_kho"]).to_numpy()
        + dk["ma_gv"].map(dm["hieu_ung_gv"]).to_numpy()
        + 0.04 * (dk["hoc_ky_thu"].to_numpy() - 1)
        + rng.normal(0, 0.6, n)
    )
    qt = np.clip(round_half_up(nen + 0.6 + rng.normal(0, 0.7, n), 1), 0, 10)
    thi = np.clip(np.floor((nen - 0.3 + rng.normal(0, 1.1, n)) * 4 + 0.5) / 4, 0, 10)
    dk["diem_qua_trinh"] = qt
    dk["diem_thi"] = thi
    dk["diem_tong_ket"] = tinh_diem_tong_ket(qt, thi)

    bat_dau = dk["ma_hoc_ky"].map(hk_info["ngay_bat_dau"])
    dk["ngay_dang_ky"] = [d - timedelta(days=int(x)) for d, x in zip(bat_dau, rng.integers(7, 21, n))]
    dk = dk.sort_values(["ma_hoc_ky", "ma_lhp", "ma_sv"]).reset_index(drop=True)
    dk.insert(0, "ma_dang_ky", np.arange(1, n + 1))
    return dk, lhp, trang_thai


# ---------------------------------------------------------------------------
# Chèn lỗi có chủ đích
# ---------------------------------------------------------------------------
def bien_the_tinh(ten: str) -> str:
    kieu = rng.integers(0, 5)
    if kieu == 0:
        return ref.bo_dau(ten)                      # Da Nang
    if kieu == 1:
        return f"  {ten.lower()} "                  # '  đà nẵng '
    if kieu == 2:
        return ("TP. " if ten in ("Đà Nẵng", "Hà Nội") else "Tỉnh ") + ten
    if kieu == 3:
        return ten.upper()
    alias = {"Thừa Thiên Huế": "Huế", "TP. Hồ Chí Minh": "HCM"}
    return alias.get(ten, ref.bo_dau(ten).upper())


def bien_the_gioi(g: str) -> str:
    return str(rng.choice(["nam", "M", "Male", "NAM"] if g == "Nam" else ["nữ", "nu", "F", "Female"]))


def chon_chi_so(pool: np.ndarray, ty_le: float, total: int, da_dung: set) -> np.ndarray:
    ung_vien = np.array([i for i in pool if i not in da_dung])
    k = min(len(ung_vien), int(round(total * ty_le)))
    chon = rng.choice(ung_vien, size=k, replace=False)
    da_dung.update(chon.tolist())
    return np.sort(chon)


def chen_loi(dm, sv, hs, dk):
    manifest = {"thoi_diem": datetime.now().isoformat(timespec="seconds"), "ty_le": TY_LE_LOI}

    # --- Nganh: tên không thống nhất ---
    nganh = dm["nganh"]
    nganh.loc[nganh["ma_nganh"] == "IT", "ten_nganh"] = "  công nghệ   thông tin "
    nganh.loc[nganh["ma_nganh"] == "SE", "ten_nganh"] = "Kỹ Thuật Phần Mềm"
    manifest["nganh_ten_khong_chuan"] = ["IT", "SE"]

    # --- DangKyHocPhan ---
    n = len(dk)
    da_dung: set = set()
    pool = np.arange(n)
    i_thieu = chon_chi_so(pool, TY_LE_LOI["dkhp_thieu_diem"], n, da_dung)
    cot = rng.choice(["diem_thi", "diem_qua_trinh"], size=len(i_thieu), p=[0.7, 0.3])
    for i, c in zip(i_thieu, cot):
        dk.at[i, c] = np.nan
        dk.at[i, "diem_tong_ket"] = np.nan

    i_ngoai = chon_chi_so(pool, TY_LE_LOI["dkhp_ngoai_thang"], n, da_dung)
    gia_tri = rng.choice([10.5, 11.0, 12.5, 15.0, -1.0, -0.5, 75.0, 85.0], size=len(i_ngoai))
    cot = rng.choice(["diem_thi", "diem_qua_trinh"], size=len(i_ngoai))
    for i, c, v in zip(i_ngoai, cot, gia_tri):
        dk.at[i, c] = v

    i_sai = chon_chi_so(pool, TY_LE_LOI["dkhp_sai_tong_ket"], n, da_dung)
    lech = rng.choice([-2.0, -1.0, -0.5, 0.5, 1.0, 2.0], size=len(i_sai))
    dk.loc[i_sai, "diem_tong_ket"] = np.clip(dk.loc[i_sai, "diem_tong_ket"].to_numpy() + lech, 0, 10)

    i_trung = chon_chi_so(pool, TY_LE_LOI["dkhp_trung_lap"], n, da_dung)
    trung = dk.loc[i_trung].copy()
    trung["ngay_dang_ky"] = [d + timedelta(days=1) for d in trung["ngay_dang_ky"]]
    trung["ma_dang_ky"] = np.arange(n + 1, n + 1 + len(trung))
    manifest["dkhp"] = {
        "tong_dong_goc": int(n),
        "thieu_diem": dk.loc[i_thieu, "ma_dang_ky"].tolist(),
        "ngoai_thang": dk.loc[i_ngoai, "ma_dang_ky"].tolist(),
        "sai_tong_ket": dk.loc[i_sai, "ma_dang_ky"].tolist(),
        "trung_lap_ban_sao": trung["ma_dang_ky"].tolist(),
    }
    dk = pd.concat([dk, trung], ignore_index=True)

    # --- SinhVien ---
    m = len(sv)
    i = rng.choice(m, size=int(m * TY_LE_LOI["sv_gioi_tinh"]), replace=False)
    sv.loc[i, "gioi_tinh"] = [bien_the_gioi(g) for g in sv.loc[i, "gioi_tinh"]]
    j = rng.choice(m, size=int(m * TY_LE_LOI["sv_tinh_thanh"]), replace=False)
    sv.loc[j, "tinh_thanh"] = [bien_the_tinh(t) for t in sv.loc[j, "tinh_thanh"]]
    k = rng.choice(m, size=int(m * TY_LE_LOI["sv_ho_ten"]), replace=False)
    sv.loc[k, "ho_ten"] = ["  " + t.lower().replace(" ", "  ") for t in sv.loc[k, "ho_ten"]]
    manifest["sinh_vien"] = {"gioi_tinh": len(i), "tinh_thanh": len(j), "ho_ten": len(k)}

    # --- HoSoTuyenSinh ---
    h = len(hs)
    da_dung = set()
    pool = np.arange(h)
    i_null = chon_chi_so(pool, TY_LE_LOI["hs_diem_null"], h, da_dung)
    hs.loc[i_null, "diem_xet_tuyen"] = np.nan
    i_ng = chon_chi_so(pool, TY_LE_LOI["hs_diem_ngoai_thang"], h, da_dung)
    hs.loc[i_ng, "diem_xet_tuyen"] = [
        (1350.0 if p == "DGNL" else float(rng.choice([31.5, 34.0, -3.0]))) for p in hs.loc[i_ng, "ma_ptxt"]
    ]
    a = rng.choice(h, size=int(h * TY_LE_LOI["hs_tinh_thanh"]), replace=False)
    hs.loc[a, "tinh_thanh"] = [bien_the_tinh(t) for t in hs.loc[a, "tinh_thanh"]]
    b = rng.choice(h, size=int(h * TY_LE_LOI["hs_gioi_tinh"]), replace=False)
    hs.loc[b, "gioi_tinh"] = [bien_the_gioi(g) for g in hs.loc[b, "gioi_tinh"]]
    c = rng.choice(h, size=int(h * TY_LE_LOI["hs_trang_thai"]), replace=False)
    hs.loc[c, "trang_thai"] = [
        str(rng.choice(["trung tuyen", "TRÚNG TUYỂN", "Trúng Tuyển "])) if t == "Trúng tuyển"
        else str(rng.choice(["khong trung tuyen", "KHÔNG TRÚNG TUYỂN", " Không trúng tuyển"]))
        for t in hs.loc[c, "trang_thai"]
    ]
    manifest["ho_so"] = {
        "diem_null": hs.loc[i_null, "ma_ho_so"].tolist(),
        "diem_ngoai_thang": hs.loc[i_ng, "ma_ho_so"].tolist(),
        "tinh_thanh": len(a), "gioi_tinh": len(b), "trang_thai": len(c),
    }
    return sv, hs, dk, manifest


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(argv=None):
    parser = argparse.ArgumentParser(description="Sinh dữ liệu giả lập cho CSDL nguồn edu_source")
    parser.add_argument("--csv-only", action="store_true", help="Chỉ xuất CSV, không nạp vào CSDL")
    args, _ = parser.parse_known_args(argv)
    t0 = time.time()

    print("[1/5] Tạo danh mục (khoa, ngành, môn, học kỳ, giảng viên)...")
    dm = tao_danh_muc()
    print("[2/5] Sinh hồ sơ tuyển sinh...")
    hs = tao_tuyen_sinh()
    print("[3/5] Sinh sinh viên và lịch sử đổi ngành...")
    sv, lich_su = tao_sinh_vien(hs, dm)
    print("[4/5] Sinh lớp học phần và đăng ký học phần...")
    dk, lhp, trang_thai = tao_dang_ky(sv, dm)

    sv["trang_thai"] = sv["ma_sv"].map(trang_thai)
    sv["ngay_cap_nhat"] = [
        datetime(nam + 1, 8, 25, 9, 0) if ma in set(lich_su["ma_sv"]) else datetime(nam, 9, 1, 8, 0)
        for ma, nam in zip(sv["ma_sv"], sv["nam_nhap_hoc"])
    ]
    hs = hs.merge(sv[["ma_ho_so", "ma_sv"]], on="ma_ho_so", how="left")

    sv, hs, dk, manifest = chen_loi(dm, sv, hs, dk)

    bang = {
        "Khoa": dm["khoa"],
        "Nganh": dm["nganh"],
        "PhuongThucXetTuyen": dm["ptxt"],
        "GiangVien": dm["giang_vien"],
        "MonHoc": dm["mon_hoc"],
        "HocKy": dm["hoc_ky"],
        "SinhVien": sv[["ma_sv", "ho_ten", "gioi_tinh", "ngay_sinh", "tinh_thanh", "ma_nganh", "ma_lop",
                        "nam_nhap_hoc", "trang_thai", "ngay_cap_nhat"]],
        "LichSuChuyenNganh": lich_su,
        "LopHocPhan": lhp[["ma_lhp", "ma_mon", "ma_hoc_ky", "ma_gv", "si_so_toi_da"]],
        "DangKyHocPhan": dk[["ma_dang_ky", "ma_sv", "ma_lhp", "ngay_dang_ky", "diem_qua_trinh",
                             "diem_thi", "diem_tong_ket"]],
        "HoSoTuyenSinh": hs[["ma_ho_so", "ho_ten", "gioi_tinh", "ngay_sinh", "tinh_thanh", "ma_nganh",
                             "ma_ptxt", "nam_tuyen_sinh", "ngay_nop", "diem_xet_tuyen", "trang_thai",
                             "da_nhap_hoc", "ma_sv"]],
    }

    DATA_DIR.mkdir(exist_ok=True)
    for ten, df in bang.items():
        df.to_csv(DATA_DIR / f"{ten}.csv", index=False, encoding="utf-8-sig")
    (DATA_DIR / "error_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("\nSố dòng mỗi bảng:")
    for ten, df in bang.items():
        print(f"   {ten:<20} {len(df):>9,}")

    if not args.csv_only:
        print(f"\n[5/5] Tạo CSDL {SOURCE_DB} và nạp dữ liệu...")
        engine_server = get_engine()
        run_sql_file(engine_server, SQL_DIR / "01_create_source_db.sql")
        engine = get_engine(SOURCE_DB)
        for ten, df in bang.items():
            df.to_sql(ten.lower(), engine, if_exists="append", index=False, chunksize=1000, method="multi")
            print(f"   đã nạp {ten}")
    else:
        print("\n[5/5] Bỏ qua bước nạp CSDL (--csv-only). CSV nằm ở thư mục data/")

    print(f"\nHoàn tất sau {time.time() - t0:.1f} giây.")


if __name__ == "__main__":
    main()
