import os
import sys
import time
import io
import pandas as pd

# --- UTF-8 Output Setup ---
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except Exception:
    pass

# --- IMPORTS ---
from scrapper import LinkedInSearchScraper
from bot import LinkedInCommentGenerator
from comment import LinkedInCommentPoster

def main():
    """
    Main function to orchestrate the entire LinkedIn workflow:
    1. Scrape posts.
    2. Generate AI comments.
    3. Post comments to LinkedIn.
    """

    # --- USER CONFIGURATION ---
    CHROME_PROFILE_PATH = r""  #  Change to your path
    OPENAI_API_KEY = "" #paste the api key here
    SEARCH_URL = "" #keep the search url
    COMMENT_PROMPT = "" #write the type of comment

    TOTAL_SCROLLS = 1
    POSTING_DELAY = 15  # Seconds
    SCRAPED_DATA_CSV = "scraped_linkedin_posts.csv"
    FINAL_DATA_CSV = "final_posts_with_comments.csv"

    if not CHROME_PROFILE_PATH or not SEARCH_URL:
        print(" ERROR: Missing CHROME_PROFILE_PATH or SEARCH_URL.")
        sys.exit(1)

    # --- STAGE 1: SCRAPE POSTS ---
    print(" Starting Stage 1: Scraping LinkedIn posts...")
    scraper = None
    try:
        scraper = LinkedInSearchScraper(profile_path=CHROME_PROFILE_PATH)
        scraper.scrape_and_save(
            search_url=SEARCH_URL,
            csv_file=SCRAPED_DATA_CSV,
            total_scrolls=TOTAL_SCROLLS
        )
    except Exception as e:
        print(f" Error during scraping: {e}")
    finally:
        if scraper:
            scraper.close()
            print(" Scraping complete. Browser closed.")

    # --- STAGE 2: GENERATE COMMENTS ---
    print(" Starting Stage 2: Generating comments...")
    if not os.path.exists(SCRAPED_DATA_CSV):
        print(" ERROR: Scraped data file not found.")
        sys.exit(1)

    try:
        generator = LinkedInCommentGenerator(api_key=OPENAI_API_KEY)
        generator.generate_comments_for_all(
            csv_file=SCRAPED_DATA_CSV,
            comment_type=COMMENT_PROMPT,
            output_file=FINAL_DATA_CSV
        )
        print(" Comment generation complete.")
    except Exception as e:
        print(f"Error during comment generation: {e}")

    # --- STAGE 3: POST COMMENTS ---
    print(" Starting Stage 3: Posting comments to LinkedIn...")
    if not os.path.exists(FINAL_DATA_CSV):
        print(" ERROR: Final data file not found.")
        sys.exit(1)

    poster = None
    try:
        df = pd.read_csv(FINAL_DATA_CSV)
        if df.empty:
            print(" No comments to post.")
            return

        poster = LinkedInCommentPoster(profile_path=CHROME_PROFILE_PATH)
        for index, row in df.iterrows():
            post_url = row.get("Post URL")
            comment = row.get("Comment")
            
            print(f"this is post url {post_url}")
            print(f"this is comment{comment}")

            if pd.notna(post_url) and pd.notna(comment):
                print(f"\n Posting comment {index + 1}/{len(df)} to {post_url}")
                poster.post_comment(post_url, comment)
                print(f" Waiting {POSTING_DELAY} seconds before next post...")
                time.sleep(POSTING_DELAY)
            else:
                print(f"Skipping row {index + 1}: Missing URL or comment.")

    except Exception as e:
        print(f"Error during posting: {e}")
    finally:
        if poster:
            poster.close()
            print(" Posting complete. Browser closed.")

    print("\n All tasks finished successfully.")

if __name__ == "__main__":
    main()
