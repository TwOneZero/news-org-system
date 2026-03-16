"""Quick script to check content quality of saved articles."""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(mongo_uri)
db = client["news_org"]
collection = db["articles"]

# Get latest article from yonhap_economy
article = collection.find_one({"source": "yonhap_economy"}, sort=[("published_at", -1)])

if article:
    print(f"Title: {article['title']}")
    print(f"URL: {article['url']}")
    print(f"Published: {article['published_at']}")
    print("\n" + "="*80)
    print("Content (first 500 chars):")
    print("="*80)
    print(article['content'][:500])
    print("\n" + "="*80)
    print("Content (last 200 chars):")
    print("="*80)
    print(article['content'][-200:])
    print("="*80)
else:
    print("No article found")
