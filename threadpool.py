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
        self.profiles = profiles
        self.index = 0

    async def get_next_profile(self) -> str:
        """Get the next profile in a rotating manner."""
        profile = self.profiles[self.index]
        self.index = (self.index + 1) % len(self.profiles)
        return profile


@asynccontextmanager
async def get_driver(profile: str):
    """Async context manager for WebDriver"""
    driver = setup_driver(profile)
    try:
        yield driver
    finally:
        driver.quit()

async def post_single_comment(video_urls: List[str], profile: str, comments: List[str]) -> None:
    """Post a comment on a single video using the specified profile"""
    async with get_driver(profile) as driver:
        for url in video_urls:
            try:
                driver.get(url)
                
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
                
                """
                # Submit comment
                submit_button = driver.find_element(By.CSS_SELECTOR, "#submit-button")
                submit_button.click()
                """
                
                # Wait between comments
                await asyncio.sleep(random.uniform(30, 60))
                
                print(f"Successfully posted comment on {url} using profile: {profile}")    
            except Exception as e:
                print(f"Error posting comment on {url} with profile {profile}: {e}")

async def post_comments(video_urls_dict: Dict[str, List[str]], profiles: List[str], comments: List[str]) -> None:
    """Post comments on all videos using rotating profiles, two at a time."""
    profile_rotator = ProfileRotator(profiles)
    tasks = []

    dict_items = list(video_urls_dict.items())
    chunk_size = 70

    for i in range(0, len(dict_items), chunk_size):
        # Get a chunk of 70 key-value pairs
        chunk = dict_items[i:i + chunk_size]

        # Get two profiles for this chunk
        profile1 = await profile_rotator.get_next_profile()
        profile2 = await profile_rotator.get_next_profile()

        # Post comments concurrently using the two profiles
        tasks.append(asyncio.create_task(post_comments_with_profiles(chunk, profile1, profile2, comments)))

    # Wait for all chunks to be processed
    await asyncio.gather(*tasks)

async def post_comments_with_profiles(video_urls_slice: List[tuple], profile1: str, profile2: str, comments: List[str]) -> None:
    """Post comments on a slice of video URLs using two profiles concurrently."""
    tasks = []

    # Split the slice into two parts for the two profiles
    half = len(video_urls_slice) // 2
    slice1 = video_urls_slice[:half]
    slice2 = video_urls_slice[half:]

    video_urls1 = [url for _, urls in slice1 for url in urls]
    video_urls2 = [url for _, urls in slice2 for url in urls]

    # Post comments using profile1 on slice1
    tasks.append(asyncio.create_task(post_single_comment(video_urls1, profile1, comments)))

    # Post comments using profile2 on slice2
    tasks.append(asyncio.create_task(post_single_comment(video_urls2, profile2, comments)))

    # Wait for both profiles to finish their slices
    await asyncio.gather(*tasks)


def main():
    pass

# Example usage
if __name__ == "__main__":
    main()