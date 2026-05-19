import os
import re
import json
import asyncio
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from markdownify import markdownify as md
from playwright.async_api import async_playwright

START_URLS = [
    "https://dhanhq.co/docs/DhanHQ-py/",
    "https://dhanhq.co/docs/v2/"
]

OUTPUT_DIR = "dhan_docs"

visited = set()
all_pages = []

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/raw_html", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/markdown", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/txt", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/combined", exist_ok=True)


def clean_filename(url):
    parsed = urlparse(url)
    path = parsed.path.strip("/")

    if not path:
        path = "index"

    path = path.replace("/", "_")

    return re.sub(r'[^a-zA-Z0-9_\-]', '_', path)


def extract_main_content(html):
    soup = BeautifulSoup(html, "lxml")

    # Remove junk
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # Try common documentation selectors
    selectors = [
        "main",
        "article",
        ".content",
        ".markdown",
        ".theme-doc-markdown",
        ".docs-content",
        ".doc-content"
    ]

    for selector in selectors:
        section = soup.select_one(selector)
        if section:
            return str(section)

    return str(soup.body)


async def get_all_links(page, base_url):
    links = await page.eval_on_selector_all(
        "a",
        """elements => elements.map(e => e.href)"""
    )

    valid_links = []

    for link in links:
        if not link:
            continue

        if link.startswith(base_url):
            valid_links.append(link.split("#")[0])

    return list(set(valid_links))


async def crawl_page(browser, url, base_domain):
    if url in visited:
        return

    visited.add(url)

    print(f"Crawling: {url}")

    page = await browser.new_page()

    try:
        await page.goto(url, wait_until="networkidle", timeout=60000)

        html = await page.content()

        filename = clean_filename(url)

        # Save raw HTML
        with open(f"{OUTPUT_DIR}/raw_html/{filename}.html", "w", encoding="utf-8") as f:
            f.write(html)

        # Extract meaningful content
        main_content = extract_main_content(html)

        markdown = md(main_content)

        text = BeautifulSoup(main_content, "lxml").get_text("\n")

        # Save markdown
        with open(f"{OUTPUT_DIR}/markdown/{filename}.md", "w", encoding="utf-8") as f:
            f.write(markdown)

        # Save txt
        with open(f"{OUTPUT_DIR}/txt/{filename}.txt", "w", encoding="utf-8") as f:
            f.write(text)

        all_pages.append({
            "url": url,
            "file": filename
        })

        # Discover more links
        links = await get_all_links(page, base_domain)

        for link in links:
            if link not in visited:
                await crawl_page(browser, link, base_domain)

    except Exception as e:
        print(f"Failed: {url}")
        print(e)

    finally:
        await page.close()


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for start_url in START_URLS:
            parsed = urlparse(start_url)
            base_domain = f"{parsed.scheme}://{parsed.netloc}"

            await crawl_page(browser, start_url, base_domain)

        await browser.close()

    # Combine all markdown
    combined_md = ""

    for page in all_pages:
        file = page["file"]
        url = page["url"]

        path = f"{OUTPUT_DIR}/markdown/{file}.md"

        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                combined_md += f"\n\n# SOURCE: {url}\n\n"
                combined_md += f.read()

    with open(f"{OUTPUT_DIR}/combined/dhan_all_docs.md", "w", encoding="utf-8") as f:
        f.write(combined_md)

    # Combine all txt
    combined_txt = ""

    for page in all_pages:
        file = page["file"]
        url = page["url"]

        path = f"{OUTPUT_DIR}/txt/{file}.txt"

        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                combined_txt += f"\n\nSOURCE: {url}\n\n"
                combined_txt += f.read()

    with open(f"{OUTPUT_DIR}/combined/dhan_all_docs.txt", "w", encoding="utf-8") as f:
        f.write(combined_txt)

    # Metadata
    with open(f"{OUTPUT_DIR}/metadata.json", "w", encoding="utf-8") as f:
        json.dump(all_pages, f, indent=2)

    print("\nDONE")
    print(f"Pages crawled: {len(all_pages)}")


if __name__ == "__main__":
    asyncio.run(main())