import requests
import yaml

def load_feed_urls_from_yaml(file_path):
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
        return data.get('TechnologyFeeds', {}).get('urls', [])

def validate_feed_urls(urls, timeout=10):
    results = []
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/114.0.0.0 Safari/537.36'
        )
    }

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            content_type = response.headers.get('Content-Type', '')

            if response.status_code == 200 and ('xml' in content_type or 'rss' in content_type or 'atom' in content_type):
                results.append((url, True, "Valid feed"))
            elif response.status_code == 200:
                results.append((url, False, "Accessible but not a feed"))
            else:
                results.append((url, False, f"HTTP {response.status_code}"))
        except requests.RequestException as e:
            results.append((url, False, str(e)))

    return results

# Usage
yaml_file = 'feeds.yml'  # Update with your YAML file path
urls = load_feed_urls_from_yaml(yaml_file)

for url, valid, message in validate_feed_urls(urls):
    status = "✅" if valid else "❌"
    print(f"{status} {url} - {message}")
