import requests

proxy = "http://109.196.98.101:8888"
proxies = {"http": proxy, "https": proxy}

try:
    response = requests.get("https://www.youtube.com", proxies=proxies, timeout=50)
    if response.status_code == 200:
        print("Proxy is working.")
    else:
        print("Proxy is not working.")
except Exception as e:
    print(f"Error: {e}")


def confiugure_clean_driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    import os
    from driversetup import get_chrome_profiles_dir, get_profile_path
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    
    prefs = {
        "profile.managed_default_content_settings.images": 1,
        "profile.managed_default_content_settings.videos": 1,
        "profile.managed_default_content_settings.javascript": 1,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    try:
        profile_path = get_profile_path("Default")
        if os.path.exists(profile_path):
            chrome_options.add_argument(f'--user-data-dir={get_chrome_profiles_dir()}')
            chrome_options.add_argument(f'--profile-directory={os.path.basename(profile_path)}')
        else:
            print(f"Warning: Chrome profile path does not exist: {profile_path}")
    except (OSError, ValueError) as e:
        print(f"Error setting up Chrome profile: {e}")
    
    capabilities = DesiredCapabilities.CHROME
    capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}

    service = Service(ChromeDriverManager().install())
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Remove the "navigator.webdriver" property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    driver.execute_cdp_cmd(
        "Network.setBlockedURLs",
        {
            "urls": []
        }
    )
    driver.execute_cdp_cmd("Network.enable", {})
    
    driver.refresh()

    driver.quit()

if __name__ == "__main__":
    confiugure_clean_driver()