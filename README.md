# Tiki Async Crawler — ETL Pipeline

An asynchronous Python ETL pipeline for extracting, transforming, and storing product catalog data from Tiki.

## Tech Stack

- **Core:** Python, `asyncio`, `aiohttp`
- **Data Processing:** `pandas`, BeautifulSoup4, Regular Expressions
- **Fault Tolerance:** Exponential backoff, PID-based process locking, atomic file writes, Dead-Letter Queue (DLQ)
- **Deployment:** Docker, Docker Compose, Apache Airflow (planned integration)

## Project Structure

```text
tiki-async-crawler/
├── data/
│   └── product_ids.csv
├── output/
│   ├── tiki_products_part_1.json
│   └── danh_sach_loi.json
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── cleaner.py
│   ├── crawler.py
│   └── storage.py
├── requirements.txt
├── main.py
└── README.md
```

## Data Schema

**Input:** `data/product_ids.csv` — source file containing product IDs.

**Output:** Partitioned JSON files containing up to 1,000 product records each.

| Field | Type | Description |
|---|---|---|
| `id` | Integer / String | Unique product ID |
| `name` | String | Product title |
| `url_key` | String | Product URL slug |
| `price` | Float / Object | Product pricing information |
| `description` | String | Cleaned, plain-text description |
| `images_url` | List | Product image URLs |

**API Endpoint:** `https://tiki.vn/api/v2/products/{product_id}`

## Key Features

- **Asynchronous Crawling:** Concurrent HTTP requests using `asyncio` and `aiohttp`.
- **Concurrency Control:** Configurable semaphore and randomized delays.
- **Automatic Retries:** Exponential backoff for transient failures, including HTTP 429 and network errors.
- **Data Cleaning:** HTML sanitization, whitespace normalization, and Unicode NFC normalization.
- **Image Extraction:** Extracts image URLs from multiple fallback fields.
- **Atomic File Writes:** Uses temporary files and `os.replace()` to reduce the risk of corrupted output.
- **Checkpointing:** Skips completed partitions to support pipeline resumption.
- **Dead-Letter Queue:** Stores failed product IDs in `output/danh_sach_loi.json` for subsequent retries.
- **Chunked Storage:** Splits product records into manageable JSON files.

## ETL Workflow

1. **Extract:** Load, validate, and deduplicate product IDs from the source CSV.
2. **Transform:** Fetch product data and normalize descriptions, images, and other fields.
3. **Load:** Save processed records into partitioned JSON files using atomic writes.
4. **Recover:** Retry failed product IDs through the dead-letter queue recovery process `xu_ly_va_duyet_lai_loi`.

## Configuration

Pipeline parameters are defined in `src/config.py`.

| Parameter | Default | Description |
|---|---:|---|
| `KICH_THUOC_CHUNK` | `1000` | Maximum records per JSON partition |
| `GIOI_HAN_DONG_THOI` | `10` | Maximum concurrent HTTP requests |
| `SO_LAN_THU_LAI` | `3` | Maximum retry attempts |

## Installation & Usage

```bash
git clone <YOUR_REPOSITORY_URL>
cd tiki-async-crawler
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Replace `<YOUR_REPOSITORY_URL>` with your repository URL.

**Note:** Request concurrency and retry delays should be configured responsibly. HTTP 403/429 responses may still occur depending on API access policies and rate limits.