import os
import boto3
from playwright.sync_api import sync_playwright

class Twitter:

    def __init__(self, state_bucket):
        self.state_bucket = state_bucket
        self.s3_client = boto3.client('s3')
        self.state_file_path = '/tmp/twitter_state.json'

    def _download_state(self):
        try:
            self.s3_client.download_file(self.state_bucket, 'twitter_state.json', self.state_file_path)
            print("Successfully downloaded Twitter state from S3.")
            return True
        except Exception as e:
            print(f"Error downloading Twitter state from S3: {e}")
            return False

    def update_status(self, text):
        if not self._download_state():
            raise Exception("Cannot post to Twitter without state file.")

        with sync_playwright() as p:
            # Lambda requires these flags for chromium
            browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--single-process'])
            context = browser.new_context(storage_state=self.state_file_path)
            page = context.new_page()

            print("Navigating to X compose page...")
            page.goto('https://x.com/compose/tweet')

            # Wait for the text area to be visible
            print("Waiting for tweet text area...")
            page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=30000)

            print("Typing tweet...")
            page.locator('[data-testid="tweetTextarea_0"]').fill(text)

            print("Clicking post button...")
            page.locator('[data-testid="tweetButton"]').click()

            # Wait for the tweet to be posted (e.g., looking for a toast message)
            print("Waiting for confirmation...")
            try:
                page.wait_for_selector('[data-testid="toast"]', timeout=15000)
            except Exception as e:
                print(f"Toast not found, but continuing: {e}")
            
            print("Tweet posted successfully.")
            browser.close()
            return True
