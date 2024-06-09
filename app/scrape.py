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

@app.local_entrypoint()
def main(url):
    links = get_links.remote(url)

    print(links)
