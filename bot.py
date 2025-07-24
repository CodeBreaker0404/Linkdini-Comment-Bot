# -*- coding: utf-8 -*-
import io
import sys
import pandas as pd
from openai import OpenAI

# Setup UTF-8 output

class LinkedInCommentGenerator:
    """
    Generates AI-based comments for LinkedIn posts using the OpenAI API.
    """

    def __init__(self, api_key=""):
        """
        Initializes the OpenAI client.
        Args:
            api_key (str): Your OpenAI API key (leave blank for external injection).
        """
        self.client = OpenAI(api_key=api_key)

    def generate_comment(self, post_content, comment_type):
        """
        Generates a single comment using the OpenAI API.
        Args:
            post_content (str): The LinkedIn post content.
            comment_type (str): Instruction/prompt type (tone or goal).
        Returns:
            str: Generated comment text.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a helpful assistant that writes LinkedIn comments. {comment_type}"},
                    {"role": "user", "content": f"Write a comment for this post:\n{post_content}"}
                ],
                temperature=0.5,
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[ERROR] OpenAI error: {e}")
            return None

    def generate_comments_for_all(self, csv_file, comment_type, output_file="comments_generated.csv"):
        """
        Generates comments for all posts and saves them to a new CSV file.
        Args:
            csv_file (str): Path to input CSV file with post content and URLs.
            comment_type (str): Prompt guiding the type of comment.
            output_file (str): Path to save the post-comment results.
        """
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            print(f"[ERROR] Could not read CSV: {e}")
            return

        results = []

        for i, row in df.iterrows():
            post = row.get("Post Content", "")
            url = row.get("Post URL", "")
            if not post:
                continue

            print(f"[INFO] Generating comment for post {i + 1}/{len(df)}")
            comment = self.generate_comment(post, comment_type)
            if comment:
                results.append({
                    "Post Content": post,
                    "Post URL": url,
                    "Comment": comment
                })

        try:
            pd.DataFrame(results).to_csv(output_file, index=False)
            print(f"[SUCCESS] Saved {len(results)} comments to {output_file}")
        except Exception as e:
            print(f"[ERROR] Could not save results: {e}")
