"""Claude CLI client module for generating article summaries."""
import subprocess
import json
import time
from typing import Dict, Optional


class ClaudeClient:
    """Claude CLI client."""

    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.claude_command = config.claude_command
        self.claude_model = config.claude_model

    def _build_prompt(self, article: Dict) -> str:
        """Build prompt for Claude.

        Args:
            article: Article dictionary

        Returns:
            Prompt string
        """
        prompt = f"""Please generate a 1-2 paragraph concise summary in Chinese for the following article:

Title: {article['title']}
Source: {article['source']}
Link: {article['url']}

Requirements:
1. Summarize the main content in 1-2 paragraphs in Chinese
2. Keep it objective and accurate
3. If it's a news article, describe the main content; if it's a technical article, briefly explain the key technical points
4. Do not exceed 150 words

Please output only the summary, without any prefix or formatting."""
        return prompt

    def process_article(self, article: Dict, max_retries: int = 2) -> Dict:
        """Process a single article with Claude.

        Args:
            article: Article dictionary
            max_retries: Maximum retry attempts

        Returns:
            Updated article dictionary with Claude summary
        """
        prompt = self._build_prompt(article)

        for attempt in range(max_retries):
            try:
                # Build command
                cmd = [
                    "claude",
                    self.claude_command,
                    "-p",
                    prompt
                ]

                # Run Claude CLI
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode == 0:
                    summary = result.stdout.strip()
                    article['claude_summary'] = summary
                    self.logger.debug(f"  Successfully processed: {article['title'][:30]}...")
                    return article
                else:
                    self.logger.warning(f"  Claude failed (attempt {attempt + 1}/{max_retries}): {article['title'][:30]}...")
                    if attempt < max_retries - 1:
                        time.sleep(2)

            except subprocess.TimeoutExpired:
                self.logger.warning(f"  Claude timeout (attempt {attempt + 1}/{max_retries}): {article['title'][:30]}...")
                if attempt < max_retries - 1:
                    time.sleep(2)
            except Exception as e:
                self.logger.error(f"  Claude error: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)

        # All retries failed
        article['claude_summary'] = article.get('summary', '')[:150]
        self.logger.error(f"  Processing failed, using original summary: {article['title'][:30]}...")
        return article

    def process_articles(self, articles: list, skip_existing: bool = True) -> list:
        """Process multiple articles with Claude.

        Args:
            articles: List of article dictionaries
            skip_existing: Skip articles that already have claude_summary

        Returns:
            List of processed articles
        """
        total = len(articles)
        self.logger.info(f"Starting to process {total} articles with Claude...")

        processed = 0
        skipped = 0
        failed = 0

        for i, article in enumerate(articles):
            # Skip if already processed
            if skip_existing and article.get('claude_summary'):
                skipped += 1
                continue

            # Process article
            processed_article = self.process_article(article)

            if processed_article.get('claude_summary'):
                processed += 1
            else:
                failed += 1

            # Progress update every 10 articles
            if (i + 1) % 10 == 0:
                self.logger.info(f"  Progress: {i + 1}/{total}")

            # Small delay to avoid rate limiting
            time.sleep(0.5)

        self.logger.info(f"Claude processing done: {processed} processed, {skipped} skipped, {failed} failed")

        return articles

    def process_category_articles(self, category_articles: Dict[str, list]) -> Dict[str, list]:
        """Process articles in all categories.

        Args:
            category_articles: Dictionary mapping category to article list

        Returns:
            Processed category articles
        """
        result = {}

        for category, articles in category_articles.items():
            self.logger.info(f"Processing category: {category}")
            result[category] = self.process_articles(articles)

        return result
