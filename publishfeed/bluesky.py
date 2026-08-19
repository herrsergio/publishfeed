from urllib.parse import urljoin, urlparse

import opengraph_py3
import requests
from atproto import Client, models


class Bluesky:

    def __init__(self, handle, password):
        self.handle = handle
        self.password = password
        self.client = Client()

    def update_status(self, text, link_url=None):
        """
        Post a message to Bluesky.
        text can be a string or an atproto client_utils.TextBuilder object.
        If link_url is given, an external embed (link preview card) is built
        and attached, since Bluesky does not auto-generate link previews.
        """
        try:
            print(f"Logging in to Bluesky as {self.handle}...")
            self.client.login(self.handle, self.password)

            embed = None
            if link_url:
                embed = self._build_external_embed(link_url)

            print("Posting to Bluesky...")
            response = self.client.send_post(text, embed=embed)
            print(f"Bluesky post success. URI: {response.uri}")
            return response
        except Exception as e:
            print(f"Error posting to Bluesky: {e}")
            raise e

    def _build_external_embed(self, url):
        """
        Build an app.bsky.embed.external card for the given URL.
        Bluesky clients do not crawl URLs, so we fetch the page's OpenGraph
        metadata and upload the thumbnail image ourselves.
        Returns None if the card cannot be built (posting continues without it).
        """
        try:
            meta = self._fetch_open_graph(url)

            thumb_blob = None
            image_url = meta.get('image')
            if image_url:
                try:
                    img_resp = requests.get(image_url, timeout=10)
                    if img_resp.status_code == 200 and img_resp.content:
                        # Bluesky rejects blobs over ~1MB; skip oversized images.
                        if len(img_resp.content) <= 1_000_000:
                            thumb_blob = self.client.upload_blob(img_resp.content).blob
                        else:
                            print("Bluesky: thumbnail too large (>1MB), skipping image.")
                except Exception as e:
                    print(f"Bluesky: could not upload thumbnail: {e}")

            external = models.AppBskyEmbedExternal.External(
                uri=url,
                title=meta.get('title') or url,
                description=meta.get('description') or '',
                thumb=thumb_blob,
            )
            return models.AppBskyEmbedExternal.Main(external=external)
        except Exception as e:
            print(f"Bluesky: could not build link preview card: {e}")
            return None

    @staticmethod
    def _fetch_open_graph(url):
        """Fetch OpenGraph title/description/image for a URL."""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        r = requests.get(url, headers=headers, timeout=10)

        meta = {}
        page = opengraph_py3.OpenGraph(html=r.content)
        if page.is_valid():
            meta['title'] = page.get('title')
            meta['description'] = page.get('description')

            image_url = page.get('image', None)
            if image_url and not image_url.startswith('http'):
                parsed = urlparse(url)
                domain = f"{parsed.scheme}://{parsed.netloc}/"
                image_url = urljoin(domain, image_url)
            meta['image'] = image_url

        return meta
