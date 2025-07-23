from rapidfuzz import fuzz
import re

def generate_hashtags_fuzzy(title):
    keywords_to_hashtags = {
        "ai": "#AI",
        "algorithm": "#algorithm",
        "Amazon Web Services": "#AWS",
        "API": "#API",
        "artificial intelligence": "#AI",
        "Aurora": "#Aurora",
        "AWS": "#AWS",
        "Azure": "#Azure",
        "Bedrock": "#Bedrock",
        "blockchain": "#blockchain",
        "ChatGPT": "#ChatGPT",
        "Claude": "#Claude",
        "cloud computing": "#CloudComputing",
        "cloud": "#Cloud",
        "CloudWatch": "#CloudWatch",
        "CNCF": "#CNCF",
        "CNCF": "#CNCF",
        "compliance": "#compliance",
        "containers": "#containers",
        "data": "#data",
        "database": "#database",
        "devops": "#DevOps",
        "EC2": "#EC2",
        "Fargate": "#Fargate",
        "Forrester": "#Forrester",
        "foundational model": "#FM",
        "Gartner": "#Gartner",
        "GCP": "#GCP",
        "Gemini": "#Gemini",
        "Gemini": "#Gemini",
        "GitHub": "#GitHub",
        "Google Cloud Platform": "#GCP",
        "Google": "#Google",
        "GPT": "#GPT",
        "health": "#health",
        "Inferentia": "#Inferentia",
        "innovation": "#innovation",
        "k8s": "#Kubernetes",
        "Kubernetes": "#Kubernetes",
        "kubernetes": "#Kubernetes",
        "large language models": "#LLM",
        "leadership": "#leadership",
        "Linux": "#Linux",
        "LLM": "#LLM",
        "LLMs": "#LLM",
        "machine learning": "#ML",
        "malware": "#malware",
        "MCP": "#MCP",
        "microservices": "#microservices",
        "Microsoft": "#Microsoft",
        "ml": "#ML",
        "model context protocol": "#MCP",
        "open source": "#OpenSource",
        "OpenAI": "#OpenAI",
        "Pandas": "#Pandas",
        "public sector": "#PublicSector",
        "ransomware": "#ransomware",
        "RDS": "#RDS",
        "robot": "#robot",
        "S3": "#S3",
        "SageMaker": "#SageMaker",
        "Scikit": "#Scikit",
        "serverless": "#serverless",
        "SQL": "#SQL",
        "technology": "#technology",
        "Terraform": "#Terraform",
        "TOFAG": "#TOGAF",
        "Trainium": "#Trainium",
        "transformers": "#transformers",
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


