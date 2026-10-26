# Data Pipeline & Web Scraper

## Overview

A robust, production-grade asynchronous ETL pipeline engineered for extracting, transforming, and loading (ETL) large-scale product catalogs from e-commerce platforms (Tiki). Built with a core focus on extreme concurrency, fault tolerance, atomic file transactions, and strict rate-limiting to process millions of records reliably in resource-constrained environments.

---

## Architecture & Core Features

* **Asynchronous Concurrency Engine**: Leverages Python's `asyncio` and `aiohttp` to manage thousands of non-blocking HTTP requests within a single-threaded event loop, maximizing network throughput without CPU overhead.
* **Controlled Concurrency (`Semaphore`)**: Implements strict rate-limiting via semaphores to prevent local resource exhaustion and evade automated anti-bot triggers (HTTP 429/403).
* **Idempotent Partitioned Checkpointing**: Automatically segments massive datasets into structured chunks and skips pre-existing partitions, allowing seamless pipeline resumability after interruptions.
* **Multi-Tier Fault Tolerance & Exponential Backoff**: Features automated retry policies with exponential backoff delays and a dedicated dead-letter queue (`danh_sach_loi.json`) to isolate permanently failed payloads.
* **Atomic File Persistence**: Utilizes atomic write strategies (staging to `.tmp` files followed by `os.replace`) to completely eliminate data corruption risks during sudden process terminations or power failures.
* **Advanced Data Sanitization**: Strips malicious HTML structures, normalizes Unicode strings to NFC standard, and removes zero-width/hidden whitespace characters using compiled Regular Expressions and BeautifulSoup.

---

## Project Structure

```text
tiki-async-crawler/
│
├── data/                    # Input dataset storage
│   └── product_ids.csv      # Source product IDs repository
│
├── output/                  # Partitioned JSON chunks & dead-letter queue
│
├── src/                     # Core application modules
│   ├── __init__.py          # Package initializer
│   ├── config.py            # Global pipeline configurations
│   ├── cleaner.py           # HTML parsing and data sanitization logic
│   ├── crawler.py           # Async HTTP worker & retry orchestration
│   └── storage.py           # PID locking, chunking, and file validation
│
├── requirements.txt         # Project dependencies
├── main.py                  # Pipeline orchestration entry point
└── README.md                # Project documentation