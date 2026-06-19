#!/usr/bin/env python
import os
import sys

# Add parent directory to path to import local modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from twitter import Twitter

def test_local_posting():
    print("Initializing Twitter Playwright process...")
    # We don't need a real bucket if we're using a local state file
    twitter = Twitter(state_bucket="local-test-only")
    
    # We want to use the local state file instead of downloading from S3
    # so we override the download method
    twitter.state_file_path = 'twitter_state.json'
    
    def mock_download():
        if os.path.exists(twitter.state_file_path):
            print(f"Found local {twitter.state_file_path}, skipping S3 download.")
            return True
        else:
            print(f"Error: Could not find local {twitter.state_file_path}.")
            print("Please run management/sync_twitter_state.py first (and comment out the 'os.remove(state_file)' line if needed) so the file stays locally.")
            return False
            
    twitter._download_state = mock_download
    
    test_message = "Hello from Playwright locally! Testing the automation script before Lambda deployment. 🚀"
    
    print(f"Attempting to post: '{test_message}'")
    try:
        twitter.update_status(test_message)
        print("Success! The local Playwright process works.")
    except Exception as e:
        print(f"Failed to post: {e}")

if __name__ == '__main__':
    test_local_posting()
