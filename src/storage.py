import json
import os
import pandas as pd
import asyncio
from src.config import FILE_CSV, THU_MUC_OUTPUT, FILE_LOI, FILE_PID
from src.crawler import tai_san_pham

def quan_ly_pid():
    if os.path.exists(FILE_PID):
        try:
            with open(FILE_PID, "r") as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, 0)
        except (OSError, ValueError):
            pass
    with open(FILE_PID, "w") as f:
        f.write(str(os.getpid()))

def xoa_pid():
    if os.path.exists(FILE_PID):
        try:
            os.remove(FILE_PID)
        except:
            pass

def doc_danh_sach_id():
    if not os.path.exists(FILE_CSV):
        return []
    df = pd.read_csv(FILE_CSV, sep=None, engine="python")
    cot_id = next((c for c in df.columns if "id" in str(c).lower()), df.columns[0])
    ids = df[cot_id].dropna().astype(str).str.strip().tolist()
    return list(dict.fromkeys([i for i in ids if i.isdigit()]))

def luu_json_an_toan(duong_dan, obj):
    tmp = duong_dan + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, duong_dan)

async def xu_ly_va_duyet_lai_loi(session, sem):
    if not os.path.exists(FILE_LOI):
        return
    with open(FILE_LOI, "r", encoding="utf-8") as f:
        danh_sach_loi = json.load(f)
    if not danh_sach_loi:
        return

    tasks = [tai_san_pham(session, sem, pid) for pid in danh_sach_loi]
    ket_qua = await asyncio.gather(*tasks)

    phuc_hoi = []
    van_loi = []
    for trang_thai, ket_qua_item in ket_qua:
        if trang_thai == "thanh_cong":
            phuc_hoi.append(ket_qua_item)
        else:
            van_loi.append(ket_qua_item)

    if phuc_hoi:
        files = [os.path.join(THU_MUC_OUTPUT, f) for f in os.listdir(THU_MUC_OUTPUT) if f.startswith("tiki_products_part_")]
        if files:
            files.sort(key=os.path.getmtime)
            file_cuoi = files[-1]
            try:
                with open(file_cuoi, "r", encoding="utf-8") as f:
                    data_cu = json.load(f)
                data_cu.extend(phuc_hoi)
                luu_json_an_toan(file_cuoi, data_cu)
            except Exception:
                pass

    luu_json_an_toan(FILE_LOI, van_loi)

def kiem_tra_file_dung():
    if not os.path.exists(THU_MUC_OUTPUT):
        return
    for file_name in os.listdir(THU_MUC_OUTPUT):
        if not file_name.endswith(".json"):
            continue
        file_path = os.path.join(THU_MUC_OUTPUT, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                items = json.load(f)
            items_hop_le = []
            co_loi = False
            for item in items:
                if isinstance(item, dict) and item.get("id") and item.get("name"):
                    items_hop_le.append(item)
                else:
                    co_loi = True
            if co_loi:
                luu_json_an_toan(file_path, items_hop_le)
        except Exception:
            pass