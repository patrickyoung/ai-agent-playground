#!/usr/bin/env python3
"""Archive Wikipedia pages for offline viewing.

This module provides a simple, readable tool to download Wikipedia pages
with their associated resources (images, stylesheets) for offline viewing.

The design philosophy follows PEP 20 (The Zen of Python):
    - Simple is better than complex
    - Readability counts
    - Errors should never pass silently

Type hints are used throughout for clarity and to support static analysis
tools like mypy.

Example:
    $ python wiki_archiver.py https://en.wikipedia.org/wiki/Python
    $ python wiki_archiver.py --help

Author: Guido van Rossum (hypothetical implementation)
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Error: Required package not installed: {e.name}", file=sys.stderr)
    print("Please run: pip install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)


# Configure logging with a clear, helpful format
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Simple output for end users
)
logger = logging.getLogger(__name__)


@dataclass
class ArchiveStats:
    """Statistics about the archiving operation.

    Using a dataclass makes the data structure explicit and provides
    useful __repr__ and __eq__ implementations automatically.
    """
    images_downloaded: int = 0
    images_failed: int = 0
    stylesheets_downloaded: int = 0
    stylesheets_failed: int = 0

    def total_resources(self) -> int:
        """Total number of resources processed."""
        return (self.images_downloaded + self.images_failed +
                self.stylesheets_downloaded + self.stylesheets_failed)

    def success_rate(self) -> float:
        """Calculate success rate as a percentage."""
        total = self.total_resources()
        if total == 0:
            return 100.0
        successful = self.images_downloaded + self.stylesheets_downloaded
        return (successful / total) * 100


class WikipediaArchiver:
    """Archive Wikipedia pages for offline viewing.

    This class handles downloading a Wikipedia page and its resources
    (images and CSS files) to create a self-contained offline version.

    The implementation favors readability and maintainability over
    performance optimization. For most use cases, the straightforward
    synchronous approach is sufficient and easier to understand.

    Attributes:
        url: The Wikipedia page URL to archive
        output_dir: Directory where archived files will be saved
        timeout: Request timeout in seconds
        stats: Statistics about the archiving operation
    """

    def __init__(
        self,
        url: str,
        output_dir: Path,
        timeout: int = 30
    ) -> None:
        """Initialize the archiver.

        Args:
            url: Wikipedia page URL to download
            output_dir: Directory for storing archived content
            timeout: HTTP request timeout in seconds
        """
        self.url = url
        self.output_dir = output_dir
        self.timeout = timeout
        self.stats = ArchiveStats()

        # Use a session for connection pooling and consistent headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WikipediaArchiver/1.0 (Educational tool)'
        })

    def _create_directory_structure(self) -> None:
        """Create the output directory and subdirectories for assets.

        Using exist_ok=True makes this operation idempotent, which is
        a good practice for file system operations.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'images').mkdir(exist_ok=True)
        (self.output_dir / 'css').mkdir(exist_ok=True)

    def _download_resource(
        self,
        url: str,
        local_path: Path
    ) -> bool:
        """Download a resource and save it locally.

        Args:
            url: URL of the resource to download
            local_path: Path where the resource should be saved

        Returns:
            True if successful, False otherwise

        Note:
            Errors are logged but don't stop execution. This makes the
            archiver more robust - a few missing images shouldn't fail
            the entire operation.
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Write in binary mode to handle all file types correctly
            local_path.write_bytes(response.content)
            return True

        except requests.RequestException as e:
            # Log the specific error but continue processing
            logger.debug(f"Failed to download {url}: {e}")
            return False
        except IOError as e:
            logger.warning(f"Failed to save {local_path}: {e}")
            return False

    def _process_images(self, soup: BeautifulSoup) -> None:
        """Download images referenced in the page.

        Args:
            soup: Parsed HTML document

        Note:
            Images are saved with sanitized filenames based on their
            original names. The src attributes are updated to point
            to the local copies.
        """
        images = soup.find_all('img')
        logger.info(f"Processing {len(images)} images...")

        for i, img in enumerate(images, start=1):
            src = img.get('src') or img.get('data-src')
            if not src:
                continue

            # Convert relative URLs to absolute
            absolute_url = urljoin(self.url, src)

            # Generate a safe local filename
            # Use index to avoid filename collisions
            original_name = Path(urlparse(absolute_url).path).name
            safe_name = f"{i:04d}_{original_name}"
            local_path = self.output_dir / 'images' / safe_name

            # Download and update reference
            if self._download_resource(absolute_url, local_path):
                img['src'] = f'images/{safe_name}'
                self.stats.images_downloaded += 1
            else:
                self.stats.images_failed += 1

    def _process_stylesheets(self, soup: BeautifulSoup) -> None:
        """Download CSS stylesheets referenced in the page.

        Args:
            soup: Parsed HTML document
        """
        stylesheets = soup.find_all('link', rel='stylesheet')
        logger.info(f"Processing {len(stylesheets)} stylesheets...")

        for i, link in enumerate(stylesheets, start=1):
            href = link.get('href')
            if not href:
                continue

            absolute_url = urljoin(self.url, href)

            # Generate local filename
            safe_name = f"style_{i:04d}.css"
            local_path = self.output_dir / 'css' / safe_name

            # Download and update reference
            if self._download_resource(absolute_url, local_path):
                link['href'] = f'css/{safe_name}'
                self.stats.stylesheets_downloaded += 1
            else:
                self.stats.stylesheets_failed += 1

    def _add_archive_notice(self, soup: BeautifulSoup) -> None:
        """Add a notice to the page indicating it's an archived copy.

        Args:
            soup: Parsed HTML document
        """
        if not soup.body:
            return

        # Create a styled notice banner
        notice = soup.new_tag(
            'div',
            style=(
                'background: #fef6e7; '
                'border: 2px solid #f39c12; '
                'border-radius: 4px; '
                'padding: 12px; '
                'margin: 16px; '
                'font-family: sans-serif;'
            )
        )
        notice.string = (
            '📦 Archived Wikipedia Page - '
            'This is an offline copy. Some features may not work.'
        )

        # Insert at the beginning of the body
        soup.body.insert(0, notice)

    def archive(self) -> bool:
        """Perform the archiving operation.

        Returns:
            True if successful, False otherwise

        Note:
            This is the main public method. It orchestrates the entire
            archiving process in a clear, sequential manner.
        """
        try:
            logger.info(f"Downloading page: {self.url}")

            # Download the main HTML page
            response = self.session.get(self.url, timeout=self.timeout)
            response.raise_for_status()

            # Parse with BeautifulSoup
            # lxml parser is faster but html.parser is in stdlib
            soup = BeautifulSoup(response.content, 'html.parser')

            # Create output directories
            self._create_directory_structure()

            # Download and update resources
            self._process_stylesheets(soup)
            self._process_images(soup)

            # Add informative notice
            self._add_archive_notice(soup)

            # Save the modified HTML
            output_file = self.output_dir / 'index.html'
            # Use prettify() for readable HTML output
            output_file.write_text(soup.prettify(), encoding='utf-8')

            # Report results
            self._print_summary(output_file)

            return True

        except requests.RequestException as e:
            logger.error(f"Failed to download page: {e}")
            return False
        except Exception as e:
            # Catch unexpected errors and provide helpful message
            logger.error(f"Unexpected error during archiving: {e}")
            logger.debug("", exc_info=True)  # Full traceback in debug mode
            return False

    def _print_summary(self, output_file: Path) -> None:
        """Print a summary of the archiving operation.

        Args:
            output_file: Path to the main HTML file
        """
        print("\n" + "=" * 60)
        print("Archive Complete")
        print("=" * 60)
        print(f"Output: {output_file}")
        print(f"\nResources downloaded:")
        print(f"  Images:      {self.stats.images_downloaded} "
              f"({self.stats.images_failed} failed)")
        print(f"  Stylesheets: {self.stats.stylesheets_downloaded} "
              f"({self.stats.stylesheets_failed} failed)")
        print(f"\nSuccess rate: {self.stats.success_rate():.1f}%")
        print("=" * 60)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed command-line arguments

    Note:
        Good CLI design is important. Help messages should be clear
        and examples should be provided.
    """
    parser = argparse.ArgumentParser(
        description='Archive Wikipedia pages for offline viewing.',
        epilog="""
Examples:
  %(prog)s https://en.wikipedia.org/wiki/Python_(programming_language)
  %(prog)s https://en.wikipedia.org/wiki/Linux -o linux_archive
  %(prog)s https://en.wikipedia.org/wiki/Coffee --verbose

The archived page will be saved as index.html in the output directory,
along with images/ and css/ subdirectories containing the resources.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'url',
        help='Wikipedia page URL to archive'
    )

    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=Path('wiki_archive'),
        help='output directory (default: wiki_archive)'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='request timeout in seconds (default: 30)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='enable verbose output'
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure)

    Note:
        Returning an exit code allows shell scripts to check if the
        operation succeeded. This is good Unix practice.
    """
    args = parse_args()

    # Configure logging level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Basic input validation
    if not args.url.startswith(('http://', 'https://')):
        print("Error: URL must start with http:// or https://", file=sys.stderr)
        return 1

    # Create and run archiver
    archiver = WikipediaArchiver(
        url=args.url,
        output_dir=args.output,
        timeout=args.timeout
    )

    success = archiver.archive()
    return 0 if success else 1


if __name__ == '__main__':
    # Clean exit on keyboard interrupt
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        sys.exit(130)  # Standard exit code for SIGINT
