import os
import json
import time
import platform
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.proxy import Proxy, ProxyType
from webdriver_manager.chrome import ChromeDriverManager
from testproxies import print_proxy_test_results, test_proxies, test_single_proxy, get_working_proxies

proxies = [ "1.12.55.136:2080", "1.180.0.162:7302", "1.180.49.222:7302", "5.8.18.244:993", "5.56.124.176:8192", "5.135.1.146:25275", "5.189.159.215:59166", "8.142.3.145:3306", "8.210.76.150:27832", "8.210.253.223:53854", "8.218.160.143:1080", "18.163.25.217:8080", "23.253.253.26:59166", "24.249.199.4:4145", "24.249.199.12:4145", "31.41.90.142:1080", "31.43.203.100:1080", "31.202.25.190:3128", "34.79.91.3:59040", "37.44.238.2:54140", "37.192.118.80:1080", "37.230.114.48:1081", "39.170.85.129:7302", "42.193.23.91:7890", "43.132.238.17:24018"]

#print_proxy_test_results(test_proxies(proxies))
#proxies = get_working_proxies(proxies)
#print(proxies)
proxies = None

def get_chrome_profiles_dir():
    """
    Get the base Chrome profiles directory based on the operating system.
    
    Returns:
        str: The path to the Chrome profiles directory
    """
    system = platform.system().lower()
    
    if system == "windows":
        return os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data')
    elif system == "linux":
        return os.path.expanduser('~/.config/google-chrome')
    elif system == "darwin":  # macOS
        return os.path.expanduser('~/Library/Application Support/Google/Chrome')
    else:
        raise OSError(f"Unsupported operating system: {system}")


def list_chrome_profiles():
    """
    List all available Chrome profiles and their details.
    
    Returns:
        dict: A dictionary of profile names and their paths
    """
    profiles = {}
    profiles_dir = get_chrome_profiles_dir()
    
    if not os.path.exists(profiles_dir):
        return profiles

    # Check Default profile
    default_path = os.path.join(profiles_dir, 'Default')
    if os.path.exists(default_path):
        profiles['Default'] = default_path

    # Check numbered profiles
    for item in os.listdir(profiles_dir):
        if item.startswith('Profile '):
            profile_path = os.path.join(profiles_dir, item)
            
            # Try to get the profile name from Preferences file
            pref_file = os.path.join(profile_path, 'Preferences')
            if os.path.exists(pref_file):
                try:
                    with open(pref_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        profile_name = data.get('profile', {}).get('name', item)
                        profiles[profile_name] = profile_path
                except (json.JSONDecodeError, IOError):
                    # If we can't read the preferences, use the directory name
                    profiles[item] = profile_path
            else:
                profiles[item] = profile_path

    return profiles


def get_profile_path(profile_identifier):
    """
    Get the path for a specific Chrome profile.
    
    Args:
        profile_identifier (str): Name or number of the profile to use
        
    Returns:
        str: Full path to the profile directory
    """
    profiles = list_chrome_profiles()
    
    # If the identifier is a direct match
    if profile_identifier in profiles:
        return profiles[profile_identifier]
    
    # Try to match by profile number
    if profile_identifier.isdigit():
        profile_dir = f'Profile {profile_identifier}'
        for name, path in profiles.items():
            if path.endswith(profile_dir):
                return path
    
    # Try to match by partial name
    matches = [path for name, path in profiles.items() 
              if profile_identifier.lower() in name.lower()]
    
    if matches:
        return matches[0]
    
    raise ValueError(f"Could not find Chrome profile matching '{profile_identifier}'")


def setup_driver(profile_identifier=None, headless=False):
    """
    Create a Selenium WebDriver instance with optional user profile and proxy settings.
    Args:
        profile_identifier (str): The identifier for the Chrome profile.
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

    if profile_identifier:
        try:
            profile_path = get_profile_path(profile_identifier)
            if os.path.exists(profile_path):
                options.add_argument(f'--user-data-dir={get_chrome_profiles_dir()}')
                options.add_argument(f'--profile-directory={os.path.basename(profile_path)}')
            else:
                print(f"Warning: Chrome profile path does not exist: {profile_path}")
        except (OSError, ValueError) as e:
            print(f"Error setting up Chrome profile: {e}")

    # Set up proxy
    if proxies:
        proxy = random.choice(proxies)
        if proxy:
            options.add_argument(f'--proxy-server=socks5://{proxy}')
        driver.get("https://www.whatismyipaddress.com/")
        time.sleep(5)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Remove the "navigator.webdriver" property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    

    return driver


def print_available_profiles():
    """
    Print all available Chrome profiles in a readable format.
    """
    profiles = list_chrome_profiles()
    if not profiles:
        print("No Chrome profiles found.")
        return
        
    print("\nAvailable Chrome Profiles:")
    print("-" * 50)
    for name, path in profiles.items():
        print(f"Profile Name: {name}")
        print(f"Path: {path}")
        print("-" * 50)


if __name__ == "__main__":
    print_available_profiles()