Async Web Scraper
==================
An asynchronous web scraping tool using Python's httpx and selectolax.

Features:
- Async I/O for high concurrency
- HTML parsing with CSS selectors
- Basic rate limiting and error handling
- CSV export of results
- Reads target URLs from file

Installation & Run:
-------------------
pip install -r requirements.txt
python scrape.py --urls urls.txt --selector "title" --out results.csv

Purpose:
--------
Demonstrates concurrency, networking, and parsing — useful for data collection and automation tasks.
