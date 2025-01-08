from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from typing import List, Dict
import os
import random
import time
import json


comments = [
    "Great video! Very informative",
    "Thanks for sharing this content!",
    "This helped me understand the topic better",
    "Well explained, keep it up!"
]

email = "unaiprobador@gmail.com"
password = "Jotajota99"


def setup_driver(user_profile=None):
    options = Options()
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    if user_profile:
        profile_path = os.path.expandvars(f'C:\\Users\\{user_profile}\\AppData\\Local\\Google\\Chrome\\User Data')
        options.add_argument(f'--user-data-dir={profile_path}')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
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