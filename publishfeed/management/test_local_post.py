#!/usr/bin/env python
import os
import sys

# Add parent directory to path to import local modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from bluesky import Bluesky
from atproto import client_utils

def test_local_posting():
    print("Initializing Bluesky local posting test...")
    
    # Retrieve credentials from environment variables
    handle = os.environ.get("BLUESKY_HANDLE")
    password = os.environ.get("BLUESKY_PASSWORD")
    
    if not handle or not password:
        print("Error: BLUESKY_HANDLE and BLUESKY_PASSWORD environment variables must be set.")
        print("Usage:")
        print("  BLUESKY_HANDLE=\"your.handle.bsky.social\" BLUESKY_PASSWORD=\"your-app-password\" python3 management/test_local_post.py")
        sys.exit(1)
        
    print(f"Using handle: {handle}")
    bluesky = Bluesky(handle, password)
    
    # Create a Rich Text test message with a link and a tag
    tb = client_utils.TextBuilder()
    tb.text("Hello from Antigravity/Bluesky local test script! 🚀\nTesting rich text links: ")
    tb.link("Bluesky Python SDK", "https://atproto.blue")
    tb.text("\nAnd a tag: ")
    tb.tag("#atproto", "atproto")
    
    print("Attempting to post to Bluesky...")
    try:
        response = bluesky.update_status(tb)
        print("Success! Post created.")
        print(f"Post URI: {response.uri}")
    except Exception as e:
        print(f"Failed to post: {e}")

if __name__ == '__main__':
    test_local_posting()
