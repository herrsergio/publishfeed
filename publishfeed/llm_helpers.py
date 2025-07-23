import logging
import os
import time
from urllib.parse import urlparse

import newspaper
import openai
import requests
from bs4 import BeautifulSoup
from newspaper import Config, settings


def load_openai_key():
    """Load OpenAI API key from file or environment variable."""
    key_file_path = os.path.join(os.path.dirname(__file__), "openai_key.txt")

    if os.path.exists(key_file_path):
        with open(key_file_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    # Fallback to environment variable
    return os.environ.get("OPENAI_KEY")


openai.api_key = load_openai_key()


def _extract_with_requests(url):
    """Fallback extraction using requests and BeautifulSoup."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
    }

    try:
        # Add a small delay to appear more human-like
        time.sleep(1)

        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()

        # Try to find main content areas
        content_selectors = [
            "article",
            '[role="main"]',
            "main",
            ".content",
            ".post-content",
            ".entry-content",
            ".article-content",
            ".post-body",
            ".story-body",
        ]

        text = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                text = " ".join([elem.get_text(strip=True) for elem in elements])
                if len(text) > 200:
                    break

        # Fallback to body if no specific content found
        if not text or len(text) < 200:
            body = soup.find("body")
            if body:
                text = body.get_text(strip=True)

        # Clean up the text
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        text = " ".join(lines)

        return text if len(text) > 100 else ""

    except Exception as e:
        logging.warning("Requests fallback failed: %s", str(e))
        return ""


def extract_article_text(url):
    """Extract article text from URL with multiple fallback strategies."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    ]

    # First try newspaper with different user agents
    for i, user_agent in enumerate(user_agents):
        try:
            config = Config()
            config.browser_user_agent = user_agent
            config.request_timeout = 10
            config.number_threads = 1

            article = newspaper.Article(url, config=config)
            article.download()
            article.parse()

            if article.text and len(article.text.strip()) > 100:
                logging.info(
                    "Successfully extracted article with newspaper (user agent %d)",
                    i + 1,
                )
                return article.text

            logging.warning("Article text too short or empty with user agent %d", i + 1)

        except Exception as e:
            logging.warning(
                "Failed to extract article with user agent %d: %s", i + 1, str(e)
            )
            continue

    # Fallback to requests + BeautifulSoup
    logging.info("Trying requests fallback for URL: %s", url)
    text = _extract_with_requests(url)
    if text:
        logging.info("Successfully extracted article with requests fallback")
        return text

    logging.error("All extraction attempts failed for URL: %s", url)
    return ""


def extract_article_summary(url):
    """Extract article summary from URL with multiple fallback strategies."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    ]

    # First try newspaper with different user agents
    for i, user_agent in enumerate(user_agents):
        try:
            settings.MAX_SUMMARY_SENT = 3
            config = Config()
            config.browser_user_agent = user_agent
            config.request_timeout = 10
            config.number_threads = 1

            article = newspaper.Article(url, config=config)
            article.download()
            article.parse()
            article.nlp()

            if article.summary and len(article.summary.strip()) > 50:
                logging.info(
                    "Successfully extracted summary with newspaper (user agent %d)",
                    i + 1,
                )
                return article.summary

            logging.warning("Summary too short or empty with user agent %d", i + 1)

        except Exception as e:
            logging.warning(
                "Failed to extract summary with user agent %d: %s", i + 1, str(e)
            )
            continue

    # Fallback: extract full text and create summary from first few sentences
    logging.info("Trying text extraction fallback for summary")
    text = _extract_with_requests(url)
    if text:
        # Create a simple summary from first 3 sentences
        sentences = text.split(". ")[:3]
        summary = ". ".join(sentences)
        if len(summary) > 50:
            logging.info("Successfully created summary from extracted text")
            return summary

    logging.error("All summary extraction attempts failed for URL: %s", url)
    return ""


def summarize_text(text, max_tokens=200):
    if not text:
        return ""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize this article for a Twitter post (250 chars max) using a friendly casual techical tone, add emojis and hashtags if you consider good option:\n\n{text}",
                }
            ],
            temperature=0.7,
            max_tokens=max_tokens,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logging.error(f"LLM summarization failed: {e}")
        return ""
