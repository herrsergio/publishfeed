from rapidfuzz import fuzz
import re

def generate_hashtags_fuzzy(title):
    keywords_to_hashtags = {
                "API": "#API",
        "AWS": "#AWS",
        "Amazon Web Services": "#AWS",
        "Aurora": "#Aurora",
        "Azure": "#Azure",
        "Bedrock": "#Bedrock",
        "CNCF": "#CNCF",
        "CNCF": "#CNCF",
        "ChatGPT": "#ChatGPT",
        "Claude": "#Claude",
        "CloudWatch": "#CloudWatch",
        "EC2": "#EC2",
        "Fargate": "#Fargate",
        "Forrester": "#Forrester",
        "GCP": "#GCP",
        "GPT": "#GPT",
        "Gartner": "#Gartner",
        "Gemini": "#Gemini",
        "Gemini": "#Gemini",
        "GitHub": "#GitHub",
        "Google Cloud Platform": "#GCP",
        "Google": "#Google",
        "Inferentia": "#Inferentia",
        "Kubernetes": "#Kubernetes",
        "LLM": "#LLM",
        "LLMs": "#LLM",
        "Linux": "#Linux",
        "Microsoft": "#Microsoft",
        "OpenAI": "#OpenAI",
        "RDS": "#RDS",
        "S3": "#S3",
        "SQL": "#SQL",
        "SageMaker": "#SageMaker",
        "TOFAG": "#TOGAF",
        "Terraform": "#Terraform",
        "Trainium": "#Trainium",
        "ai": "#AI",
        "algorithm": "#algorithm",
        "artificial intelligence": "#AI",
        "blockchain": "#blockchain",
        "cloud computing": "#CloudComputing",
        "cloud": "#Cloud",
        "compliance": "#compliance",
        "containers": "#containers",
        "data": "#data",
        "database": "#database",
        "devops": "#DevOps",
        "foundational model": "#FM",
         "health": "#health",
        "innovation": "#innovation",
        "k8s": "#Kubernetes",
        "kubernetes": "#Kubernetes",
        "large language models": "#LLM",
        "leadership": "#leadership",
        "machine learning": "#ML",
        "malware": "#malware",
        "MCP": "#MCP",
        "model context protocol": "#MCP",
        "microservices": "#microservices",
        "ml": "#ML",
        "open source": "#OpenSource",
        "Pandas": "#Pandas",
        "public sector": "#PublicSector",
        "ransomware": "#ransomware",
        "robot": "#robot",
        "Scikit": "#Scikit",
        "serverless": "#serverless",
        "technology": "#technology",
        "transformers": "#transofrmers",
    }

    hashtags = set()
    title_clean = re.sub(r"[^\w\s]", "", title.lower())

    for phrase, hashtag in keywords_to_hashtags.items():
        # Exact phrase match
        pattern = r'\b' + re.escape(phrase.lower()) + r'\b'
        if re.search(pattern, title_clean):
            hashtags.add(hashtag)
        else:
            # Fuzzy fallback
            score = fuzz.partial_ratio(phrase.lower(), title_clean)
            if score >= 85:
                hashtags.add(hashtag)

    return list(hashtags)

