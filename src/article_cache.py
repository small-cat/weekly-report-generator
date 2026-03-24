"""Article cache module for storing and loading articles."""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ArticleCache:
    """Article cache for storing fetched articles."""

    def __init__(self, cache_dir: str = "./download"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_file_path(self, start_date: datetime) -> Path:
        """Get cache file path for given date.

        Args:
            start_date: Start date

        Returns:
            Cache file path
        """
        date_str = start_date.strftime('%Y-%m-%d')
        return self.cache_dir / f"articles_{date_str}.json"

    def _serialize_article(self, article: Dict) -> Dict:
        """Serialize article for JSON storage.

        Args:
            article: Article dictionary

        Returns:
            Serializable article dictionary
        """
        serialized = article.copy()
        # Convert datetime to string
        if serialized.get('published') and isinstance(serialized['published'], datetime):
            serialized['published'] = serialized['published'].isoformat()
        return serialized

    def _deserialize_article(self, article: Dict) -> Dict:
        """Deserialize article from JSON.

        Args:
            article: Article dictionary from JSON

        Returns:
            Article dictionary with datetime
        """
        deserialized = article.copy()
        # Convert string back to datetime
        if deserialized.get('published') and isinstance(deserialized['published'], str):
            deserialized['published'] = datetime.fromisoformat(deserialized['published'])
        return deserialized

    def save_articles(self, articles: Dict[str, List[Dict]], start_date: datetime) -> str:
        """Save articles to cache file.

        Args:
            articles: Dictionary mapping category to article list
            start_date: Start date

        Returns:
            Cache file path
        """
        cache_file = self._get_cache_file_path(start_date)

        # Serialize articles
        serialized = {}
        for category, article_list in articles.items():
            serialized[category] = [self._serialize_article(a) for a in article_list]

        # Save to file
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(serialized, f, ensure_ascii=False, indent=2)

        return str(cache_file)

    def load_articles(self, start_date: datetime) -> Optional[Dict[str, List[Dict]]]:
        """Load articles from cache file.

        Args:
            start_date: Start date

        Returns:
            Articles dictionary or None if cache doesn't exist
        """
        cache_file = self._get_cache_file_path(start_date)

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                serialized = json.load(f)

            # Deserialize articles
            deserialized = {}
            for category, article_list in serialized.items():
                deserialized[category] = [self._deserialize_article(a) for a in article_list]

            return deserialized
        except Exception:
            return None

    def cache_exists(self, start_date: datetime) -> bool:
        """Check if cache exists for given date.

        Args:
            start_date: Start date

        Returns:
            True if cache exists
        """
        cache_file = self._get_cache_file_path(start_date)
        return cache_file.exists()

    def get_cache_info(self, start_date: datetime) -> dict:
        """Get cache file info.

        Args:
            start_date: Start date

        Returns:
            Dictionary with cache info
        """
        cache_file = self._get_cache_file_path(start_date)

        if not cache_file.exists():
            return {"exists": False}

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            total = sum(len(articles) for articles in data.values())

            return {
                "exists": True,
                "path": str(cache_file),
                "size": os.path.getsize(cache_file),
                "categories": len(data),
                "total_articles": total
            }
        except Exception:
            return {"exists": False}
