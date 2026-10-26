import html
import re
import unicodedata
from bs4 import BeautifulSoup

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