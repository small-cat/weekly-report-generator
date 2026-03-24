"""Deduplicator module for removing duplicate articles."""
import hashlib
from typing import List, Dict


class Deduplicator:
    """Article deduplicator."""

    def __init__(self, logger):
        self.logger = logger

    def _normalize_title(self, title: str) -> str:
        """Normalize title for comparison.

        Args:
            title: Article title

        Returns:
            Normalized title
        """
        return title.strip().lower()

    def _generate_key(self, article: Dict) -> str:
        """Generate unique key for article.

        Args:
            article: Article dictionary

        Returns:
            Unique key
        """
        # Use URL if available, otherwise use normalized title
        if article.get('url'):
            return hashlib.md5(article['url'].encode('utf-8')).hexdigest()
        else:
            return hashlib.md5(self._normalize_title(article['title']).encode('utf-8')).hexdigest()

    def deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title or URL.

        Args:
            articles: List of article dictionaries

        Returns:
            Deduplicated article list
        """
        self.logger.info("Starting article deduplication...")

        seen_keys = set()
        deduplicated = []
        duplicates = 0

        for article in articles:
            key = self._generate_key(article)

            if key not in seen_keys:
                seen_keys.add(key)
                deduplicated.append(article)
            else:
                duplicates += 1
                self.logger.debug(f"  Duplicate found: {article['title'][:50]}...")

        self.logger.info(f"Deduplication done: {len(articles)} -> {len(deduplicated)} (removed {duplicates} duplicates)")

        return deduplicated

    def deduplicate_by_category(self, category_articles: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Deduplicate articles within each category.

        Args:
            category_articles: Dictionary mapping category to article list

        Returns:
            Deduplicated category articles
        """
        result = {}

        for category, articles in category_articles.items():
            result[category] = self.deduplicate(articles)

        return result

    def deduplicate_all(self, category_articles: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Deduplicate articles across all categories first, then distribute.

        Args:
            category_articles: Dictionary mapping category to article list

        Returns:
            Deduplicated category articles
        """
        self.logger.info("Starting global article deduplication...")

        # Collect all articles
        all_articles = []
        for category, articles in category_articles.items():
            for article in articles:
                all_articles.append(article)

        # Deduplicate globally
        deduplicated = self.deduplicate(all_articles)

        # Regroup by category
        result = {}
        for article in deduplicated:
            category = article['category']
            if category not in result:
                result[category] = []
            result[category].append(article)

        # Log per category
        for category, articles in result.items():
            self.logger.info(f"  {category}: {len(articles)} articles")

        total = sum(len(arts) for arts in result.values())
        self.logger.info(f"Total after deduplication: {total} articles")

        return result
