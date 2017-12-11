"""Utilities for crawling and scraping emails."""

from email.utils import getaddresses
from itertools import chain
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from typing import Set, NamedTuple, Optional, Iterable
from urllib.parse import urlparse, urljoin

from lxml import etree
import requests
from requests.utils import prepend_scheme_if_needed

REQUEST_TIMEOUT_SECONDS = 10.0

FetchResult = NamedTuple('FetchResult', (
    ('url', str),
    ('successful', bool),
    ('page', Optional[etree.Element])
))


def linked_urls(page: etree.Element, base_url: str) -> Set[str]:
    """Return hyperlinked urls from page within same domain."""
    urls = (
        urljoin(base_url, url)
        for url in page.xpath("//a/@href")
    )
    target_domain = urlparse(base_url).netloc
    return {
        url
        for url in urls
        if urlparse(url).netloc == target_domain
    }


def emails(page: etree.Element) -> Set[str]:
    """Extract email addresses from given page."""
    return {
        address.split('?', 1)[0]
        for _, address in getaddresses(
            page.xpath("//a[starts-with(@href, 'mailto:')]/@href")
        )
        if '@' in address
    }


def fetch(url: str, timeout_seconds: float = REQUEST_TIMEOUT_SECONDS) -> FetchResult:
    try:
        page = etree.HTML(
            requests.get(url, timeout=timeout_seconds).content
        )
    except Exception:
        page = None
    return FetchResult(
        url=url,
        successful=page is not None,
        page=page
    )


def crawl_emails(initial_url: str) -> Iterable[str]:
    """Emit email addresses discovered by crawling the specified URL."""
    frontier = {prepend_scheme_if_needed(initial_url, 'http'),}
    visited_urls = set()
    emitted_emails = set()

    with ThreadPool(processes=cpu_count()) as pool:
        while frontier:
            results = pool.map_async(fetch, frontier).get()
            visited_urls.update(result.url for result in results)
            successful_results = [result for result in results if result.successful]

            frontier = {
                url.lower()
                for result in successful_results
                for url in linked_urls(result.page, result.url)
            } - visited_urls

            scraped_emails = {
                email.lower()
                for r in successful_results
                for email in emails(r.page)
            } - emitted_emails
            yield from scraped_emails
            emitted_emails.update(scraped_emails)
