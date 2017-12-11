#!/usr/bin/python

"""Command-line interface for email crawler."""

import argparse

from email_crawler import crawler

parser = argparse.ArgumentParser()
parser.add_argument('url', help='initial URL or domain', type=str)


def main():
    """Entrypoint for CLI."""
    args = parser.parse_args()
    print("Found these email addresses:")
    for email_address in crawler.crawl_emails(args.url):
        print(email_address)


if __name__ == '__main__':
    main()
