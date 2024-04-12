import requests
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor


PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')


def download_image(image_info, folder, image_index):
    """Download an individual image given a URL and a target folder."""
    img_url = image_info['src']['original']
    img_data = requests.get(img_url).content
    file_path = os.path.join(folder, f"image_{image_index}.jpg")
    with open(file_path, 'wb') as handler:
        handler.write(img_data)


def download_images(api_key, query, page):
    url = 'https://api.pexels.com/v1/search'
    headers = {'Authorization': api_key}
    params = {'query': query, 'per_page': 30, 'page': page}  # Fetch up to 30 images per request
    response = requests.get(url, headers=headers, params=params)
    next_page = None

    if response.status_code == 200:
        json_response = response.json()
        images = json_response['photos']
        folder = 'downloaded_images'
        os.makedirs(folder, exist_ok=True)
        # Use ThreadPoolExecutor to download images in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Map download_image function to all images
            executor.map(download_image, images, [folder]*len(images), [i for i in range(len(images))])
        if 'next_page' in json_response:
            next_page = page + 1
    else:
        print(f"Failed to fetch images: {response.status_code}")
    return next_page


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_images.py search_tag")
        sys.exit(1)
    search_query = sys.argv[1]
    next_page = 1
    while True:
        next_page = download_images(PEXELS_API_KEY, search_query, page=next_page)
        if next_page is None:
            next_page = 1
        time.sleep(300)  # Wait for 300 seconds before fetching new images
