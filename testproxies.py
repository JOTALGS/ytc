import requests
from concurrent.futures import ThreadPoolExecutor
import time
from typing import List, Dict
import json

def test_single_proxy(proxy: str, timeout: int = 10) -> Dict:
    """
    Test a single proxy by attempting to connect to a testing website.
    
    Args:
        proxy (str): Proxy address in format 'ip:port'
        timeout (int): Maximum time to wait for response in seconds
        
    Returns:
        dict: Dictionary containing test results
    """
    proxies = {
        'http': f'http://{proxy}',
        'https': f'http://{proxy}'
    }
    
    result = {
        'proxy': proxy,
        'working': False,
        'response_time': None,
        'error': None
    }
    
    try:
        start_time = time.time()
        # Try to connect to a reliable testing website
        response = requests.get('http://httpbin.io/ip', 
                              proxies=proxies, 
                              timeout=timeout)
        
        if response.status_code == 200:
            result['working'] = True
            result['response_time'] = round(time.time() - start_time, 2)
            
            # Verify if proxy is actually working by checking returned IP
            returned_ip = json.loads(response.text)['origin'].split(',')[0]
            proxy_ip = proxy.split(':')[0]
            
            if returned_ip != proxy_ip:
                result['error'] = 'Proxy not anonymous'
                result['working'] = False
                
    except requests.exceptions.RequestException as e:
        result['error'] = str(e)
    
    return result

def test_proxies(proxy_list: List[str], timeout: int = 10, max_workers: int = 10) -> List[Dict]:
    """
    Test multiple proxies concurrently.
    
    Args:
        proxy_list (List[str]): List of proxies to test
        timeout (int): Maximum time to wait for each proxy
        max_workers (int): Maximum number of concurrent tests
        
    Returns:
        List[Dict]: List of test results for each proxy
    """
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_proxy = {
            executor.submit(test_single_proxy, proxy, timeout): proxy 
            for proxy in proxy_list
        }
        
        for future in future_to_proxy:
            results.append(future.result())
    
    return results

def print_proxy_test_results(results: List[Dict]):
    """
    Print the results of proxy testing in a readable format.
    
    Args:
        results (List[Dict]): List of proxy test results
    """
    print("\nProxy Test Results:")
    print("-" * 60)
    
    working_proxies = [r for r in results if r['working']]
    failed_proxies = [r for r in results if not r['working']]
    
    print(f"Total Proxies Tested: {len(results)}")
    print(f"Working Proxies: {len(working_proxies)}")
    print(f"Failed Proxies: {len(failed_proxies)}")
    print("\nWorking Proxies Details:")
    print("-" * 60)
    
    for result in working_proxies:
        print(f"Proxy: {result['proxy']}")
        print(f"Response Time: {result['response_time']} seconds")
        print("-" * 30)
    
    if failed_proxies:
        print("\nFailed Proxies Details:")
        print("-" * 60)
        for result in failed_proxies:
            print(f"Proxy: {result['proxy']}")
            print(f"Error: {result['error']}")
            print("-" * 30)

def get_working_proxies(proxy_list: List[str]) -> List[str]:
    """
    Test proxies and return only the working ones.
    
    Args:
        proxy_list (List[str]): List of proxies to test
        
    Returns:
        List[str]: List of working proxies
    """
    results = test_proxies(proxy_list)
    return [r['proxy'] for r in results if r['working']]