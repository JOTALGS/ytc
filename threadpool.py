import asyncio
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, List
import random
from itertools import cycle
import time
from contextlib import asynccontextmanager
from driversetup import setup_driver

# A general guideline is to limit the number of comments to around 5-10 per day per account,
# and to avoid making identical or similar comments on the same video to prevent being flagged as spam.
# Some users report being able to make up to 50-100 comments per day per account without issues, while others have encountered problems with as few as 5 comments


class ProfileRotator:
    def __init__(self, profiles: List[str]):
        self.profile_cycle = cycle(profiles)
        self._lock = asyncio.Lock()
    
    async def get_next_profile(self) -> str:
        async with self._lock:
            return next(self.profile_cycle)


@asynccontextmanager
async def get_driver(profile: str):
    """Async context manager for WebDriver"""
    driver = setup_driver(profile)
    try:
        yield driver
    finally:
        driver.quit()

async def post_single_comment(video_url: str, profile: str, comments: List[str]) -> None:
    """Post a comment on a single video using the specified profile"""
    async with get_driver(profile) as driver:
        try:
            driver.get(video_url)
            
            # Wait for comment box
            comment_box = WebDriverWait(driver, 40).until(
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
            await asyncio.sleep(random.uniform(30, 60))
            
            print(f"Successfully posted comment on {video_url} using profile: {profile}")
            
        except Exception as e:
            print(f"Error posting comment on {video_url} with profile {profile}: {e}")

async def post_comments(video_urls_dict: Dict[str, List[str]], profiles: List[str], comments: List[str]) -> None:
    """Post comments on all videos using rotating profiles"""
    profile_rotator = ProfileRotator(profiles)
    tasks = []
    
    for search_url, videos in video_urls_dict.items():
        for video_url in videos:
            # Get next profile for this video
            profile = await profile_rotator.get_next_profile()
            # Create task for posting comment
            task = asyncio.create_task(post_single_comment(video_url, profile, comments))
            tasks.append(task)
    
    # Wait for all comments to be posted
    await asyncio.gather(*tasks)


def main():
    pass

# Example usage
if __name__ == "__main__":
    main()