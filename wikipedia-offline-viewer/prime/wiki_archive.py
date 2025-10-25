#!/usr/bin/env python3
"""
Wikipedia Archiver - The Prime Version

Chat, we're gonna download Wikipedia pages. Fast. Simple. No nonsense.
We're using ThreadPoolExecutor because async is overkill and threads are fine
for I/O bound work. Fight me.

Usage:
    python wiki_archive.py <url> [output_dir]
    python wiki_archive.py https://en.wikipedia.org/wiki/Vim
"""

from __future__ import annotations
import sys
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("pip install requests beautifulsoup4", file=sys.stderr)
    sys.exit(1)


@dataclass
class DownloadStats:
    """Track what we downloaded because metrics are cool."""
    images: int = 0
    css: int = 0
    failed: int = 0

    def report(self) -> None:
        total = self.images + self.css
        print(f"\nDownloaded: {total} resources ({self.images} images, {self.css} css)")
        if self.failed:
            print(f"Failed: {self.failed} (check your network)")


class WikiArchiver:
    """
    Not over-engineered. Just enough structure to be maintainable.
    We're doing concurrent downloads because waiting is for chumps.
    """

    def __init__(self, url: str, output: Path, workers: int = 8):
        self.url = url
        self.output = output
        self.workers = workers
        self.stats = DownloadStats()

        # Session for connection pooling - this matters for performance
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (WikiArchiver) Prime/1.0'
        })

    def _sanitize_filename(self, url: str, ext: str) -> str:
        """Generate clean filenames. No special chars that'll break filesystems."""
        path = urlparse(url).path
        name = Path(path).stem or 'file'
        # Keep it simple - alphanumeric and basic punctuation only
        clean = re.sub(r'[^a-zA-Z0-9_-]', '_', name)[:50]
        return f"{clean}.{ext}"

    def _download_resource(self, url: str, filepath: Path) -> bool:
        """Download a thing. Return success boolean. Don't overthink it."""
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            filepath.write_bytes(resp.content)
            return True
        except Exception:
            # Failed downloads shouldn't kill the whole archive
            return False

    def _download_images(self, soup: BeautifulSoup) -> None:
        """Concurrent image downloads because sequential is slow."""
        img_dir = self.output / 'img'
        img_dir.mkdir(exist_ok=True)

        images = soup.find_all('img')
        if not images:
            return

        print(f"Downloading {len(images)} images...", end='', flush=True)

        def download_img(img_tag) -> tuple[bool, Optional[str], Optional[str]]:
            src = img_tag.get('src') or img_tag.get('data-src')
            if not src:
                return False, None, None

            img_url = urljoin(self.url, src)
            ext = Path(urlparse(img_url).path).suffix.lstrip('.') or 'jpg'
            filename = self._sanitize_filename(img_url, ext)
            filepath = img_dir / filename

            success = self._download_resource(img_url, filepath)
            return success, src, f'img/{filename}' if success else None

        # ThreadPoolExecutor for I/O bound work - simple and effective
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = [executor.submit(download_img, img) for img in images]

            for future in as_completed(futures):
                success, old_src, new_src = future.result()
                if success:
                    self.stats.images += 1
                    # Update the HTML reference
                    for img in soup.find_all('img'):
                        if img.get('src') == old_src or img.get('data-src') == old_src:
                            img['src'] = new_src
                            if 'data-src' in img.attrs:
                                del img['data-src']
                else:
                    self.stats.failed += 1

        print(" done")

    def _download_css(self, soup: BeautifulSoup) -> None:
        """Download stylesheets. Wikipedia has a lot. Deal with it."""
        css_dir = self.output / 'css'
        css_dir.mkdir(exist_ok=True)

        stylesheets = soup.find_all('link', rel='stylesheet')
        if not stylesheets:
            return

        print(f"Downloading {len(stylesheets)} stylesheets...", end='', flush=True)

        def download_css(link_tag, idx: int) -> tuple[bool, Optional[str], Optional[str]]:
            href = link_tag.get('href')
            if not href:
                return False, None, None

            css_url = urljoin(self.url, href)
            filename = f"style_{idx:03d}.css"
            filepath = css_dir / filename

            success = self._download_resource(css_url, filepath)
            return success, href, f'css/{filename}' if success else None

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = [
                executor.submit(download_css, link, i)
                for i, link in enumerate(stylesheets)
            ]

            for future in as_completed(futures):
                success, old_href, new_href = future.result()
                if success:
                    self.stats.css += 1
                    for link in soup.find_all('link', rel='stylesheet'):
                        if link.get('href') == old_href:
                            link['href'] = new_href
                else:
                    self.stats.failed += 1

        print(" done")

    def archive(self) -> bool:
        """
        Do the thing. Download everything. Make it work offline.
        Returns success boolean for that clean exit code.
        """
        print(f"Archiving: {self.url}")

        try:
            # Get the page
            resp = self.session.get(self.url, timeout=20)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch page: {e}", file=sys.stderr)
            return False

        soup = BeautifulSoup(resp.content, 'html.parser')

        # Create output directory
        self.output.mkdir(parents=True, exist_ok=True)

        # Download assets concurrently - this is where we win on speed
        self._download_css(soup)
        self._download_images(soup)

        # Add banner so people know this is archived
        if soup.body:
            banner = soup.new_tag('div', style=(
                'position:sticky;top:0;background:#ff6b6b;color:#fff;'
                'padding:8px;text-align:center;font-weight:bold;z-index:9999;'
            ))
            banner.string = '⚡ OFFLINE ARCHIVE'
            soup.body.insert(0, banner)

        # Save the modified HTML
        output_file = self.output / 'index.html'
        output_file.write_text(str(soup), encoding='utf-8')

        print(f"\nSaved to: {output_file}")
        self.stats.report()
        return True


def main() -> int:
    """CLI entry point. Keep it simple."""
    if len(sys.argv) < 2:
        print("Usage: python wiki_archive.py <url> [output_dir]")
        print("Example: python wiki_archive.py https://en.wikipedia.org/wiki/Vim")
        return 1

    url = sys.argv[1]
    output = Path(sys.argv[2] if len(sys.argv) > 2 else 'archive')

    if not url.startswith(('http://', 'https://')):
        print("URL must start with http:// or https://", file=sys.stderr)
        return 1

    archiver = WikiArchiver(url, output, workers=8)
    success = archiver.archive()

    return 0 if success else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted", file=sys.stderr)
        sys.exit(130)
