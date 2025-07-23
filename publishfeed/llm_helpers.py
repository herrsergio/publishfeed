import logging
import os

import newspaper
import openai
from newspaper import Config, settings

openai.api_key = os.environ["OPENAI_KEY"]

def extract_article_text(url):
    try:
        config = Config()
        config.browser_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

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
        config.browser_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

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
            messages=[{
                "role": "user",
                "content": f"Summarize this article in 1-3 sentences using a friendly casual techical tone, add emojis if needed, for a Twitter post:\n\n{text}"
            }],
            temperature=0.7,
            max_tokens=max_tokens,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        logging.error(f"LLM summarization failed: {e}")
        return ""

