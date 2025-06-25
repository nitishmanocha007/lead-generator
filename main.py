from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from serpapi import GoogleSearch
from apify_client import ApifyClient
import os

app = FastAPI()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
APIFY_KEY = os.getenv("APIFY_KEY")

if not SERPAPI_KEY or not APIFY_KEY:
    raise ValueError("API keys not found. Please set SERPAPI_KEY and APIFY_KEY in environment variables.")

class QueryRequest(BaseModel):
    query: str
    num_results: int = 20

@app.post("/scrape")
def scrape_linkedin(data: QueryRequest):
    linkedin_urls = get_linkedin_profiles(data.query, data.num_results)

    if not linkedin_urls:
        return {"message": "No LinkedIn profiles found", "urls": []}

    apify_results = run_apify_scraper(linkedin_urls)
    return {"urls": linkedin_urls, "apify_results": apify_results}


def get_linkedin_profiles(query, num_results=20):
    params = {
        "engine": "google",
        "q": f"site:linkedin.com/in/ {query}",
        "api_key": SERPAPI_KEY,
        "num": num_results
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    linkedin_urls = []
    for result in results.get("organic_results", []):
        link = result.get("link")
        if "linkedin.com/in/" in link:
            linkedin_urls.append(link)

    return linkedin_urls

def run_apify_scraper(linkedin_urls):
    client = ApifyClient(APIFY_KEY)

    run_input = {"profileUrls": linkedin_urls}
    run = client.actor("2SyF0bVxmgGr8IVCZ").call(run_input=run_input)

    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(item)

    return results
