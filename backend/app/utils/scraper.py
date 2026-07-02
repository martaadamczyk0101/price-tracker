import json
import random
import time

import undetected_chromedriver as uc
from pyvirtualdisplay import Display
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from backend.app.utils.price_parser import parse_price
from backend.app.utils.selectors import SELECTORS

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


def get_product_info(url):
    store_base = next(
        (base for base in SELECTORS if url.startswith(base)), None
    )

    if store_base is None:
        raise ValueError(f"Unsupported shop for URL: {url}")

    price_selectors = SELECTORS[store_base]["price"]
    title_selectors = SELECTORS[store_base]["title"]
    image_selectors = SELECTORS[store_base].get("image", [])

    display = Display(visible=False, size=(1920, 1080))
    display.start()

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"--user-agent={random.choice(_USER_AGENTS)}")
    options.binary_location = "/usr/bin/chromium"

    driver = uc.Chrome(
        options=options,
        driver_executable_path="/usr/bin/chromedriver",
        version_main=149,
    )

    try:
        driver.get(url)
        time.sleep(random.uniform(2.0, 4.0))

        price_value = None
        for selector in price_selectors:
            deadline = time.time() + 15
            while time.time() < deadline:
                try:
                    els = driver.find_elements(By.CSS_SELECTOR, selector)
                    if els:
                        text = els[0].text.replace("\xa0", "").strip()
                        if text:
                            price_value = parse_price(text)
                            break
                except Exception:
                    pass
                time.sleep(0.5)
            if price_value is not None:
                break

        title_value = "Unknown product"
        for selector in title_selectors:
            deadline = time.time() + 15
            while time.time() < deadline:
                try:
                    els = driver.find_elements(By.CSS_SELECTOR, selector)
                    if els:
                        text = els[0].text.strip()
                        if text:
                            title_value = text
                            break
                except Exception:
                    pass
                time.sleep(0.5)
            if title_value != "Unknown product":
                break

        image_value = None
        for selector in image_selectors:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                sources = driver.execute_script("""
                    return Array.from(document.querySelectorAll(arguments[0])).map(function(img) {
                        var dataLg = img.getAttribute('data-lgimg');
                        if (dataLg) {
                            try { var p = JSON.parse(dataLg); if (p.url) return p.url; } catch(e) {}
                        }
                        return img.getAttribute('content') || img.getAttribute('src') || img.getAttribute('data-src') || '';
                    });
                """, selector)
                for src in (sources or []):
                    if src and src.startswith("http"):
                        image_value = src
                        break
                if image_value:
                    break
            except Exception:
                continue

        return price_value, title_value, image_value

    finally:
        driver.quit()
        display.stop()
