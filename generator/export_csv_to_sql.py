import pandas as pd
import os

df_khoa = pd.read_csv('data/Khoa.csv')
df_nganh = pd.read_csv('data/Nganh.csv')
df_gv = pd.read_csv('data/GiangVien.csv')
df_mon = pd.read_csv('data/MonHoc.csv')
df_sv = pd.read_csv('data/SinhVien.csv')

df_nganh = df_nganh.merge(df_khoa, on='ma_khoa', how='left')
df_gv = df_gv.merge(df_khoa, on='ma_khoa', how='left')
df_mon = df_mon.merge(df_khoa, on='ma_khoa', how='left')
df_sv = df_sv.merge(df_nganh[['ma_nganh', 'ten_nganh']], on='ma_nganh', how='left')

lines = []
lines.append("USE edu_dw;")
lines.append("GO\n")

# 1. GiangVien (118 rows)
lines.append("-- 1. NAP DIM_GIANG_VIEN (118 giang vien)")
for _, r in df_gv.iterrows():
    ma_gv = r['ma_gv']
    ho_ten = str(r['ho_ten']).replace("'", "''")
    hoc_vi = str(r['hoc_vi']).replace("'", "''")
    ten_khoa = str(r['ten_khoa']).replace("'", "''")
    lines.append(f"IF NOT EXISTS (SELECT 1 FROM dim_giang_vien WHERE ma_gv = '{ma_gv}') INSERT INTO dim_giang_vien (ma_gv, ho_ten, hoc_vi, ten_khoa) VALUES ('{ma_gv}', N'{ho_ten}', N'{hoc_vi}', N'{ten_khoa}');")
lines.append("GO\n")

# 2. MonHoc (120 rows)
lines.append("-- 2. NAP DIM_MON_HOC (120 mon hoc)")
for _, r in df_mon.iterrows():
    ma_mon = r['ma_mon']
    ten_mon = str(r['ten_mon']).replace("'", "''")
    stc = int(r['so_tin_chi'])
    loai_mon = str(r['loai_mon']).replace("'", "''")
    ten_khoa = str(r['ten_khoa']).replace("'", "''")
    lines.append(f"IF NOT EXISTS (SELECT 1 FROM dim_mon_hoc WHERE ma_mon = '{ma_mon}') INSERT INTO dim_mon_hoc (ma_mon, ten_mon, so_tin_chi, loai_mon, ten_khoa) VALUES ('{ma_mon}', N'{ten_mon}', {stc}, N'{loai_mon}', N'{ten_khoa}');")
lines.append("GO\n")

# 3. Nganh (10 rows)
lines.append("-- 3. NAP DIM_NGANH (10 nganh)")
for _, r in df_nganh.iterrows():
    ma_nganh = r['ma_nganh']
    ten_nganh = str(r['ten_nganh']).replace("'", "''")
    ten_khoa = str(r['ten_khoa']).replace("'", "''")
    lines.append(f"IF NOT EXISTS (SELECT 1 FROM dim_nganh WHERE ma_nganh = '{ma_nganh}') INSERT INTO dim_nganh (ma_nganh, ten_nganh, ten_khoa) VALUES ('{ma_nganh}', N'{ten_nganh}', N'{ten_khoa}');")
lines.append("GO\n")

# 4. SinhVien (4,948 rows)
lines.append("-- 4. NAP DIM_SINH_VIEN (4948 sinh vien)")
values = []
for i, r in df_sv.iterrows():
    ma_sv = r['ma_sv']
    ho_ten = str(r['ho_ten']).replace("'", "''")
    gt = str(r['gioi_tinh']) if pd.notna(r['gioi_tinh']) else 'Nam'
    tt = str(r['tinh_thanh']).replace("'", "''") if pd.notna(r['tinh_thanh']) else 'Đà Nẵng'
    tn = str(r['ten_nganh']).replace("'", "''") if pd.notna(r['ten_nganh']) else 'Công nghệ thông tin'
    ml = str(r['ma_lop']) if pd.notna(r['ma_lop']) else '19IT1'
    values.append(f"('{ma_sv}', N'{ho_ten}', N'{gt}', N'{tt}', N'{tn}', '{ml}', '2019-09-01', '9999-12-31', 1)")
    if len(values) >= 500:
        val_str = ",\n".join(values)
        lines.append(f"INSERT INTO dim_sinh_vien (ma_sv, ho_ten, gioi_tinh, tinh_thanh, ten_nganh, ma_lop, ngay_hieu_luc, ngay_het_han, is_current)\nSELECT v.ma_sv, v.ho_ten, v.gioi_tinh, v.tinh_thanh, v.ten_nganh, v.ma_lop, v.ngay_hieu_luc, v.ngay_het_han, v.is_current FROM (VALUES\n{val_str}\n) AS v(ma_sv, ho_ten, gioi_tinh, tinh_thanh, ten_nganh, ma_lop, ngay_hieu_luc, ngay_het_han, is_current) WHERE NOT EXISTS (SELECT 1 FROM dim_sinh_vien WHERE ma_sv = v.ma_sv);\nGO\n")
        values = []

if values:
    val_str = ",\n".join(values)
    lines.append(f"INSERT INTO dim_sinh_vien (ma_sv, ho_ten, gioi_tinh, tinh_thanh, ten_nganh, ma_lop, ngay_hieu_luc, ngay_het_han, is_current)\nSELECT v.ma_sv, v.ho_ten, v.gioi_tinh, v.tinh_thanh, v.ten_nganh, v.ma_lop, v.ngay_hieu_luc, v.ngay_het_han, v.is_current FROM (VALUES\n{val_str}\n) AS v(ma_sv, ho_ten, gioi_tinh, tinh_thanh, ten_nganh, ma_lop, ngay_hieu_luc, ngay_het_han, is_current) WHERE NOT EXISTS (SELECT 1 FROM dim_sinh_vien WHERE ma_sv = v.ma_sv);\nGO\n")

out_path = os.path.join('sql', 'nap_du_lieu_tu_csv_sang_dw.sql')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines))

print(f"Đã tạo thành công file: {out_path} ({len(lines)} dòng)")

