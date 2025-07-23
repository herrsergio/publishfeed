import logging
import os

import newspaper
import openai
from newspaper import Config, settings


def load_openai_key():
    """Load OpenAI API key from file or environment variable."""
    key_file_path = os.path.join(os.path.dirname(__file__), "openai_key.txt")

    if os.path.exists(key_file_path):
        with open(key_file_path, "r") as f:
            return f.read().strip()

    # Fallback to environment variable
    return os.environ.get("OPENAI_KEY")


openai.api_key = load_openai_key()


def extract_article_text(url):
    try:
        config = Config()
        config.browser_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"

        article = newspaper.Article(url, config=config)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        logging.warning(f"Failed to extract article: {e}")
        return ""


def extract_article_summary(url):
    try:
        settings.MAX_SUMMARY_SENT = 3
        config = Config()
        config.browser_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"

        article = newspaper.Article(url, config=config)
        article.download()
        article.parse()
        article.nlp()
        return article.summary
    except Exception as e:
        logging.warning(f"Failed to extract article: {e}")
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
