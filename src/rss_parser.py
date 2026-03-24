"""RSS parser module for parsing OPML and RSS feeds."""
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional
import feedparser
from dateutil import parser as date_parser
from dateutil import tz


class RSSParser:
    """RSS and OPML parser."""

    def __init__(self, logger):
        self.logger = logger

    def parse_opml(self, opml_path: str) -> Dict[str, List[Dict]]:
        """Parse OPML file and extract RSS sources by category.

        Args:
            opml_path: Path to OPML file

        Returns:
            Dictionary mapping category name to list of feed info
        """
        self.logger.info(f"Parsing OPML file: {opml_path}")

        tree = ET.parse(opml_path)
        root = tree.getroot()

        categories = {}

        # Find body element
        body = root.find('body')
        if body is None:
            self.logger.warning("Body element not found")
            return categories

        # Recursively parse outlines
        self._parse_outline(body, categories, 'Uncategorized')

        self.logger.info(f"Parsed {len(categories)} categories")

        total_feeds = sum(len(feeds) for feeds in categories.values())
        self.logger.info(f"Total RSS sources: {total_feeds}")

        return categories

    def _parse_outline(self, element, categories: Dict, current_category: str):
        """Recursively parse outline elements.

        Args:
            element: XML element
            categories: Categories dictionary to populate
            current_category: Current category name
        """
        for outline in element.findall('outline'):
            text = outline.get('text', '')
            xml_url = outline.get('xmlUrl', '')
            html_url = outline.get('htmlUrl', '')
            description = outline.get('description', '')

            # Check if this is a feed (has xmlUrl) or a category
            if xml_url:
                # This is a feed
                feed_info = {
                    'name': text,
                    'url': xml_url,
                    'html_url': html_url,
                    'description': description,
                    'category': current_category
                }

                if current_category not in categories:
                    categories[current_category] = []

                categories[current_category].append(feed_info)
            else:
                # This is a category, recurse with new category name
                self._parse_outline(outline, categories, text)

    def fetch_feed(self, url: str):
        """Fetch RSS/Atom feed from URL.

        Args:
            url: RSS feed URL

        Returns:
            Parsed feed or None if failed
        """
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                self.logger.warning(f"Feed parsing may have issues: {url}")
            return feed
        except Exception as e:
            self.logger.error(f"Failed to fetch feed {url}: {str(e)}")
            return None

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats.

        Args:
            date_str: Date string

        Returns:
            Parsed datetime or None
        """
        if not date_str:
            return None

        try:
            # date_str is "Mon, 23 Mar 2026 01:08:03 GMT"
            dt = date_parser.parse(date_str)
            # Normalize to naive datetime (remove timezone info)
            if dt.tzinfo is not None:
                dt = dt.astimezone(tz.tzutc()).replace(tzinfo=None)
            return dt
        except Exception as e:
            self.logger.error(f"Failed to parse date {date_str}: {str(e)}")
            return None

    def filter_by_date(self, entries: List, start_date: datetime) -> List:
        """Filter entries by start date.

        Args:
            entries: List of feed entries
            start_date: Start date for filtering

        Returns:
            Filtered entries
        """
        # Normalize start_date to naive datetime
        if start_date.tzinfo is not None:
            start_date = start_date.replace(tzinfo=None)

        filtered = []

        for entry in entries:
            published = None

            # Try different date fields
            if hasattr(entry, 'published'):
                published = self.parse_date(entry.published)
            elif hasattr(entry, 'updated'):
                published = self.parse_date(entry.updated)
            elif hasattr(entry, 'dc_date'):
                published = self.parse_date(entry.dc_date)

            if published and published >= start_date:
                filtered.append(entry)

        return filtered

    def extract_article_info(self, entry, source_name: str, category: str) -> Dict:
        """Extract article information from entry.

        Args:
            entry: Feed entry
            source_name: Source name
            category: Category name

        Returns:
            Article dictionary
        """
        # Get title
        title = getattr(entry, 'title', 'No Title')

        # Get link
        link = ''
        if hasattr(entry, 'links') and entry.links:
            for l in entry.links:
                if l.get('type', '').startswith('text/html'):
                    link = l.get('href', '')
                    break
        if not link:
            link = getattr(entry, 'link', '')

        # Get published date
        published = None
        if hasattr(entry, 'published'):
            published = self.parse_date(entry.published)
        elif hasattr(entry, 'updated'):
            published = self.parse_date(entry.updated)
        elif hasattr(entry, 'dc_date'):
            published = self.parse_date(entry.dc_date)

        # Get summary
        summary = getattr(entry, 'summary', '') or getattr(entry, 'description', '')

        # Get content
        content = ''
        if hasattr(entry, 'content'):
            for c in entry.content:
                if c.type.startswith('text/html'):
                    content = c.value
                    break

        return {
            'title': title,
            'url': link,
            'published': published,
            'source': source_name,
            'category': category,
            'summary': summary,
            'content': content,
            'claude_summary': ''
        }

    def fetch_articles_from_category(self, feeds: List[Dict], start_date: datetime) -> List[Dict]:
        """Fetch articles from multiple feeds in a category.

        Args:
            feeds: List of feed info dictionaries
            start_date: Start date for filtering

        Returns:
            List of article dictionaries
        """
        articles = []

        for feed_info in feeds:
            self.logger.info(f"  Fetching: {feed_info['name']}")

            feed = self.fetch_feed(feed_info['url'])
            if feed is None:
                continue

            filtered_entries = self.filter_by_date(feed.entries, start_date)

            if filtered_entries:
                self.logger.info(f"    Found {len(filtered_entries)} articles this week")
            else:
                self.logger.debug(f"    No new articles this week")

            for entry in filtered_entries:
                article = self.extract_article_info(
                    entry,
                    feed_info['name'],
                    feed_info['category']
                )
                articles.append(article)

        return articles

    def fetch_all_articles(self, categories: Dict[str, List[Dict]], start_date: datetime) -> Dict[str, List[Dict]]:
        """Fetch all articles from all categories.

        Args:
            categories: Dictionary mapping category to feed list
            start_date: Start date for filtering

        Returns:
            Dictionary mapping category to article list
        """
        self.logger.info("Starting to fetch RSS articles...")

        result = {}

        for category, feeds in categories.items():
            self.logger.info(f"Processing category: {category}")
            articles = self.fetch_articles_from_category(feeds, start_date)
            result[category] = articles
            self.logger.info(f"  {category}: {len(articles)} articles")

        total = sum(len(arts) for arts in result.values())
        self.logger.info(f"Total articles fetched: {total}")

        return result
