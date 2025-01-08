from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from typing import List, Dict
import os
import random
import time
import json

# A general guideline is to limit the number of comments to around 5-10 per day per account,
# and to avoid making identical or similar comments on the same video to prevent being flagged as spam.
# Some users report being able to make up to 50-100 comments per day per account without issues, while others have encountered problems with as few as 5 comments

proxies = [
    "192.99.44.178:3128",
    "162.241.207.217:80",
    "191.97.96.208:8080",
]

comments = [
    "Great video! Very informative",
    "Thanks for sharing this content!",
    "This helped me understand the topic better",
    "Well explained, keep it up!"
]

email = "unaiprobador@gmail.com"
password = "Jotajota99"


def setup_driver(user_profile=None, headless=False):
    """
    Create a Selenium WebDriver instance with optional user profile and proxy settings.

    Args:
        user_profile (str): The username for the Chrome user profile.
        proxy (str): The proxy server address in the format 'host:port'.
        headless (bool): Whether to run the browser in headless mode.

    Returns:
        webdriver.Chrome: Configured WebDriver instance.
    """
    options = Options()
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")

    if user_profile:
        profile_path = os.path.expandvars(f'C:\\Users\\{user_profile}\\AppData\\Local\\Google\\Chrome\\User Data')
        options.add_argument(f'--user-data-dir={profile_path}')

    capabilities = webdriver.DesiredCapabilities.CHROME

    proxy = random.choice(proxies)
    if proxy:
        proxy_settings = Proxy()
        proxy_settings.proxy_type = ProxyType.MANUAL
        proxy_settings.http_proxy = proxy
        proxy_settings.ssl_proxy = proxy
        proxy_settings.add_to_capabilities(capabilities)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options, desired_capabilities=capabilities)

    # Remove the "navigator.webdriver" property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver

def post_comments(video_urls_dict: Dict[str, List[str]], user_profile=None):
    driver = setup_driver(user_profile)
    try:
        for search_url, videos in video_urls_dict.items():
            for video_url in videos:
                driver.get(video_url)
                
                # Wait for comment box
                comment_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#simplebox-placeholder"))
                )
                comment_box.click()
                
                # Find and fill comment field
                comment_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#contenteditable-root"))
                )
                
                # Select random comment
                random_comment = random.choice(comments)
                comment_field.send_keys(random_comment)
                
                # Submit comment
                submit_button = driver.find_element(By.CSS_SELECTOR, "#submit-button")
                submit_button.click()
                
                # Wait between comments
                time.sleep(random.uniform(30, 60))
    
    finally:
        driver.quit()

def main():
    pass

# Example usage
if __name__ == "__main__":
    main()