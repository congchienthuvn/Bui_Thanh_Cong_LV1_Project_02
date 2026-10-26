import os

FILE_CSV = "data/product_ids.csv"
THU_MUC_OUTPUT = "output"
FILE_LOI = "output/danh_sach_loi.json"
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