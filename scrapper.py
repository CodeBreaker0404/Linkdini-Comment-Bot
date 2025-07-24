import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


class LinkedInSearchScraper:
    def __init__(self, profile_path):
        options = Options()
        options.add_argument(f"user-data-dir={profile_path}")
        self.driver = webdriver.Chrome(options=options)

    def scrape_and_save(self, search_url, csv_file, total_scrolls=1):
        print(" Starting LinkedIn post scraping...")
        self.driver.get(search_url)
        time.sleep(5)

        posts = set()
        skipped = 0

        for scroll_num in range(total_scrolls):
            print(f" Scrolling... {scroll_num + 1}/{total_scrolls}")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            elements = self.driver.find_elements(By.CLASS_NAME, "update-components-text")

            for el in elements:
                text = el.text.strip()
                if not text:
                    continue
                try:
                    parent = el.find_element(By.XPATH, "./ancestor::div[contains(@class,'feed-shared-update-v2')]")
                    urn = parent.get_attribute("data-urn")
                    if urn and "urn:li:activity:" in urn:
                        post_url = f"https://www.linkedin.com/feed/update/{urn}"
                        posts.add((text, post_url))
                    else:
                        skipped += 1
                        print(f"Skipping post: data-urn not found.")
                except Exception as e:
                    skipped += 1
                    print(f" Error finding URL for post: {e.__class__.__name__}: {e}")

        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Post Content", "Post URL"])
            for content, url in posts:
                writer.writerow([content, url])

        print(f"Scraping complete. {len(posts)} posts saved to {csv_file}")
        print(f"Skipped {skipped} posts without valid URL.")

    def close(self):
        self.driver.quit()


__all__ = ["LinkedInSearchScraper"]
