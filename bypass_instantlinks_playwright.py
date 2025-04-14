# This script automates the process of extracting hidden form data
# and cookies from a webpage using Playwright, and then submits that data
# to another URL using the requests library.

# Specifically made to bypass the redirection of instantlinks.co

# Author: Lokesh Pandey

# DISCLAIMER: This script is for educational purposes only.
# Use responsibly and ethically.

# Ensure you have the required libraries installed:
# [pip install requests beautifulsoup4 playwright]

# Extra step to install Playwright browsers:
# [playwright install]

# Usage:
# [python bypass_instantlinks.py PATH_TO_LINK_WITHOUT_BASE_URL]

# Example:
# [python bypass_instantlinks.py 4TKpCv]


import argparse
from time import sleep
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright


def extract_hidden_form_data(html):
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form", {"id": "go-link"})

    if not form:
        raise ValueError("❌ Form with id='go-link' not found.")

    try:
        return {
            "_method": "POST",
            "_csrfToken": form.find("input", {"name": "_csrfToken"})["value"],
            "ad_form_data": form.find("input", {"name": "ad_form_data"})["value"],
            "_Token[fields]": form.find("input", {"name": "_Token[fields]"})["value"],
            "_Token[unlocked]": form.find("input", {"name": "_Token[unlocked]"})[
                "value"
            ],
        }
    except Exception as e:
        raise ValueError(f"⚠️ Error extracting form inputs: {e}")


def get_form_data_and_cookie_string(path: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print("🌐 Navigating to verify URL...")
        page.goto(
            "https://business.ndfrecruitment.com/verify/?https://instantlinks.co/"
            + path,
            wait_until="load",
        )
        page.wait_for_url("https://business.ndfrecruitment.com/", timeout=10000)

        page.evaluate(
            """
            const btn = document.querySelector('.second-button');
            if (btn && btn.getAttribute('onclick')) {
                eval(btn.getAttribute('onclick'));
            }
        """
        )

        page.wait_for_url("https://instantlinks.co/" + path, timeout=10000)
        print("🔄 Waiting for 5secs")
        # wait for 10 secs
        page.wait_for_timeout(10000)
        print("🔄 Waited done")

        final_url = page.url
        print(f"➡️ Redirected to: {final_url}")

        html = page.content()
        cookies = context.cookies()

        # Join cookies as string
        cookie_str = "; ".join(
            [
                f"{cookie['name']}={cookie['value']}"
                for cookie in cookies
                if "instantlinks.co" in cookie["domain"]
            ]
        )

        form_data_dict = extract_hidden_form_data(html)
        form_data_raw = urlencode(form_data_dict)

        browser.close()
        return form_data_raw, cookie_str


def get_ajax_headers(cookie_str: str):
    return {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9,ar-AE;q=0.8,ar;q=0.7,hi-IN;q=0.6,hi;q=0.5",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://instantlinks.co",
        "Referer": "https://instantlinks.co/SNBD",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "Cookie": cookie_str,
    }


def submit_form(form_data_raw: str, cookie_str: str):
    url = "https://instantlinks.co/links/go"

    print("Cookie string:", cookie_str)
    print("Form data:", form_data_raw)
    print("Submitting form...")
    headers = get_ajax_headers(cookie_str)

    response = requests.post(
        url,
        headers=headers,
        data=form_data_raw,
    )

    print(f"📡 Status: {response.status_code}")
    print("🧾 Response preview:", response.text[:500])
    return response


def main():
    parser = argparse.ArgumentParser(description="Bypass instantlinks.co redirection")
    parser.add_argument("path", help="Path part of the URL (e.g., 4TKpCv)")
    args = parser.parse_args()
    path = args.path
    print(f"🔗 Path: {path}")
    form_data_raw, cookie_str = get_form_data_and_cookie_string(path)
    submit_form(form_data_raw, cookie_str)


if __name__ == "__main__":
    main()
