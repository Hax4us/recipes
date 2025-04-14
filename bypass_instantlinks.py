# This script bypass the redirection of instantlinks.co links

# Author: Lokesh Pandey

# DISCLAIMER: This script is for educational purposes only.
# Use responsibly and ethically.

# Ensure you have the required libraries installed:
# [pip install requests beautifulsoup4]

# NOTE: You have to goto https://instantlinks.co/XYZ and open dev tools
# and then open network tab and then click on the link
# and just copy one cookie "app_visitor" and then pass that cookie to this script

# [bypass_instantlinks.py PATH_TO_LINK_WITHOUT_BASE_URL --cookies "app_visitor=YOUR_COOKIE; ab=2;"]

# Example:
# [bypass_instantlinks.py 4TKpCv --cookies "app_visitor=Q2FrZQ%3D%3D.NjAwZmNjM2RkYWU2YTA3NTY4ZjdiMj"]

from time import sleep
import requests
from bs4 import BeautifulSoup
import argparse
import sys
import traceback

import urllib


def get_html_headers(path: str = ""):
    return {
        "accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3;q=0.7"
        ),
        "accept-language": "en-US,en;q=0.9,ar-AE;q=0.8,ar;q=0.7,hi-IN;q=0.6,hi;q=0.5",
        "cache-control": "max-age=0",
        "priority": "u=0, i",
        "referer": "https://business.ndfrecruitment.com/",
        "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/135.0.0.0 Safari/537.36"
        ),
    }


def get_ajax_headers(path: str = ""):
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
    }


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


def parse_cookie_string(cookie_str):
    cookies = {}
    for pair in cookie_str.split(";"):
        if "=" in pair:
            key, value = pair.strip().split("=", 1)
            cookies[key] = value
    return cookies


def debug_log(message, verbose):
    if verbose:
        print(f"[DEBUG] {message}")


def main():
    parser = argparse.ArgumentParser(description="Bypass instantlinks.co redirection")
    parser.add_argument("path", help="Path part of the URL (e.g., /4TKpCv)")
    parser.add_argument(
        "--cookies",
        help='Custom cookies string like "key1=val1; key2=val2"',
        default=None,
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable detailed debug output"
    )
    args = parser.parse_args()

    base_url = "https://instantlinks.co"
    target_url = f"{base_url}/{args.path}"
    form_action_url = f"{base_url}/links/go"
    custom_cookies = parse_cookie_string(args.cookies) if args.cookies else {}

    try:
        with requests.Session() as session:
            # Step 1: Initial cookie fetch
            debug_log(
                f"Hitting base URL {base_url} to get session cookies", args.verbose
            )
            base_res = session.get(base_url, headers=get_html_headers(args.path))
            debug_log(f"Initial GET status: {base_res.status_code}", args.verbose)
            debug_log(f"Initial cookies: {session.cookies.get_dict()}", args.verbose)

            # Step 2: Inject user cookies if provided
            if custom_cookies:
                session.cookies.update(custom_cookies)
                print("🧁 Custom cookies applied!")

            debug_log(
                f"Session cookies after custom cookies: {session.cookies.get_dict()}",
                args.verbose,
            )

            # Step 3: Hit the shortlink
            debug_log(f"Hitting target URL {target_url}", args.verbose)
            res = session.get(target_url, headers=get_html_headers(args.path))
            debug_log(f"Shortlink GET status: {res.status_code}", args.verbose)
            res.raise_for_status()

            # Step 4: Parse form
            form_data = extract_hidden_form_data(res.text)
            print("🔍 Extracted Form Data:")
            for k, v in form_data.items():
                debug_log(f"{k}: {v[:60]}{'...' if len(v) > 60 else ''}", args.verbose)

            # Step 5: Submit form
            debug_log(f"POSTing to {form_action_url} with form data", args.verbose)

            raw_body = urllib.parse.urlencode(form_data, doseq=True)

            debug_log(f"Raw form body:\n{raw_body}", args.verbose)

            # Prepare final headers (add raw cookie header manually)
            ajax_headers = get_ajax_headers(args.path)

            debug_log(
                f"Cookies before action URL: {session.cookies.get_dict()}", args.verbose
            )

            # Get the raw cookie header
            raw_cookie_header = "; ".join(
                [f"{key}={value}" for key, value in session.cookies.items()]
            )

            # Get the raw cookie header but without looping
            # bcz we want specific order of cookies
            # first cookie is csrfToken
            # second cookie is app_visitor
            # third cookie is AppSession
            # fourth cookie is ab

            # # lets extract csrtToken only
            # raw_cookie_header = "csrfToken=" + session.cookies.get("csrfToken", "")
            # # then app_visitor
            # raw_cookie_header += (
            #     "; " + "app_visitor=" + session.cookies.get("app_visitor", "")
            # )
            # # then AppSession
            # raw_cookie_header += (
            #     "; " + "AppSession=" + session.cookies.get("AppSession", "")
            # )
            # # then ab
            # raw_cookie_header += "; " + "ab=" + session.cookies.get("ab", "")
            debug_log(f"Raw cookie header:\n{raw_cookie_header}", args.verbose)

            ajax_headers["Cookie"] = raw_cookie_header  # lowercase on purpose

            # # Update cookie "csrfToken" from form data
            # csrf_token = form_data["_csrfToken"]
            # session.cookies.set("csrfToken", csrf_token)
            # debug_log(f"Updated csrfToken in cookies: {csrf_token}", args.verbose)

            debug_log(
                f"Session cookies before action url: {session.cookies.get_dict()}",
                args.verbose,
            )

            # mimic the delay of the browser
            sleep(3)

            # Do the POST like curl
            post_res = requests.post(
                form_action_url,
                headers=ajax_headers,
                data=raw_body,
            )
            debug_log(f"POST status: {post_res.status_code}", args.verbose)
            post_res.raise_for_status()

            print("\n✅ POST request complete!")

            # response is json {"url": ""}
            json_response = post_res.json()
            debug_log(f"JSON response: {json_response}", args.verbose)
            if "url" in json_response:
                print("🔗 Redirected URL:", json_response["url"])
            else:
                print("⚠️ No URL found in the response.")

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
