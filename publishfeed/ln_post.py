import os
import urllib.request
from urllib.parse import urlparse
from urllib.parse import urljoin

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

# Using legacy method to share URL so it can also add image to the post
def post_2_linkedin_legacy(message, link, link_text, author, api_url, headers):
    #thumbnail = get_image_url_from_link(link)
    thumbnail = custom_get_img_from_link(link)

    payload = {
        "content": {
            "contentEntities": [
                {
                    "entityLocation": link,
                    "thumbnails": [
                        {
                            "resolvedUrl": thumbnail
                        }
                    ]
                }
            ],
            "title": link_text
        },
        'distribution': {
            'linkedInDistributionTarget': {}
        },
        'owner': f'{author}',
        'text': {
            'text': link_text
        }
    }
    r = requests.post(api_url, headers=headers, json=payload)
    r.json()
    print(r)

def post_2_linkedin_new(message, link, link_text, author, api_url, headers):
    thumbnail_url = custom_get_img_from_link(link)
    image_urn = None

    if thumbnail_url:
        image_urn = upload_image_and_get_urn(thumbnail_url, author, headers)

    #print("image_urn = "+image_urn)

    article_obj = {
        "source": link,
        "title": message,
        "description": link_text,
    }

    if image_urn:
        article_obj["thumbnail"] = image_urn

    post_data = {
        "author": author,
        "commentary": link_text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "content": {
            "article": article_obj
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False
    }

    headers["Linkedin-Version"] = "202505"

    response = requests.post(
            api_url, 
            headers=headers, 
            json=post_data
    )

    print("LinkedIn post status:", response.status_code)
    print(response.text)

def get_image_url_from_link(link):
    image_url = ""
    og_link = opengraph_py3.OpenGraph(url=link)

    for key, value in og_link.items():
        if key == "image":
            image_url = value

    return image_url

def custom_get_img_from_link(link):
    
    #headers = {"User-Agent":get_random_UA()}
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}
    r = requests.get(link, headers=headers)

    parsed_uri = urlparse(link)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

    page = opengraph_py3.OpenGraph(html=r.content)

    if page.is_valid():

        image_url = page.get('image', None)

        if not image_url.startswith('http'):
            image_url = urljoin(domain, page['image'])

        return image_url

def upload_image_and_get_urn(image_url, author_urn, headers):
    # 1. Step: Initialize image upload
    init_payload = {
        "initializeUploadRequest": {
            "owner": author_urn
        }
    }

    init_resp = requests.post(
        "https://api.linkedin.com/rest/images?action=initializeUpload",
        headers={**headers, "LinkedIn-Version": "202505", "Content-Type": "application/json"},
        json=init_payload
    )

    if init_resp.status_code != 200:
        print("Failed to initialize image upload:", init_resp.status_code, init_resp.text)
        return None

    upload_info = init_resp.json()
    upload_url = upload_info["value"]["uploadUrl"]
    image_urn = upload_info["value"]["image"]

    # 2. Step: Download image from source
    img_resp = requests.get(image_url)
    if img_resp.status_code != 200:
        print("Failed to download image:", image_url)
        return None

    # 3. Step: Upload image bytes to LinkedIn
    put_resp = requests.put(
        upload_url,
        headers={"Content-Type": "image/jpeg"},
        data=img_resp.content
    )

    if put_resp.status_code not in (200, 201):
        print("Failed to upload image to LinkedIn:", put_resp.status_code, put_resp.text)
        return None

    return image_urn

# Uploading the image to Linkedin did not work
# Keeping this function, it could be handy later
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
