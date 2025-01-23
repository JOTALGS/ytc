from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List
from threadpool import post_comments
import time
import asyncio
from driversetup import list_chrome_profiles


user_profiles = ["Persona 2", "Default", "Sixto"]

def get_video_urls(search_links: List[str], num_videos: int) -> dict:
    # Initialize webdriver
    driver = webdriver.Chrome()
    results = {}
    
    try:
        for search_url in search_links:
            videos = []
            driver.get(search_url)
            
            # Wait for video elements to load
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.ID, "contents")))
            
            # Scroll to load more videos
            last_height = driver.execute_script("return document.documentElement.scrollHeight")
            while len(videos) < num_videos:
                driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(2)  # Wait for content to load
                
                # Get video links
                video_elements = driver.find_elements(By.CSS_SELECTOR, "a#video-title")
                videos = [elem.get_attribute('href') for elem in video_elements if elem.get_attribute('href')]
                videos = [url for url in videos if url][:num_videos]
                
                new_height = driver.execute_script("return document.documentElement.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            results[search_url] = videos
            
    finally:
        driver.quit()
    
    return results

async def main():
    search_links = [
        "https://www.youtube.com/results?search_query=python+programming",
        "https://www.youtube.com/results?search_query=selenium+tutorial"
    ]
    num_videos = 2
    comments = [
        "Great video! Very informative",
        "Thanks for sharing this content!",
        "This helped me understand the topic better",
        "Well explained, keep it up!"
    ]

    profiles = list_chrome_profiles()
    profiles = list(profiles.keys())
    print(profiles)

    results = get_video_urls(search_links, num_videos)
    for search_url, videos in results.items():
        print(f"\nSearch URL: {search_url}")
        print(f"Found {len(videos)} videos:")
        for video in videos:
            print(video)

    await post_comments(results, profiles, comments)

# Example usage
if __name__ == "__main__":
    asyncio.run(main())