import re
import sys
import urllib.request

import modal # host code on Modal serverless platform

app = modal.App(name="weblink-scraper")

"""
    Custom containers

    Playwright - used to launch a headless Chromium browser.  Interprets any JS on a webpage.
    modal.Image - pre-bundled image - `modal.Image.debian_slim`

"""
playwright_image = modal.Image.debian_slim(python_version="3.10").run_commands(
    "apt-get update",
    "apt-get install -y software-properties-common",
    "apt-add-repository non-free",
    "apt-add-repository contrib",
    "pip install playwright==1.30.0",
    "playwright install-deps chromium",
    "playwright install chromium",
)

@app.function(image=playwright_image)
async def get_links(cur_url: str):
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # scrape links on webpage
        await page.goto(cur_url)
        links = await page.eval_on_selector_all("a[href]", "elements => elements.map(element => element.href)")

        # close session
        await browser.close()

    print("Links", links)

    return links

"""
    Deploy App: Schedule App Deployments

    Simulate a list of websites to crawl.  In a more realistic architecture,
    this would be a dynamically generated list.
"""
@app.function(schedule=modal.Period(days=5))
def daily_scrape():
    urls = ["https://modal.com", "https://github.com", "https://www.ai.engineer/worldsfair/2024/schedule"]

    for links in get_links.map(urls):
        for link in links:
            print(links)


"""
    Scaling out

    Update our script to fetch a large list of links in parallel.
"""
@app.local_entrypoint()
def main():
    urls = ["https://modal.com", "https://github.com"]

    for links in get_links.map(urls):
        for link in links:
            print(links)
