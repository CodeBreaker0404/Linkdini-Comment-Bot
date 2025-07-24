# -*- coding: utf-8 -*-
import io
import sys
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class LinkedInCommentPoster:
    def __init__(self, profile_path):
        if not profile_path:
            raise ValueError("A Chrome profile path must be provided.")

        options = Options()
        options.add_argument(f"--user-data-dir={profile_path}")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)

    def post_comment(self, post_url, comment_text):
        if not post_url or not comment_text:
            print("Error: Post URL and comment text must be provided.")
            return
        if "linkedin.com" not in post_url:
            print("Invalid LinkedIn URL.")
            return

        print(f"🔗 Visiting: {post_url}")
        self.driver.get(post_url)
        time.sleep(60)

        # Scroll and click comment button
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(60)

        try:
            comment_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.comment-button"))
            )
            comment_btn.click()
            time.sleep(60)
            print(" Comment button clicked successfully.")
        except Exception as e:
            print("Comment button click failed:", e)
            try:
                self.driver.execute_script("""
                    var btn = document.querySelector('button.comment-button');
                    if (btn) btn.click();
                """)
                time.sleep(60)
                print("Fallback JS: Comment button clicked.")
            except Exception as e:
                print("Fallback JS click failed:", e)
                return

        # Type comment
        try:
            comment_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true' and contains(@class, 'ql-editor')]"))
            )
            self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true' and contains(@class, 'ql-editor')]"))
            )
            self.driver.execute_script("arguments[0].innerHTML = '';", comment_box)
            self.driver.execute_script("arguments[0].innerText = arguments[1];", comment_box, comment_text)
            comment_box.click()
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", comment_box)
            print("Comment typed successfully.")
        except Exception as e:
            print("Could not write in comment box:", e)
            try:
                self.driver.execute_script(f"""
                    var commentBox = document.querySelector('div[contenteditable="true"].ql-editor');
                    if (commentBox) {{
                        commentBox.innerHTML = '';
                        commentBox.innerText = `{comment_text}`;
                        commentBox.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                """)
                print("Fallback JS: Typed comment successfully.")
            except Exception as e:
                print("Fallback JS typing failed:", e)
                return

        # Submit comment
        try:
            submit_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'comments-comment-box__submit-button')]"))
            )
            submit_btn.click()
            time.sleep(60)
            print(" Comment submitted successfully.")
        except Exception as e:
            print("Could not submit comment:", e)
            try:
                self.driver.execute_script("""
                    var submitBtn = document.querySelector('button[class*="comments-comment-box__submit-button"]');
                    if (submitBtn) submitBtn.click();
                """)
                time.sleep(2)
                print("Fallback JS: Comment submitted.")
            except Exception as e:
                print("Fallback submit failed:", e)

        time.sleep(1)

    def post_comments_from_csv(self, csv_path):
        print("Starting Stage 3: Posting comments to LinkedIn...")
        try:
            df = pd.read_csv(csv_path, encoding='utf-8', encoding_errors='replace')
        except Exception as e:
            print(f" Error reading CSV file: {e}")
            return

        print(f"Reading CSV file: {csv_path}")
        print(f"Detected columns: {list(df.columns)}")
        print(f"First few rows:\n{df.head().to_string()}")

        df.columns = df.columns.str.strip().str.lower()
        expected_columns = {'post url': 'post_url', 'comment': 'comment'}
        df.rename(columns={k: v for k, v in expected_columns.items() if k in df.columns}, inplace=True)

        if 'post_url' not in df.columns or 'comment' not in df.columns:
            print(f" Error: CSV must contain 'Post URL' and 'Comment' columns. Found: {list(df.columns)}")
            return

        for i, row in df.iterrows():
            url = str(row.get('post_url', '')).strip()
            comment = str(row.get('comment', '')).strip()

            if not url or not comment or url == 'nan' or comment == 'nan':
                print(f"Skipping row {i + 1}: Missing or invalid URL ('{url}') or comment ('{comment}').")
                continue

            try:
                self.post_comment(url, comment)
            except Exception as e:
                print(f"Error posting comment on row {i + 1}: {e}")

        self.close()

    def close(self):
        print("Closing browser session...")
        self.driver.quit()
        print("Posting complete. Browser closed.")
