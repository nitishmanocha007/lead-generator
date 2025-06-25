from serpapi import GoogleSearch
from apify_client import ApifyClient
import json


def get_linkedin_profiles(query, num_results=20):
    params = {
        "engine": "google",
        "q": f"site:linkedin.com/in/ {query}",
        "api_key": "cabc49f64d4ea49e50986543fecf9a3c119b1725a02ba00a982a4bed0204ae5b",  # Replace this with your SerpAPI key
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
    client = ApifyClient("apify_api_0Kdh08NOWcOoxAyM6vMR6nGOHriTeb0cfdQB")  # Replace this with your Apify API token

    # Prepare input
    run_input = {
        "profileUrls": linkedin_urls
    }

    # Run the Actor and wait for it to finish
    run = client.actor("2SyF0bVxmgGr8IVCZ").call(run_input=run_input)

    # Fetch and print Actor results
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        print(item)
        results.append(item)

    return results

# --- Run full pipeline ---
query = "real estate agent India"
urls = get_linkedin_profiles(query, num_results=20)

if urls:
    print(f"🔗 Found {len(urls)} LinkedIn profiles. Sending to Apify...")
    apify_results = run_apify_scraper(urls)
else:
    print("⚠️ No LinkedIn URLs found.")

with open("apify_results.json", "w", encoding="utf-8") as f:
    json.dump(apify_results, f, indent=2, ensure_ascii=False)
