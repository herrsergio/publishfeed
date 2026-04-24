#!/usr/bin/env python
import json
import argparse
import os

def create_state(auth_token, ct0):
    # Base playwright state structure
    state = {
        "cookies": [
            {
                "name": "auth_token",
                "value": auth_token,
                "domain": ".x.com",
                "path": "/",
                "expires": 4102444800, # Year 2100
                "httpOnly": True,
                "secure": True,
                "sameSite": "None"
            },
            {
                "name": "auth_token",
                "value": auth_token,
                "domain": ".twitter.com",
                "path": "/",
                "expires": 4102444800,
                "httpOnly": True,
                "secure": True,
                "sameSite": "None"
            }
        ],
        "origins": []
    }
    
    if ct0:
        state["cookies"].append({
            "name": "ct0",
            "value": ct0,
            "domain": ".x.com",
            "path": "/",
            "expires": 4102444800,
            "httpOnly": False,
            "secure": True,
            "sameSite": "Lax"
        })
        state["cookies"].append({
            "name": "ct0",
            "value": ct0,
            "domain": ".twitter.com",
            "path": "/",
            "expires": 4102444800,
            "httpOnly": False,
            "secure": True,
            "sameSite": "Lax"
        })
    
    output_path = 'twitter_state.json'
    with open(output_path, 'w') as f:
        json.dump(state, f, indent=2)
        
    print(f"Created {output_path} successfully!")
    print("You can now run the local test script.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create Playwright state from X.com cookies')
    parser.add_argument('--auth_token', required=True, help="Value of the auth_token cookie")
    parser.add_argument('--ct0', required=False, help="Value of the ct0 cookie (highly recommended for X)")
    args = parser.parse_args()
    
    create_state(args.auth_token, args.ct0)
