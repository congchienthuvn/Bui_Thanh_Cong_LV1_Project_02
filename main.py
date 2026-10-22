import asyncio
import html
import json
import os
import random
import re
import time
import unicodedata
import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

#Config
FILE_CSV = "product_ids.csv"
THU_MUC_OUTPUT = "tiki_data_output"
FILE_LOI = "danh_sach_loi.json"
FILE_PID = "crawler.pid"

KICH_THUOC_CHUNK = 1000
GIOI_HAN_DONG_THOI = 10
SO_LAN_THU_LAI = 3

API_URL = "https://tiki.vn/api/v2/products/{}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
    "Referer": "https://tiki.vn/",
    "X-Client-Source": "pdp",
}


#PID
def quan_ly_pid():
    if os.path.exists(FILE_PID):
        try:
            with open(FILE_PID, "r") as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, 0)
            print(f"Canh bao: Tien trinh cu (PID: {old_pid}) co the van dang chay.")
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
# lấy ds id
def doc_danh_sach_id():
    if not os.path.exists(FILE_CSV):
        print(f"Khong tim thay file {FILE_CSV}.")
        return []
    df = pd.read_csv(FILE_CSV, sep=None, engine="python")
    cot_id = next((c for c in df.columns if "id" in str(c).lower()), df.columns[0])
    ids = df[cot_id].dropna().astype(str).str.strip().tolist()
    return list(dict.fromkeys([i for i in ids if i.isdigit()]))

KY_TU_DAC_BIET = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")
def lam_sach_mo_ta(raw):
    if not raw:
        return ""
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    for tag in soup.find_all(["br", "p", "li", "div", "tr"]):
        tag.append(" ")
    text = html.unescape(soup.get_text(separator=" "))
    text = unicodedata.normalize("NFC", text)
    text = KY_TU_DAC_BIET.sub("", text).replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()

def phan_tich_san_pham(data):
    if not isinstance(data, dict) or not data.get("id"):
        return None
    hinh_anh = [
        img.get("base_url") or img.get("large_url") or img.get("thumbnail_url")
        for img in (data.get("images") or []) if isinstance(img, dict)
    ]
    hinh_anh = [u for u in hinh_anh if u]
    if not hinh_anh and data.get("thumbnail_url"):
        hinh_anh.append(data["thumbnail_url"])

    return {
        "id": data.get("id"),
        "name": data.get("name"),
        "url_key": data.get("url_key"),
        "price": data.get("price"),
        "description": lam_sach_mo_ta(data.get("description", "")),
        "images_url": hinh_anh,
    }


# api
async def tai_san_pham(session, sem, pid):
    url = API_URL.format(pid)
    for lan_thu in range(SO_LAN_THU_LAI):
        try:
            async with sem:
                await asyncio.sleep(random.uniform(2.0, 4.0))
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json(content_type=None)
                        item = phan_tich_san_pham(data)
                        if item:
                            return "thanh_cong", item
                        return "loi_du_lieu", pid
                    elif resp.status == 404:
                        return "khong_tim_thay", pid
                    elif resp.status in (429, 403):
                        await asyncio.sleep(15 * (lan_thu + 1))
                    else:
                        await asyncio.sleep(2 ** lan_thu)
        except Exception:
            await asyncio.sleep(2 ** lan_thu)
    return "that_bai", pid

def luu_json_an_toan(duong_dan, obj):
    tmp = duong_dan + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, duong_dan)


