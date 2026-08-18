import glob
import os
import platform
import random
import subprocess
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from backend.app.utils.price_parser import parse_price
from backend.app.utils.selectors import SELECTORS

_IS_LINUX = platform.system() == "Linux"

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

_display = None


def init_display():
    global _display
    if not _IS_LINUX:
        return
    from pyvirtualdisplay import Display

    subprocess.run(["pkill", "-9", "Xvfb"], capture_output=True)
    for lock in glob.glob("/tmp/.X*-lock"):
        try:
            os.remove(lock)
        except OSError:
            pass

    _display = Display(visible=False, size=(1920, 1080))
    _display.start()
    print("Xvfb display started", flush=True)


def stop_display():
    global _display
    if _display is not None:
        try:
            _display.stop()
        except Exception:
            pass
        _display = None
        print("Xvfb display stopped", flush=True)


def get_product_info(url):
    store_base = next(
        (base for base in SELECTORS if url.startswith(base)), None
    )

    if store_base is None:
        raise ValueError(f"Unsupported shop for URL: {url}")

    price_selectors = SELECTORS[store_base]["price"]
    title_selectors = SELECTORS[store_base]["title"]
    image_selectors = SELECTORS[store_base].get("image", [])

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"--user-agent={random.choice(_USER_AGENTS)}")

    if _IS_LINUX:
        options.binary_location = "/usr/bin/chromium"
        driver = uc.Chrome(
            options=options,
            driver_executable_path="/usr/bin/chromedriver",
            version_main=149,
        )
    else:
        driver = uc.Chrome(options=options)

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
                _bad = ("doodle", "logo", "banner", "sprite", ".svg", "placeholder")
                for src in (sources or []):
                    if src and src.startswith("http") and not any(b in src.lower() for b in _bad):
                        image_value = src
                        break
                if image_value:
                    break
            except Exception:
                continue

        return price_value, title_value, image_value

    finally:
        _quit_driver(driver)


def _quit_driver(driver):
    try:
        driver.quit()
    except Exception:
        pass

    # undetected_chromedriver's quit() only kills the chromedriver
    # process without waiting on it, leaking the process's stdin/
    # stdout/stderr pipes (and the zombie itself) in this process
    # until Python happens to garbage-collect the Popen object. Under
    # sustained scraping this exhausts the open-file limit, so reap
    # it explicitly here.
    proc = getattr(getattr(driver, "service", None), "process", None)
    if proc is None:
        return
    for stream in (proc.stdin, proc.stdout, proc.stderr):
        if stream is not None:
            try:
                stream.close()
            except Exception:
                pass
    try:
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
            proc.wait(timeout=5)
        except Exception:
            pass
