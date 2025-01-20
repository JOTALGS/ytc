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