<img width="561" height="291" alt="image" src="https://github.com/user-attachments/assets/fe6b5b32-c589-4aed-8fff-a5aa650c2194" />
# Tinh nang

- **Hieu suat cao:** Su dung `asyncio` va `aiohttp` de thuc hien cac request giup tang toc do thu thap du lieu dang ke.
- **Quan ly Checkpoint:** Tu dong chia nho du lieu thanh cac phin (chunk) 1000 san pham moi file va bo qua cac phan da cào thanh cong neu chay lai.
- **Kiem soat tien trinh (PID):** Su dung file `crawler.pid` de ngan chan tinh trang chay trung lap nhieu tien cung mot luc.
- **Xu ly va duyet lai loi:** Gom cac ID loi vao file rieng (`danh_sach_loi.json`) va tu dong thuc hien duyet lai de vot vat du lieu o cuoi tien trinh.
- **Kiem tra du lieu (Audit):** Tu dong quet va lam sach cac file JSON ket qua de loai bo cac ban ghi bi thieu thong tin.

---

# Cau truc thu muc du an

```text
Project02/
│
├── venv/                     # Moi truong ao Python
├── tiki_data_output/         # Thu muc chua cac file ket qua JSON (1000 san pham/file)
├── main.py                   # Ma nguon chinh cua chuong trinh
├── product_ids.csv           # File dau vao chua danh sach Product ID cua Tiki
├── danh_sach_loi.json        # File luu tru cac ID gap loi trong qua trinh cao
└── crawler.pid               # File quan ly tien trinh chay
=======
>>>>>>> Stashed changes
