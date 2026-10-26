import asyncio
import random
from src.config import API_URL, SO_LAN_THU_LAI
from src.cleaner import phan_tich_san_pham
# crawl sp
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