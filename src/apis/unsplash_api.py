import requests
import os
from src.config import UNSPLASH_ACCESS_KEY

class UnsplashAPI:
    def __init__(self, access_key):
        self.access_key = access_key
        self.api_url = "https://api.unsplash.com/"

    def search_photos(self, query, orientation="landscape", count=10):
        endpoint = f"{self.api_url}search/photos"
        headers = {"Authorization": f"Client-ID {self.access_key}"}
        params = {"query": query, "orientation": orientation, "per_page": count}
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return [photo["urls"]["regular"] for photo in data["results"]]
        except requests.exceptions.RequestException as e:
            print(f"Unsplash API request failed: {e}")
            return []

if __name__ == '__main__':
    # Example Usage (replace with your actual access key)
    if not UNSPLASH_ACCESS_KEY:
        print("Please set the Unsplash API access key in the environment variables.")
    else:
        unsplash_api = UnsplashAPI(UNSPLASH_ACCESS_KEY)
        search_term = "nature"
        image_urls = unsplash_api.search_photos(search_term)

        if image_urls:
            print(f"Found {len(image_urls)} images for '{search_term}':")
            for url in image_urls:
                print(url)
        else:
            print(f"No images found for '{search_term}'.")
