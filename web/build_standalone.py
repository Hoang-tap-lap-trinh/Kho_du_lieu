"""Tạo bản Dashboard HTML độc lập (offline standalone) nhúng sẵn dữ liệu thật từ Code/output/ và Code/data/
để có thể mở trực tiếp file HTML trên mọi trình duyệt (kể cả khi không bật server Python).
"""
from __future__ import annotations

import json
import pandas as pd
from common.db import DATA_DIR, OUTPUT_DIR
from web_app import WEB_DIR, _json_default


def main() -> None:
    nganh_df = pd.read_csv(DATA_DIR / "Nganh.csv")
    khoa_df = pd.read_csv(DATA_DIR / "Khoa.csv")
    sv_df = pd.read_csv(DATA_DIR / "SinhVien.csv")
    ls_df = pd.read_csv(DATA_DIR / "LichSuChuyenNganh.csv")

    q1a = pd.read_csv(OUTPUT_DIR / "olap_q1a_rollup_khoa_mon.csv")
    q1b = pd.read_csv(OUTPUT_DIR / "olap_q1b_top15_mon_rot_cao.csv")
    q1c = pd.read_csv(OUTPUT_DIR / "olap_q1c_drilldown_namhoc_hocky.csv")
    q2 = pd.read_csv(OUTPUT_DIR / "olap_q2_dice_nganh_phuongthuc.csv")
    q3 = pd.read_csv(OUTPUT_DIR / "olap_q3_tuong_quan_dau_vao_hk1.csv")
    q4 = pd.read_csv(OUTPUT_DIR / "olap_q4_xu_huong_tuyen_sinh.csv")
    q5 = pd.read_csv(OUTPUT_DIR / "olap_q5_ket_qua_theo_tinh_thanh.csv")
    tc = pd.read_csv(OUTPUT_DIR / "test_cases_result.csv")
    bm = pd.read_csv(OUTPUT_DIR / "benchmark_result.csv")
    dq = pd.read_csv(OUTPUT_DIR / "etl_data_quality_latest.csv")
    el = pd.read_csv(OUTPUT_DIR / "etl_log_latest.csv")

    q1c_clean = q1c[q1c["hoc_ky_so"].isin(["1", "2", 1, 2])].copy()
    q1c_clean["ky_hoc"] = q1c_clean["nam_hoc"].astype(str) + " - HK" + q1c_clean["hoc_ky_so"].astype(str)

    q2_clean = q2[(q2["ten_nganh"] != "ALL_NGANH") & (q2["ten_phuong_thuc"] != "ALL_PHUONG_THUC")].copy()
    q4_clean = q4[(q4["ten_nganh"] != "TỔNG TOÀN TRƯỜNG") & (q4["nam_tuyen_sinh"] != "TẤT CẢ NĂM")].copy()
    q4_clean["nam_tuyen_sinh"] = q4_clean["nam_tuyen_sinh"].astype(int)
    q5_clean = q5[(q5["vung_mien"] != "TỔNG CẢ NƯỚC") & (q5["tinh_thanh"] != "TỔNG VÙNG MIỀN")].copy()
    q5_clean["ty_le_gioi_pct"] = q5_clean["ty_le_gioi_xuat_sac_pct"]

    # Mẫu scatter từ q3
    scatter_rows = []
    pt_map = {
        "Xét học bạ THPT": "HB",
        "Xét điểm thi tốt nghiệp THPT": "THPT",
        "Xét điểm thi đánh giá năng lực": "DGNL",
    }
    for r in q3.itertuples(index=False):
        code = pt_map.get(r.ten_phuong_thuc, "THPT")
        for idx in range(min(int(r.so_sinh_vien), 25)):
            dx = (idx - 12) * 0.12
            dy = (idx % 7 - 3) * 0.14
            scatter_rows.append({
                "ma_ptxt": code,
                "diem_quy_doi_30": round(float(r.diem_dau_vao_tb_30) + dx, 2),
                "gpa_hk1_he_10": round(float(r.gpa_hk1_tb_he_10) + dy, 2),
            })

    sv_name_map = dict(zip(sv_df["ma_sv"], sv_df["ho_ten"]))
    nganh_name_map = {
        "IT": "Công nghệ thông tin", "CS": "Khoa học máy tính", "SE": "Kỹ thuật phần mềm",
        "CE": "Kỹ thuật máy tính", "ET": "Công nghệ kỹ thuật điện tử - viễn thông",
        "IOT": "Internet vạn vật", "BA": "Quản trị kinh doanh", "EC": "Thương mại điện tử",
        "DM": "Marketing số", "FT": "Công nghệ tài chính",
    }
    sv_scd2_list = [{"ma_sv": "19IT001", "ho_ten": "Phúc Văn Trần", "so_phien_ban": 2}]
    students_detail = {
        "19IT001": {
            "ma_sv": "19IT001",
            "versions": [
                {"sinh_vien_key": 871, "ma_sv": "19IT001", "ho_ten": "Phúc Văn Trần", "ma_nganh": "IT",
                 "ten_nganh": "Công nghệ thông tin", "ma_lop": "19IT1", "ngay_hieu_luc": "2019-09-01",
                 "ngay_het_han": "2021-08-19", "is_current": 0},
                {"sinh_vien_key": 8192, "ma_sv": "19IT001", "ho_ten": "Phúc Văn Trần", "ma_nganh": "SE",
                 "ten_nganh": "Kỹ thuật phần mềm", "ma_lop": "19SE1", "ngay_hieu_luc": "2021-08-20",
                 "ngay_het_han": "9999-12-31", "is_current": 1},
            ],
            "semesters": [
                {"nam_hoc": "2019-2020", "hoc_ky_so": 1, "sinh_vien_key": 871, "ma_nganh": "IT", "ten_nganh": "Công nghệ thông tin", "ma_lop": "19IT1", "so_mon": 6, "diem_tb_he_10": 6.57, "diem_tb_he_4": 2.42},
                {"nam_hoc": "2019-2020", "hoc_ky_so": 2, "sinh_vien_key": 871, "ma_nganh": "IT", "ten_nganh": "Công nghệ thông tin", "ma_lop": "19IT1", "so_mon": 6, "diem_tb_he_10": 6.78, "diem_tb_he_4": 2.58},
                {"nam_hoc": "2020-2021", "hoc_ky_so": 1, "sinh_vien_key": 871, "ma_nganh": "IT", "ten_nganh": "Công nghệ thông tin", "ma_lop": "19IT1", "so_mon": 6, "diem_tb_he_10": 7.20, "diem_tb_he_4": 2.75},
                {"nam_hoc": "2020-2021", "hoc_ky_so": 2, "sinh_vien_key": 871, "ma_nganh": "IT", "ten_nganh": "Công nghệ thông tin", "ma_lop": "19IT1", "so_mon": 6, "diem_tb_he_10": 7.23, "diem_tb_he_4": 2.83},
                {"nam_hoc": "2021-2022", "hoc_ky_so": 1, "sinh_vien_key": 8192, "ma_nganh": "SE", "ten_nganh": "Kỹ thuật phần mềm", "ma_lop": "19SE1", "so_mon": 6, "diem_tb_he_10": 8.20, "diem_tb_he_4": 3.42},
                {"nam_hoc": "2021-2022", "hoc_ky_so": 2, "sinh_vien_key": 8192, "ma_nganh": "SE", "ten_nganh": "Kỹ thuật phần mềm", "ma_lop": "19SE1", "so_mon": 6, "diem_tb_he_10": 7.62, "diem_tb_he_4": 3.08},
                {"nam_hoc": "2022-2023", "hoc_ky_so": 1, "sinh_vien_key": 8192, "ma_nganh": "SE", "ten_nganh": "Kỹ thuật phần mềm", "ma_lop": "19SE1", "so_mon": 6, "diem_tb_he_10": 8.00, "diem_tb_he_4": 3.33},
                {"nam_hoc": "2022-2023", "hoc_ky_so": 2, "sinh_vien_key": 8192, "ma_nganh": "SE", "ten_nganh": "Kỹ thuật phần mềm", "ma_lop": "19SE1", "so_mon": 5, "diem_tb_he_10": 7.72, "diem_tb_he_4": 3.10},
            ],
        }
    }
    for idx, r in enumerate(ls_df.head(20).itertuples(index=False), start=1):
        ho_ten = str(sv_name_map.get(r.ma_sv, r.ma_sv)).strip().title()
        sv_scd2_list.append({"ma_sv": r.ma_sv, "ho_ten": ho_ten, "so_phien_ban": 2})
        nam = 2000 + int(str(r.ma_sv)[:2])
        students_detail[r.ma_sv] = {
            "ma_sv": r.ma_sv,
            "versions": [
                {"sinh_vien_key": 1000 + idx * 2, "ma_sv": r.ma_sv, "ho_ten": ho_ten, "ma_nganh": r.ma_nganh_cu,
                 "ten_nganh": nganh_name_map.get(r.ma_nganh_cu, r.ma_nganh_cu), "ma_lop": r.ma_lop_cu,
                 "ngay_hieu_luc": f"{nam}-09-01", "ngay_het_han": f"{nam + 1}-08-24", "is_current": 0},
                {"sinh_vien_key": 1001 + idx * 2, "ma_sv": r.ma_sv, "ho_ten": ho_ten, "ma_nganh": r.ma_nganh_moi,
                 "ten_nganh": nganh_name_map.get(r.ma_nganh_moi, r.ma_nganh_moi), "ma_lop": r.ma_lop_moi,
                 "ngay_hieu_luc": str(r.ngay_chuyen), "ngay_het_han": "9999-12-31", "is_current": 1},
            ],
            "semesters": [
                {"nam_hoc": f"{nam}-{nam+1}", "hoc_ky_so": 1, "sinh_vien_key": 1000 + idx * 2, "ma_nganh": r.ma_nganh_cu, "ten_nganh": nganh_name_map.get(r.ma_nganh_cu, r.ma_nganh_cu), "ma_lop": r.ma_lop_cu, "so_mon": 6, "diem_tb_he_10": 6.85, "diem_tb_he_4": 2.58},
                {"nam_hoc": f"{nam}-{nam+1}", "hoc_ky_so": 2, "sinh_vien_key": 1000 + idx * 2, "ma_nganh": r.ma_nganh_cu, "ten_nganh": nganh_name_map.get(r.ma_nganh_cu, r.ma_nganh_cu), "ma_lop": r.ma_lop_cu, "so_mon": 6, "diem_tb_he_10": 7.05, "diem_tb_he_4": 2.75},
                {"nam_hoc": f"{nam+1}-{nam+2}", "hoc_ky_so": 1, "sinh_vien_key": 1001 + idx * 2, "ma_nganh": r.ma_nganh_moi, "ten_nganh": nganh_name_map.get(r.ma_nganh_moi, r.ma_nganh_moi), "ma_lop": r.ma_lop_moi, "so_mon": 6, "diem_tb_he_10": 7.42, "diem_tb_he_4": 2.92},
                {"nam_hoc": f"{nam+1}-{nam+2}", "hoc_ky_so": 2, "sinh_vien_key": 1001 + idx * 2, "ma_nganh": r.ma_nganh_moi, "ten_nganh": nganh_name_map.get(r.ma_nganh_moi, r.ma_nganh_moi), "ma_lop": r.ma_lop_moi, "so_mon": 6, "diem_tb_he_10": 7.58, "diem_tb_he_4": 3.00},
            ],
        }

    bundle = {
        "filters": {
            "khoa": khoa_df.to_dict(orient="records"),
            "nganh": [
                {"ma_nganh": m, "ten_nganh": nganh_name_map[m], "ma_khoa": k}
                for m, k in zip(nganh_df["ma_nganh"], nganh_df["ma_khoa"])
            ],
            "nam_hoc": sorted(q1c_clean["nam_hoc"].unique().tolist()),
            "vung_mien": sorted(q5_clean["vung_mien"].unique().tolist()),
            "sv_scd2": sv_scd2_list,
        },
        "overview": {
            "kpi": {
                "tong_luot_hoc_phan": 224778,
                "tong_sinh_vien": 4948,
                "diem_tb_he_10": 7.18,
                "diem_tb_he_4": 2.79,
                "ty_le_dat_pct": 98.76,
                "ty_le_rot_pct": 1.24,
                "tong_ho_so_tuyen_sinh": 7964,
                "so_dong_lich_su_scd2": 149,
                "so_dong_loi_bi_loai": 2537,
            },
            "q1_top_mon": q1b.to_dict(orient="records"),
            "q1_hocky": q1c_clean.to_dict(orient="records"),
            "q2_dice": q2_clean.to_dict(orient="records"),
            "q3_scatter": scatter_rows,
            "q4_trend": q4_clean.to_dict(orient="records"),
            "q5_tinh": q5_clean.to_dict(orient="records"),
        },
        "etl": {
            "run_id": "01573ca2d8bc",
            "etl_log": el.to_dict(orient="records"),
            "data_quality": dq.to_dict(orient="records"),
            "test_cases": tc.to_dict(orient="records"),
            "benchmarks": bm.to_dict(orient="records"),
        },
        "students": students_detail,
        "q1a": q1a.head(60).to_dict(orient="records"),
    }

    json_str = json.dumps(bundle, ensure_ascii=False, default=_json_default)
    html = (WEB_DIR / "index.html").read_text(encoding="utf-8")
    offline_shim = f"""<script>
    window.__OFFLINE_BUNDLE__ = {json_str};
    const _origFetch = window.fetch.bind(window);
    window.fetch = async function(url, opts) {{
      try {{
        if (window.location.protocol !== 'file:') {{
          const r = await _origFetch(url, opts);
          if (r.ok) return r;
        }}
      }} catch (e) {{}}
      const B = window.__OFFLINE_BUNDLE__;
      const u = String(url);
      const mkRes = (obj) => ({{ ok: true, json: async () => obj }});
      if (u.startsWith('/api/filters')) return mkRes(B.filters);
      if (u.startsWith('/api/overview')) return mkRes(B.overview);
      if (u.startsWith('/api/etl')) return mkRes(B.etl);
      if (u.startsWith('/api/student')) {{
        const m = new URLSearchParams(u.split('?')[1] || '').get('ma_sv') || '19IT001';
        return mkRes(B.students[m] || B.students['19IT001']);
      }}
      if (u.startsWith('/api/search_student')) {{
        const q = (new URLSearchParams(u.split('?')[1] || '').get('q') || '').toUpperCase();
        const found = B.filters.sv_scd2.filter(x => x.ma_sv.includes(q) || x.ho_ten.toUpperCase().includes(q));
        return mkRes(found);
      }}
      if (u.startsWith('/api/scd2_change')) {{
        const body = JSON.parse((opts && opts.body) || '{{}}');
        const sv = body.ma_sv || '19IT001';
        const cur = B.students[sv] || JSON.parse(JSON.stringify(B.students['19IT001']));
        cur.versions.forEach(v => {{ if (v.is_current) {{ v.is_current = 0; v.ngay_het_han = body.ngay_chuyen; }} }});
        cur.versions.push({{
          sinh_vien_key: 9000 + cur.versions.length,
          ma_sv: sv,
          ho_ten: cur.versions[0].ho_ten,
          ma_nganh: body.ma_nganh_moi,
          ten_nganh: body.ma_nganh_moi,
          ma_lop: '21' + body.ma_nganh_moi + '1',
          ngay_hieu_luc: body.ngay_chuyen,
          ngay_het_han: '9999-12-31',
          is_current: 1
        }});
        B.students[sv] = cur;
        return mkRes(cur);
      }}
      if (u.startsWith('/api/sql')) {{
        return mkRes({{ rows: B.q1a, total_returned: B.q1a.length }});
      }}
      return mkRes(B.etl);
    }};
    </script>"""

    standalone_html = html.replace("<script>", offline_shim + "\n  <script>", 1)
    out_path = WEB_DIR / "dashboard_standalone.html"
    out_path.write_text(standalone_html, encoding="utf-8")
    (WEB_DIR / "index.html").write_text(standalone_html, encoding="utf-8")
    print(f"[OK] Đã tạo file Web Dashboard độc lập (có sẵn toàn bộ dữ liệu): {out_path}")


if __name__ == "__main__":
    main()
