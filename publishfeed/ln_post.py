import requests

from ln_oauth import ln_auth, ln_headers

credentials = 'ln_credentials.json'
access_token = ln_auth(credentials)  # Authenticate the API
headers = ln_headers(access_token)  # Make the headers to attach to the API call.


def ln_user_info(headers):
    '''
    Get user information from Linkedin
    '''
    response = requests.get('https://api.linkedin.com/v2/me', headers=headers)
    user_info = response.json()
    return user_info


def post_2_linkedin(message, link, link_text):
    post_data = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": message
                },
                "shareMediaCategory": "ARTICLE",
                "media": [
                    {
                        "status": "READY",
                        "description": {
                            "text": message
                        },
                        "originalUrl": link,
                        "title": {
                            "text": link_text
                        }
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "CONNECTIONS"
        }
    }
    r = requests.post(api_url, headers=headers, json=post_data)
    r.json()


# Get user id to make a UGC post
user_info = ln_user_info(headers)
urn = user_info['id']

# UGC will replace shares over time.
api_url = 'https://api.linkedin.com/v2/ugcPosts'
author = f'urn:li:person:{urn}'

post_2_linkedin("", "https://t.co/vrm6illhRt", "My testing strategy for serverless applications")
