import asyncio
import json
import os
import time
import aiohttp
from src.config import THU_MUC_OUTPUT, FILE_LOI, KICH_THUOC_CHUNK, GIOI_HAN_DONG_THOI, HEADERS
from src.storage import quan_ly_pid, xoa_pid, doc_danh_sach_id, luu_json_an_toan, xu_ly_va_duyet_lai_loi, kiem_tra_file_dung
from src.crawler import tai_san_pham
# main
async def main():
    quan_ly_pid()
    try:
        danh_sach_id = doc_danh_sach_id()
        if not danh_sach_id:
            return
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
                    continue
                tasks = [tai_san_pham(session, sem, pid) for pid in ids]
                ket_qua = await asyncio.gather(*tasks)

                san_pham_hop_le = []
                for trang_thai, ket_qua_item in ket_qua:
                    if trang_thai == "thanh_cong":
                        san_pham_hop_le.append(ket_qua_item)
                    else:
                        if ket_qua_item not in tat_ca_loi:
                            tat_ca_loi.append(ket_qua_item)

                luu_json_an_toan(file_path, san_pham_hop_le)
                luu_json_an_toan(FILE_LOI, list(set(tat_ca_loi)))

            await xu_ly_va_duyet_lai_loi(session, sem)
        kiem_tra_file_dung()
    finally:
        xoa_pid()
if __name__ == "__main__":
    asyncio.run(main())