# duyet lai loi
async def xu_ly_va_duyet_lai_loi(session, sem):
    if not os.path.exists(FILE_LOI):
        return
    with open(FILE_LOI, "r", encoding="utf-8") as f:
        danh_sach_loi = json.load(f)
    if not danh_sach_loi:
        return

    print(f"Bat dau duyet lai {len(danh_sach_loi)} ID loi...")
    tasks = [tai_san_pham(session, sem, pid) for pid in danh_sach_loi]
    ket_qua = await asyncio.gather(*tasks)

    phuc_hoi = []
    van_loi = []
    for trang_thai, ket_qua_item in ket_qua:
        if trang_thai == "thanh_cong":
            phuc_hoi.append(ket_qua_item)
        else:
            van_loi.append(ket_qua_item)
    # Ghi vao file chunk cuoi cung neu phuc hoi duoc
    if phuc_hoi:
        files = [os.path.join(THU_MUC_OUTPUT, f) for f in os.listdir(THU_MUC_OUTPUT) if
                 f.startswith("tiki_products_part_")]
        if files:
            files.sort(key=os.path.getmtime)
            file_cuoi = files[-1]
            try:
                with open(file_cuoi, "r", encoding="utf-8") as f:
                    data_cu = json.load(f)
                data_cu.extend(phuc_hoi)
                luu_json_an_toan(file_cuoi, data_cu)
                print(f"Da phuc hoi thanh cong {len(phuc_hoi)} san pham vao file {file_cuoi}")
            except Exception:
                pass

    luu_json_an_toan(FILE_LOI, van_loi)
    print(f"Duyet lai xong. Con lai {len(van_loi)} san pham loi thuc su.")

# kt file
def kiem_tra_file_dung():
    if not os.path.exists(THU_MUC_OUTPUT):
        return
    print("Bat dau kiem tra cac file ket qua da luu...")
    so_file_sua = 0
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
                so_file_sua += 1
                print(f"Da lam sach file {file_name} do chua ban ghi loi.")
        except Exception:
            pass
    print(f"Hoan tat kiem tra file. Da xu ly {so_file_sua} file co van de.")
async def main():
    quan_ly_pid()
    try:
        danh_sach_id = doc_danh_sach_id()
        if not danh_sach_id:
            return
        print(f"Tong so Product ID can cao: {len(danh_sach_id)}")
        os.makedirs(THU_MUC_OUTPUT, exist_ok=True)
        chunks = [danh_sach_id[i:i + KICH_THUOC_CHUNK] for i in range(0, len(danh_sach_id), KICH_THUOC_CHUNK)]

        tat_ca_loi = []
        if os.path.exists(FILE_LOI):
            try:
                with open(FILE_LOI, "r", encoding="utf-8") as f:
                    tat_ca_loi = json.load(f)
            except:
                pass

        connector = aiohttp.TCPConnector(limit=GIOI_HAN_DONG_THOI, ttl_dns_cache=300)
        sem = asyncio.Semaphore(GIOI_HAN_DONG_THOI)
        bat_dau = time.time()

        async with aiohttp.ClientSession(connector=connector, headers=HEADERS) as session:
            for idx, ids in enumerate(chunks, start=1):
                file_path = os.path.join(THU_MUC_OUTPUT, f"tiki_products_part_{idx}.json")
                if os.path.exists(file_path):
                    print(f"[{idx}/{len(chunks)}] Da ton tai checkpoint, bo qua.")
                    continue
                print(f"Dang xu ly phan {idx}/{len(chunks)} ({len(ids)} IDs)...")
                tasks = [tai_san_pham(session, sem, pid) for pid in ids]
                ket_qua = await asyncio.gather(*tasks)

                san_pham_hop_le = []
                for trang_thai, ket_qua_item in ket_qua:
                    if trang_thai == "thanh_cong":
                        san_pham_hop_le.append(ket_xlsx := ket_qua_item)  # safe assignment
                    else:
                        if ket_qua_item not in tat_ca_loi:
                            tat_ca_loi.append(ket_qua_item)

                luu_json_an_toan(file_path, san_pham_hop_le)
                luu_json_an_toan(FILE_LOI, list(set(tat_ca_loi)))
                print(f"Hoàn thành phần {idx}. Thanh cong: {len(san_pham_hop_le)}/{len(ids)}")

            # Sau khi cao xong het, tien hành duyet lai danh sach loi va kiem tra file dung
            await xu_ly_va_duyet_lai_loi(session, sem)
        kiem_tra_file_dung()
        print(f"\nHoan thanh. Tong thoi gian: {(time.time() - bat_dau) / 60:.1f} phut.")
    finally:
        xoa_pid()
if __name__ == "__main__":
    asyncio.run(main())