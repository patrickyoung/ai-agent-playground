#!/usr/bin/env python3
"""
Wikipedia Page Archiver Pro
A production-ready tool for archiving Wikipedia pages with all assets for offline viewing.

Features:
- Asynchronous downloads for improved performance
- Retry logic with exponential backoff
- Progress tracking with visual feedback
- Comprehensive error handling and logging
- Type hints for better code maintainability
- Configurable options for various use cases
- Proper resource management and cleanup

Author: Year 5 Developer
License: MIT
"""

import argparse
import asyncio
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse
import hashlib

import aiohttp
from bs4 import BeautifulSoup
from tqdm.asyncio import tqdm


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('wiki_archiver.log')
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ArchiverConfig:
    """Configuration for the Wikipedia archiver"""
    url: str
    output_dir: Path
    max_concurrent_downloads: int = 10
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    download_images: bool = True
    download_css: bool = True
    user_agent: str = 'WikipediaArchiverPro/2.0'
    verbose: bool = False


class ResourceDownloader:
    """Handles downloading of web resources with retry logic"""

    def __init__(self, config: ArchiverConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.downloaded_urls: Set[str] = set()

    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={'User-Agent': self.config.user_agent}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def download_with_retry(
        self,
        url: str,
        max_retries: Optional[int] = None
    ) -> Optional[bytes]:
        """
        Download a resource with exponential backoff retry logic

        Args:
            url: URL to download
            max_retries: Maximum number of retry attempts

        Returns:
            Resource content as bytes, or None if failed
        """
        if max_retries is None:
            max_retries = self.config.max_retries

        retry_delay = self.config.retry_delay

        for attempt in range(max_retries + 1):
            try:
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    content = await response.read()
                    self.downloaded_urls.add(url)
                    return content

            except aiohttp.ClientError as e:
                if attempt == max_retries:
                    logger.warning(f"Failed to download {url} after {max_retries} retries: {e}")
                    return None

                # Exponential backoff
                wait_time = retry_delay * (2 ** attempt)
                logger.debug(f"Retry {attempt + 1}/{max_retries} for {url}, waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)

            except Exception as e:
                logger.error(f"Unexpected error downloading {url}: {e}")
                return None

        return None

    def generate_filename(self, url: str, extension: str = '') -> str:
        """
        Generate a unique filename based on URL hash

        Args:
            url: Resource URL
            extension: File extension to append

        Returns:
            Generated filename
        """
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        parsed = urlparse(url)
        original_name = Path(parsed.path).stem or 'resource'

        # Sanitize filename
        safe_name = "".join(c for c in original_name if c.isalnum() or c in ('_', '-'))[:30]

        if extension:
            return f"{safe_name}_{url_hash}.{extension}"
        return f"{safe_name}_{url_hash}"


class WikipediaArchiver:
    """Main archiver class for Wikipedia pages"""

    def __init__(self, config: ArchiverConfig):
        self.config = config
        self.downloader: Optional[ResourceDownloader] = None
        self.soup: Optional[BeautifulSoup] = None

    def _create_directories(self) -> None:
        """Create necessary directories for storing archived content"""
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        if self.config.download_css:
            (self.config.output_dir / 'css').mkdir(exist_ok=True)

        if self.config.download_images:
            (self.config.output_dir / 'images').mkdir(exist_ok=True)

        logger.info(f"Created output directory structure: {self.config.output_dir}")

    async def _download_page_html(self) -> Optional[str]:
        """
        Download the main Wikipedia page HTML

        Returns:
            HTML content as string, or None if failed
        """
        logger.info(f"Downloading page: {self.config.url}")

        content = await self.downloader.download_with_retry(self.config.url)
        if not content:
            logger.error("Failed to download main page")
            return None

        return content.decode('utf-8', errors='ignore')

    async def _process_images(self, pbar: tqdm) -> List[Tuple[str, str]]:
        """
        Download images and return mapping of old src to new src

        Args:
            pbar: Progress bar for visual feedback

        Returns:
            List of tuples (original_src, new_local_path)
        """
        if not self.config.download_images:
            return []

        images = self.soup.find_all('img')
        tasks = []
        image_mapping = []

        for img in images:
            src = img.get('src') or img.get('data-src')
            if not src:
                continue

            img_url = urljoin(self.config.url, src)

            # Determine file extension
            parsed = urlparse(img_url)
            ext = Path(parsed.path).suffix.lstrip('.') or 'jpg'

            filename = self.downloader.generate_filename(img_url, ext)
            local_path = self.config.output_dir / 'images' / filename

            tasks.append(self._download_and_save(img_url, local_path, pbar))
            image_mapping.append((src, f'images/{filename}'))

        # Download images concurrently with semaphore to limit concurrent connections
        semaphore = asyncio.Semaphore(self.config.max_concurrent_downloads)

        async def bounded_download(task):
            async with semaphore:
                return await task

        await asyncio.gather(*[bounded_download(task) for task in tasks])

        return image_mapping

    async def _process_stylesheets(self, pbar: tqdm) -> List[Tuple[str, str]]:
        """
        Download CSS stylesheets and return mapping of old href to new href

        Args:
            pbar: Progress bar for visual feedback

        Returns:
            List of tuples (original_href, new_local_path)
        """
        if not self.config.download_css:
            return []

        stylesheets = self.soup.find_all('link', rel='stylesheet')
        tasks = []
        css_mapping = []

        for link in stylesheets:
            href = link.get('href')
            if not href:
                continue

            css_url = urljoin(self.config.url, href)
            filename = self.downloader.generate_filename(css_url, 'css')
            local_path = self.config.output_dir / 'css' / filename

            tasks.append(self._download_and_save(css_url, local_path, pbar))
            css_mapping.append((href, f'css/{filename}'))

        # Download stylesheets concurrently
        semaphore = asyncio.Semaphore(self.config.max_concurrent_downloads)

        async def bounded_download(task):
            async with semaphore:
                return await task

        await asyncio.gather(*[bounded_download(task) for task in tasks])

        return css_mapping

    async def _download_and_save(
        self,
        url: str,
        local_path: Path,
        pbar: Optional[tqdm] = None
    ) -> bool:
        """
        Download a resource and save it locally

        Args:
            url: Resource URL
            local_path: Path to save the resource
            pbar: Optional progress bar to update

        Returns:
            True if successful, False otherwise
        """
        content = await self.downloader.download_with_retry(url)

        if content:
            try:
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.write_bytes(content)

                if pbar:
                    pbar.update(1)

                logger.debug(f"Saved: {local_path.name}")
                return True

            except IOError as e:
                logger.error(f"Failed to save {local_path}: {e}")

        if pbar:
            pbar.update(1)

        return False

    def _update_references(
        self,
        image_mapping: List[Tuple[str, str]],
        css_mapping: List[Tuple[str, str]]
    ) -> None:
        """
        Update HTML references to point to local files

        Args:
            image_mapping: Mapping of original image src to local paths
            css_mapping: Mapping of original stylesheet href to local paths
        """
        # Update image sources
        for old_src, new_src in image_mapping:
            for img in self.soup.find_all('img'):
                if img.get('src') == old_src or img.get('data-src') == old_src:
                    img['src'] = new_src
                    if 'data-src' in img.attrs:
                        del img['data-src']

        # Update stylesheet references
        for old_href, new_href in css_mapping:
            for link in self.soup.find_all('link', rel='stylesheet'):
                if link.get('href') == old_href:
                    link['href'] = new_href

        # Add a note at the top of the page
        if self.soup.body:
            note = self.soup.new_tag('div', style='background: #ffffcc; padding: 10px; margin: 10px; border: 1px solid #ccc; border-radius: 5px;')
            note.string = '📦 This is an archived offline copy of a Wikipedia page.'
            self.soup.body.insert(0, note)

    async def archive(self) -> bool:
        """
        Main method to archive the Wikipedia page

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory structure
            self._create_directories()

            # Initialize downloader
            async with ResourceDownloader(self.config) as downloader:
                self.downloader = downloader

                # Download main page
                html_content = await self._download_page_html()
                if not html_content:
                    return False

                # Parse HTML
                self.soup = BeautifulSoup(html_content, 'html.parser')

                # Count total resources to download
                num_images = len(self.soup.find_all('img')) if self.config.download_images else 0
                num_css = len(self.soup.find_all('link', rel='stylesheet')) if self.config.download_css else 0
                total_resources = num_images + num_css

                logger.info(f"Found {num_images} images and {num_css} stylesheets")

                # Download resources with progress bar
                with tqdm(total=total_resources, desc="Downloading resources", unit="file") as pbar:
                    image_mapping = await self._process_images(pbar)
                    css_mapping = await self._process_stylesheets(pbar)

                # Update HTML references
                self._update_references(image_mapping, css_mapping)

                # Save final HTML
                output_file = self.config.output_dir / 'index.html'
                output_file.write_text(str(self.soup), encoding='utf-8')

                logger.info(f"Successfully archived page to: {output_file}")

                # Print summary
                print(f"\n{'='*60}")
                print(f"Archive Summary:")
                print(f"  Output directory: {self.config.output_dir}")
                print(f"  Main file: index.html")
                print(f"  Images downloaded: {len([m for m in image_mapping if m])}")
                print(f"  Stylesheets downloaded: {len([m for m in css_mapping if m])}")
                print(f"  Total resources: {len(self.downloader.downloaded_urls)}")
                print(f"{'='*60}")

                return True

        except Exception as e:
            logger.error(f"Archiving failed: {e}", exc_info=True)
            return False


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Archive Wikipedia pages for offline viewing with all assets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://en.wikipedia.org/wiki/Python_(programming_language)
  %(prog)s https://en.wikipedia.org/wiki/Linux -o linux_archive --no-images
  %(prog)s https://en.wikipedia.org/wiki/Coffee -o coffee -v --max-concurrent 20

Features:
  - Asynchronous concurrent downloads for speed
  - Automatic retry with exponential backoff
  - Progress tracking
  - Comprehensive error handling
  - Configurable options
        """
    )

    parser.add_argument(
        'url',
        help='Wikipedia page URL to archive'
    )

    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=Path('wiki_archive'),
        help='Output directory (default: wiki_archive)'
    )

    parser.add_argument(
        '--no-images',
        action='store_true',
        help='Skip downloading images'
    )

    parser.add_argument(
        '--no-css',
        action='store_true',
        help='Skip downloading stylesheets'
    )

    parser.add_argument(
        '--max-concurrent',
        type=int,
        default=10,
        help='Maximum concurrent downloads (default: 10)'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Timeout for downloads in seconds (default: 30)'
    )

    parser.add_argument(
        '--max-retries',
        type=int,
        default=3,
        help='Maximum retry attempts (default: 3)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser.parse_args()


async def main_async() -> int:
    """Main async function"""
    args = parse_arguments()

    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Validate URL
    if not args.url.startswith('http'):
        logger.error("Please provide a valid URL starting with http or https")
        return 1

    # Create configuration
    config = ArchiverConfig(
        url=args.url,
        output_dir=args.output,
        max_concurrent_downloads=args.max_concurrent,
        timeout=args.timeout,
        max_retries=args.max_retries,
        download_images=not args.no_images,
        download_css=not args.no_css,
        verbose=args.verbose
    )

    # Create archiver and run
    archiver = WikipediaArchiver(config)
    success = await archiver.archive()

    if success:
        print(f"\n✓ Page successfully archived!")
        print(f"  Open {config.output_dir}/index.html in your browser")
        return 0
    else:
        print("\n✗ Failed to archive page")
        return 1


def main() -> None:
    """Main entry point"""
    try:
        sys.exit(asyncio.run(main_async()))
    except KeyboardInterrupt:
        print("\n\nArchiving interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
