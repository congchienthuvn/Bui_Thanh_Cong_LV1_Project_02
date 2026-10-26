# High-Performance Asynchronous Data Pipeline & Web Scraper for E-Commerce

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![AsyncIO](https://img.shields.io/badge/AsyncIO-Concurrency-orange?style=for-the-badge)
![Aiohttp](https://img.shields.io/badge/Aiohttp-Async%20HTTP-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

</div>

## Overview

A robust, production-grade asynchronous ETL pipeline designed for extracting, transforming, and loading (ETL) large-scale product catalogs from e-commerce APIs (Tiki). Built with a focus on fault tolerance, concurrency control, and atomic file operations to handle millions of records reliably in distributed or resource-constrained environments.

---

## Architecture & Core Features

* **Asynchronous I/O Engine**: Leverages `asyncio` and `aiohttp` to manage thousands of concurrent HTTP connections within a single-threaded event loop, maximizing network throughput without CPU overhead.
* **Concurrency Limiting (`Semaphore`)**: Implements strict rate-limiting to prevent server overload and evade automated rate-limit triggers (HTTP 429/403).
* **Idempotent Checkpointing**: Splits datasets into manageable chunks, automatically skipping previously processed partitions to support seamless resumability after interruptions.
* **Fault Tolerance & Exponential Backoff**: Multi-tier error handling mechanism featuring automatic retries with exponential backoff and a dedicated dead-letter queue (`danh_sach_loi.json`) for failed payloads.
* **Atomic File Persistence**: Utilizes atomic write operations (`.tmp` staging followed by `os.replace`) to eliminate data corruption risks during power outages or sudden process kills.
* **Data Sanitization & Normalization**: Strips malicious HTML tags, normalizes Unicode strings to NFC format, and strips zero-width/hidden characters using high-performance Regular Expressions and BeautifulSoup.

---

## Project Structure

```text
Project02/
│
├── data/                    # Input dataset storage
│   └── product_ids.csv      # Source product IDs
│
├── output/                  # Partitioned JSON outputs & dead-letter queue
│
├── src/                     # Core application modules
│   ├── config.py            # Global configuration constants
│   ├── cleaner.py           # HTML parsing and data sanitization
│   ├── crawler.py           # Async HTTP worker & retry logic
│   └── storage.py           # PID lock, chunking, and file validation
│
├── requirements.txt         # Project dependencies
├── main.py                  # Pipeline orchestration entry point
└── README.md                # Project documentation