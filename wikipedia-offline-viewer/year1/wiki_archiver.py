#!/usr/bin/env python3
"""
Wikipedia Page Archiver
A robust tool to download Wikipedia pages for offline viewing with all assets.

Features:
- Downloads HTML content
- Downloads and saves CSS stylesheets locally
- Downloads and saves images locally
- Preserves page structure for offline browsing
- Command-line interface with multiple options

Author: Year 1 Developer
"""

import argparse
import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WikipediaArchiver:
    """Class to handle downloading and archiving Wikipedia pages"""

    def __init__(self, url, output_dir='wiki_archive'):
        """
        Initialize the archiver

        Args:
            url (str): Wikipedia page URL to download
            output_dir (str): Directory to save archived content
        """
        self.url = url
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WikipediaArchiver/1.0'
        })

    def create_directories(self):
        """Create necessary directories for storing assets"""
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / 'css').mkdir(exist_ok=True)
        (self.output_dir / 'images').mkdir(exist_ok=True)
        logger.info(f"Created output directory: {self.output_dir}")

    def download_resource(self, url, local_path):
        """
        Download a resource (CSS, image, etc.) and save locally

        Args:
            url (str): URL of the resource
            local_path (Path): Local path to save the resource

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            with open(local_path, 'wb') as f:
                f.write(response.content)

            return True
        except Exception as e:
            logger.warning(f"Failed to download {url}: {e}")
            return False

    def process_images(self, soup):
        """
        Download images and update their references

        Args:
            soup (BeautifulSoup): Parsed HTML document
        """
        images = soup.find_all('img')
        logger.info(f"Processing {len(images)} images...")

        for i, img in enumerate(images):
            src = img.get('src') or img.get('data-src')
            if not src:
                continue

            # Make URL absolute
            img_url = urljoin(self.url, src)

            # Generate local filename
            img_filename = f"image_{i}_{os.path.basename(urlparse(img_url).path)}"
            img_path = self.output_dir / 'images' / img_filename

            # Download image
            if self.download_resource(img_url, img_path):
                # Update reference to local path
                img['src'] = f'images/{img_filename}'
                logger.debug(f"Downloaded image: {img_filename}")

    def process_stylesheets(self, soup):
        """
        Download CSS stylesheets and update their references

        Args:
            soup (BeautifulSoup): Parsed HTML document
        """
        stylesheets = soup.find_all('link', rel='stylesheet')
        logger.info(f"Processing {len(stylesheets)} stylesheets...")

        for i, link in enumerate(stylesheets):
            href = link.get('href')
            if not href:
                continue

            # Make URL absolute
            css_url = urljoin(self.url, href)

            # Generate local filename
            css_filename = f"style_{i}.css"
            css_path = self.output_dir / 'css' / css_filename

            # Download stylesheet
            if self.download_resource(css_url, css_path):
                # Update reference to local path
                link['href'] = f'css/{css_filename}'
                logger.debug(f"Downloaded stylesheet: {css_filename}")

    def download_page(self):
        """
        Download and archive the Wikipedia page

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Downloading page: {self.url}")
            response = self.session.get(self.url, timeout=15)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Create output directories
            self.create_directories()

            # Process assets
            self.process_stylesheets(soup)
            self.process_images(soup)

            # Save HTML file
            output_file = self.output_dir / 'index.html'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(str(soup.prettify()))

            logger.info(f"Successfully archived page to: {output_file}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download page: {e}")
            return False
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return False


def main():
    """Main function to parse arguments and run archiver"""
    parser = argparse.ArgumentParser(
        description='Download Wikipedia pages for offline viewing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://en.wikipedia.org/wiki/Python_(programming_language)
  %(prog)s https://en.wikipedia.org/wiki/Linux -o linux_archive
  %(prog)s https://en.wikipedia.org/wiki/Coffee -o coffee -v
        """
    )

    parser.add_argument(
        'url',
        help='Wikipedia page URL to download'
    )

    parser.add_argument(
        '-o', '--output',
        default='wiki_archive',
        help='Output directory (default: wiki_archive)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Validate URL
    if not args.url.startswith('http'):
        logger.error("Please provide a valid URL starting with http or https")
        sys.exit(1)

    # Create archiver and download
    archiver = WikipediaArchiver(args.url, args.output)
    success = archiver.download_page()

    if success:
        print(f"\n✓ Page successfully archived!")
        print(f"  Open {args.output}/index.html in your browser")
    else:
        print("\n✗ Failed to archive page")
        sys.exit(1)


if __name__ == '__main__':
    main()
