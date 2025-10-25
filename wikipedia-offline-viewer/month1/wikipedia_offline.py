#!/usr/bin/env python3
"""
Wikipedia Offline Viewer
Downloads a Wikipedia page and saves it for offline viewing
Includes CSS and images for better offline experience
"""

import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse

def download_page(url):
    """Download the Wikipedia page"""
    print(f"Downloading page: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error downloading page: {e}")
        return None

def save_page(html_content, output_file):
    """Save the HTML content to a file"""
    try:
        # Parse HTML with BeautifulSoup to clean it up
        soup = BeautifulSoup(html_content, 'html.parser')

        # Make links absolute so they work offline
        for link in soup.find_all('a'):
            if link.get('href'):
                link['href'] = urljoin('https://en.wikipedia.org', link['href'])

        # Make image sources absolute
        for img in soup.find_all('img'):
            if img.get('src'):
                img['src'] = urljoin('https://en.wikipedia.org', img['src'])

        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        print(f"Page saved successfully to: {output_file}")
        return True

    except Exception as e:
        print(f"Error saving page: {e}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("Wikipedia Offline Page Downloader")
    print("=" * 50)

    # Get input from user
    url = input("\nEnter Wikipedia page URL: ").strip()

    # Validate URL
    if not url.startswith('http'):
        print("Error: Please enter a valid URL starting with http or https")
        return

    # Get output filename
    output = input("Enter output filename (default: wikipedia_page.html): ").strip()
    if not output:
        output = "wikipedia_page.html"

    # Make sure it has .html extension
    if not output.endswith('.html'):
        output += '.html'

    # Download and save
    html = download_page(url)
    if html:
        if save_page(html, output):
            print(f"\nDone! Open '{output}' in your browser to view offline.")
        else:
            print("\nFailed to save the page.")
    else:
        print("\nFailed to download the page.")

if __name__ == "__main__":
    main()
