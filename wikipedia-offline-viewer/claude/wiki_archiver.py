#!/usr/bin/env python3
"""
Wikipedia Page Archiver - Claude's Implementation

This tool downloads Wikipedia pages for offline viewing, including images and
stylesheets. It aims to balance simplicity with robustness, prioritizing a
good user experience with helpful error messages and progress feedback.

Design philosophy:
- Clear > Clever: Code should be understandable
- Helpful > Minimal: Good error messages and guidance
- Pragmatic > Perfect: Ship working code, iterate later
- Safe by default: Validate inputs, handle errors gracefully

Usage:
    python wiki_archiver.py https://en.wikipedia.org/wiki/Python
    python wiki_archiver.py --help
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(
        f"\nError: Missing required package '{e.name}'",
        file=sys.stderr
    )
    print(
        "\nTo install dependencies, run:",
        "\n  pip install -r requirements.txt",
        "\nor:",
        "\n  pip install requests beautifulsoup4",
        file=sys.stderr
    )
    sys.exit(1)


@dataclass
class ArchiveResult:
    """Results from an archiving operation.

    I like tracking both successes and failures - it helps users understand
    what happened and makes debugging easier.
    """
    images_success: int = 0
    images_failed: int = 0
    css_success: int = 0
    css_failed: int = 0

    @property
    def total_success(self) -> int:
        return self.images_success + self.css_success

    @property
    def total_failed(self) -> int:
        return self.images_failed + self.css_failed

    @property
    def total_attempted(self) -> int:
        return self.total_success + self.total_failed

    def print_summary(self) -> None:
        """Print a friendly summary of what was archived."""
        print("\n" + "=" * 70)
        print("📦 Archive Summary")
        print("=" * 70)
        print(f"✓ Successfully downloaded: {self.total_success} resources")
        print(f"  - Images: {self.images_success}")
        print(f"  - Stylesheets: {self.css_success}")

        if self.total_failed > 0:
            print(f"\n⚠ Failed downloads: {self.total_failed} resources")
            print(f"  - Images: {self.images_failed}")
            print(f"  - Stylesheets: {self.css_failed}")
            print("\nNote: Failed downloads won't break the archive, but some")
            print("      content may be missing. This often happens with")
            print("      external resources or temporary network issues.")

        print("=" * 70)


class WikipediaArchiver:
    """
    Downloads Wikipedia pages with all assets for offline viewing.

    I chose ThreadPoolExecutor over async because:
    1. Simpler to reason about (4 hour time constraint)
    2. Good enough performance for typical Wikipedia pages
    3. Better error handling visibility
    4. Easier to add retry logic
    """

    def __init__(
        self,
        url: str,
        output_dir: Path,
        max_workers: int = 8,
        timeout: int = 15,
        max_retries: int = 2
    ):
        self.url = url
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.timeout = timeout
        self.max_retries = max_retries
        self.result = ArchiveResult()

        # Session for connection pooling - meaningful performance improvement
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (WikipediaArchiver; Claude) Python/requests'
        })

    def _validate_url(self) -> tuple[bool, Optional[str]]:
        """
        Validate the Wikipedia URL before attempting download.

        Returns: (is_valid, error_message)

        I like validating inputs early with helpful error messages rather
        than letting users discover issues after waiting for downloads.
        """
        if not self.url.startswith(('http://', 'https://')):
            return False, "URL must start with http:// or https://"

        parsed = urlparse(self.url)
        if 'wikipedia.org' not in parsed.netloc:
            return False, (
                "This tool is designed for Wikipedia pages.\n"
                f"  URL hostname: {parsed.netloc}\n"
                "  Expected: *.wikipedia.org"
            )

        return True, None

    def _download_with_retry(
        self,
        url: str,
        description: str = "resource"
    ) -> Optional[bytes]:
        """
        Download a resource with simple retry logic.

        Exponential backoff helps with temporary network issues without
        hammering servers. I kept it simple - 2 retries is usually enough.
        """
        for attempt in range(self.max_retries + 1):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.content

            except requests.Timeout:
                if attempt < self.max_retries:
                    wait = 2 ** attempt  # 1s, 2s
                    time.sleep(wait)
                else:
                    # Only print for final failure to avoid spam
                    print(f"  ⏱ Timeout downloading {description}", file=sys.stderr)

            except requests.RequestException as e:
                if attempt < self.max_retries:
                    time.sleep(1)
                else:
                    # Helpful error messages, but not overwhelming
                    if response.status_code == 404:
                        print(f"  ✗ Not found: {description}", file=sys.stderr)
                    elif response.status_code == 403:
                        print(f"  ✗ Access denied: {description}", file=sys.stderr)
                    # No need to print for every failed resource

        return None

    def _sanitize_filename(self, url: str, prefix: str, extension: str) -> str:
        """
        Generate safe, collision-free filenames.

        I use a hash suffix to prevent collisions while keeping the original
        name for easier debugging. It's a nice middle ground.
        """
        import hashlib

        parsed = urlparse(url)
        original = Path(parsed.path).stem or 'resource'

        # Keep alphanumeric and common punctuation
        clean = ''.join(c if c.isalnum() or c in '-_' else '_' for c in original)
        clean = clean[:40]  # Reasonable length

        # Add hash to prevent collisions
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]

        return f"{prefix}_{clean}_{url_hash}.{extension}"

    def _download_images(self, soup: BeautifulSoup) -> None:
        """Download images concurrently with progress indication."""
        images = soup.find_all('img')
        if not images:
            return

        img_dir = self.output_dir / 'images'
        img_dir.mkdir(exist_ok=True)

        print(f"\n📷 Downloading {len(images)} images...")

        def download_image(img_tag) -> tuple[bool, Optional[str], Optional[str]]:
            src = img_tag.get('src') or img_tag.get('data-src')
            if not src:
                return False, None, None

            img_url = urljoin(self.url, src)
            ext = Path(urlparse(img_url).path).suffix.lstrip('.') or 'jpg'
            filename = self._sanitize_filename(img_url, 'img', ext)
            filepath = img_dir / filename

            content = self._download_with_retry(img_url, f"image {filename}")

            if content:
                try:
                    filepath.write_bytes(content)
                    return True, src, f'images/{filename}'
                except IOError as e:
                    print(f"  ✗ Failed to save {filename}: {e}", file=sys.stderr)
                    return False, src, None

            return False, src, None

        # Concurrent downloads with progress tracking
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(download_image, img): img for img in images}

            completed = 0
            for future in as_completed(futures):
                success, old_src, new_src = future.result()
                completed += 1

                # Simple progress indicator every 10%
                if completed % max(1, len(images) // 10) == 0:
                    percent = (completed / len(images)) * 100
                    print(f"  Progress: {completed}/{len(images)} ({percent:.0f}%)")

                if success:
                    self.result.images_success += 1
                    # Update HTML references
                    for img in soup.find_all('img'):
                        if img.get('src') == old_src or img.get('data-src') == old_src:
                            img['src'] = new_src
                            # Remove data-src to avoid lazy loading issues
                            img.attrs.pop('data-src', None)
                else:
                    self.result.images_failed += 1

        print(f"  ✓ Images complete: {self.result.images_success} succeeded")

    def _download_stylesheets(self, soup: BeautifulSoup) -> None:
        """Download CSS stylesheets concurrently."""
        stylesheets = soup.find_all('link', rel='stylesheet')
        if not stylesheets:
            return

        css_dir = self.output_dir / 'css'
        css_dir.mkdir(exist_ok=True)

        print(f"\n🎨 Downloading {len(stylesheets)} stylesheets...")

        def download_css(link_tag, index: int) -> tuple[bool, Optional[str], Optional[str]]:
            href = link_tag.get('href')
            if not href:
                return False, None, None

            css_url = urljoin(self.url, href)
            filename = self._sanitize_filename(css_url, f'style_{index:03d}', 'css')
            filepath = css_dir / filename

            content = self._download_with_retry(css_url, f"stylesheet {filename}")

            if content:
                try:
                    filepath.write_bytes(content)
                    return True, href, f'css/{filename}'
                except IOError as e:
                    print(f"  ✗ Failed to save {filename}: {e}", file=sys.stderr)
                    return False, href, None

            return False, href, None

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(download_css, link, i): link
                for i, link in enumerate(stylesheets)
            }

            for future in as_completed(futures):
                success, old_href, new_href = future.result()

                if success:
                    self.result.css_success += 1
                    for link in soup.find_all('link', rel='stylesheet'):
                        if link.get('href') == old_href:
                            link['href'] = new_href
                else:
                    self.result.css_failed += 1

        print(f"  ✓ Stylesheets complete: {self.result.css_success} succeeded")

    def _add_archive_notice(self, soup: BeautifulSoup) -> None:
        """Add a friendly notice banner to the archived page."""
        if not soup.body:
            return

        notice = soup.new_tag(
            'div',
            style=(
                'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
                'color: white; padding: 12px 20px; margin: 0; '
                'font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; '
                'font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); '
                'border-bottom: 3px solid rgba(255,255,255,0.2);'
            )
        )
        notice.string = '📦 Offline Archive | This is a saved copy of a Wikipedia page'
        soup.body.insert(0, notice)

    def archive(self) -> bool:
        """
        Main archiving operation.

        Returns True if successful, False otherwise.

        I structure this as a clear sequence of steps so it's easy to
        understand what's happening and where failures might occur.
        """
        # Validate before doing any work
        is_valid, error_msg = self._validate_url()
        if not is_valid:
            print(f"\n❌ Invalid URL: {error_msg}", file=sys.stderr)
            return False

        print(f"\n🌐 Fetching Wikipedia page: {self.url}")

        # Download main page
        try:
            response = self.session.get(self.url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"\n❌ Failed to fetch page: {e}", file=sys.stderr)
            print("\nTroubleshooting tips:", file=sys.stderr)
            print("  - Check your internet connection", file=sys.stderr)
            print("  - Verify the URL is correct", file=sys.stderr)
            print("  - Try again in a moment (temporary server issues)", file=sys.stderr)
            return False

        print("  ✓ Page fetched successfully")

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Create output directory
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            print(f"\n📁 Output directory: {self.output_dir}")
        except OSError as e:
            print(f"\n❌ Failed to create output directory: {e}", file=sys.stderr)
            return False

        # Download resources concurrently
        self._download_stylesheets(soup)
        self._download_images(soup)

        # Add helpful banner
        self._add_archive_notice(soup)

        # Save final HTML
        output_file = self.output_dir / 'index.html'
        try:
            output_file.write_text(str(soup), encoding='utf-8')
            print(f"\n💾 Saved to: {output_file}")
        except IOError as e:
            print(f"\n❌ Failed to save HTML file: {e}", file=sys.stderr)
            return False

        # Print summary
        self.result.print_summary()

        # Provide next steps
        print("\n📖 To view the archive:")
        print(f"   open {output_file}")
        print(f"   or: python -m http.server --directory {self.output_dir}")

        return True


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    I like argparse for its automatic help generation and validation.
    The extra lines of code are worth it for better UX.
    """
    parser = argparse.ArgumentParser(
        description='Archive Wikipedia pages for offline viewing with all assets.',
        epilog="""
Examples:
  # Basic usage
  %(prog)s https://en.wikipedia.org/wiki/Python_(programming_language)

  # Specify output directory
  %(prog)s https://en.wikipedia.org/wiki/Linux -o linux_archive

  # Adjust concurrency for slower connections
  %(prog)s https://en.wikipedia.org/wiki/Coffee --workers 4

Tips:
  - The archive includes images and CSS for full offline viewing
  - Failed resources won't break the archive
  - Use --workers to adjust download concurrency
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
        default=Path('wikipedia_archive'),
        help='output directory (default: wikipedia_archive)'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=8,
        help='number of concurrent downloads (default: 8)'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=15,
        help='request timeout in seconds (default: 15)'
    )

    parser.add_argument(
        '--retries',
        type=int,
        default=2,
        help='number of retry attempts (default: 2)'
    )

    return parser.parse_args()


def main() -> int:
    """
    Main entry point.

    I return proper exit codes so the tool plays nicely with shell scripts
    and CI/CD pipelines.
    """
    args = parse_arguments()

    print("=" * 70)
    print("📦 Wikipedia Page Archiver")
    print("=" * 70)

    archiver = WikipediaArchiver(
        url=args.url,
        output_dir=args.output,
        max_workers=args.workers,
        timeout=args.timeout,
        max_retries=args.retries
    )

    success = archiver.archive()

    return 0 if success else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user", file=sys.stderr)
        print("Partial archive may exist in output directory.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        # Catch any unexpected errors with helpful guidance
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        print("\nThis is likely a bug. Please check:", file=sys.stderr)
        print("  - Your Python version (3.8+ required)", file=sys.stderr)
        print("  - Dependencies are installed correctly", file=sys.stderr)
        sys.exit(1)
