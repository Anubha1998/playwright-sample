import json
import os
import urllib
import subprocess
import playwright.sync_api
from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor

capabilities = [
  {
    'browserName': 'Chrome', 
    'browserVersion': 'latest',
    'LT:Options': {
      'platform': 'Windows 10',
      'build': 'Playwright With Parallel Build',
      'name': 'Playwright Sample Test on Windows 10 - Chrome',
      'user': 'anubhas',
      'accessKey': 'accesskey',
      'network': True,
      'video': True,
      'console': True
    }
  },
  {
    'browserName': 'MicrosoftEdge',
    'browserVersion': 'latest',
    'LT:Options': {
      'platform': 'MacOS Ventura',
      'build': 'Playwright With Parallel Build',
      'name': 'Playwright Sample Test on Windows 8 - MicrosoftEdge',
      'user': 'anubhas',
      'accessKey':'accesskey',
      'network': True,
      'video': True,
      'console': True
    }
  },
  {
    'browserName': 'Chrome',
    'browserVersion': 'latest',
    'LT:Options': {
      'platform': 'MacOS Big sur',
      'build': 'Playwright With Parallel Build',
      'name': 'Playwright Sample Test on MacOS Big sur - Chrome',
      'user': 'anubhas',
      'accessKey': 'accesskey',
      'network': True,
      'video': True,
      'console': True
    }
  }
]

def run_test(capability):
    playwrightVersion = str(subprocess.getoutput('playwright --version')).strip().split(" ")[1]
    capability['LT:Options']['playwrightClientVersion'] = playwrightVersion
    lt_cdp_url = 'wss://cdp.lambdatest.com/playwright?capabilities=' + urllib.parse.quote(json.dumps(capability))
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect(lt_cdp_url)
        page = browser.new_page()
        try:
            page.goto("https://www.bing.com/")
            page.wait_for_timeout(3000)
            page.fill('[id="sb_form_q"]', 'LambdaTest')
            page.wait_for_timeout(1000)
            page.keyboard.press("Enter")
            page.wait_for_timeout(1000)
            page.wait_for_selector('[class=" b_active"]')

            title = page.title()
            print("Title:: ", title)

            if "LambdaTest" in title:
                set_test_status(page, "passed", "Title matched")
            else:
                set_test_status(page, "failed", "Title did not match")

            # get test details at runtime using lambdatest hook
            test_details = get_test_details(page=page)
            print("Test Details response - ", json.loads(test_details))
        except Exception as err:
            print("Error:: ", err)
            set_test_status(page, "failed", str(err))

        browser.close()

def get_test_details(page):
    return page.evaluate("_ => {}", "lambdatest_action: {\"action\": \"getTestDetails\"}")

def set_test_status(page, status, remark):
    page.evaluate("_ => {}", "lambdatest_action: {\"action\": \"setTestStatus\", \"arguments\": {\"status\":\"" + status + "\", \"remark\": \"" + remark + "\"}}")

def run_tests_in_parallel():
    with ThreadPoolExecutor(max_workers=len(capabilities)) as executor:
        for capability in capabilities:
            executor.submit(run_test, capability)

if __name__ == "__main__":
    run_tests_in_parallel()
