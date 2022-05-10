import os
import urllib.request

import requests
import opengraph_py3

from ln_oauth import ln_auth, ln_headers

# credentials = '/home/ubuntu/publishfeed/publishfeed/ln_credentials.json'
# access_token = ln_auth(credentials)  # Authenticate the API
# headers = ln_headers(access_token)  # Make the headers to attach to the API call.


def ln_user_info(headers):
    '''
    Get user information from Linkedin
    '''
    response = requests.get('https://api.linkedin.com/v2/me', headers=headers)
    user_info = response.json()
    return user_info


def post_2_linkedin(message, link, link_text, author, api_url, headers):
    #asset = upload_image_linkdin(link, author, headers)
    #print(asset)
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
                        #"media": asset,
                        "originalUrl": link,
                        "title": {
                            "text": link_text
                        }
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    print(post_data)
    r = requests.post(api_url, headers=headers, json=post_data)
    r.json()
    print(r)


def upload_image_linkdin(link, author, headers):
    # https://docs.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin

    image_url = ""
    register_upload_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    register_upload_data = {
        "registerUploadRequest": {
            "recipes": [
                "urn:li:digitalmediaRecipe:feedshare-image"
            ],
            "owner": author,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }
    register_upload_response = requests.post(register_upload_url, headers=headers, json=register_upload_data, timeout=30)
    response = register_upload_response.json()

    uploadurl = response['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
    asset = response['value']['asset']

    og_link = opengraph_py3.OpenGraph(url=link)

    for key, value in og_link.items():
        if key == "image":
            image_url = value

    image_filename = image_url.split('/')[-1]
    local_image_filename = "/tmp/"+image_filename
    urllib.request.urlretrieve(image_url, local_image_filename)

    upload_response = requests.put(uploadurl, headers=headers, data=open(local_image_filename, 'rb').read())

    os.remove(local_image_filename)

    return asset



