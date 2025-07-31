from playwright.sync_api import sync_playwright
import time
import json

def get_instagram_cookies(username, password, save_path="ig_cookies.json"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.instagram.com/accounts/login/")
        time.sleep(2)
        page.fill("input[name='username']", username)
        page.fill("input[name='password']", password)
        page.click("button[type='submit']")
        time.sleep(8)  # 2차 인증은 직접 처리
        cookies = page.context.cookies()
        cookies_dict = {c['name']: c['value'] for c in cookies if c['name'] in ['sessionid', 'ds_user_id', 'csrftoken']}
        print("[쿠키값]", cookies_dict)
        with open(save_path, "w") as f:
            json.dump(cookies_dict, f)
        browser.close()
        return cookies_dict