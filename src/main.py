"""Main entry point for weekly reports generator."""
import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from logger import Logger
from rss_parser import RSSParser
from deduplicator import Deduplicator
from claude_client import ClaudeClient
from template_renderer import TemplateRenderer
from git_publisher import GitPublisher
from article_cache import ArticleCache


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Weekly Tech Reports Generator'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='./config/config.yaml',
        help='Config file path'
    )
    parser.add_argument(
        '--template',
        type=str,
        default='./template.md',
        help='Template file path'
    )
    parser.add_argument(
        '--skip-git',
        action='store_true',
        help='Skip Git push'
    )
    parser.add_argument(
        '--week-number',
        type=int,
        default=None,
        help='Week number'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        default=None,
        help='Start date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--force-refetch',
        action='store_true',
        help='Force refetch articles, ignore cache'
    )

    return parser.parse_args()


def main():
    """Main function."""
    # Parse arguments
    args = parse_args()

    # Load configuration
    config = Config(args.config)

    # Ensure directories exist
    config.ensure_directories()

    # Initialize logger
    logger = Logger(config.log_dir)
    logger.log_start()

    # Override start date if provided
    if args.start_date:
        config.config['rss']['start_date'] = args.start_date
        logger.info(f"Using specified start date: {args.start_date}")

    # Get start date
    start_date = config.get_start_date_as_datetime()
    logger.info(f"Week start date: {start_date.strftime('%Y-%m-%d')}")

    # Initialize cache
    cache = ArticleCache(config.download_dir)

    # Check cache
    use_cache = not args.force_refetch and cache.cache_exists(start_date)
    cache_info = cache.get_cache_info(start_date)

    if use_cache:
        logger.info(f"Found article cache: {cache_info['path']}")
        logger.info(f"Cache contains {cache_info['total_articles']} articles in {cache_info['categories']} categories")
        logger.info("Will load articles from cache, skip RSS fetching")

    try:
        # Step 1: Parse OPML (only if not using cache)
        if not use_cache:
            logger.info("=" * 30)
            logger.info("Step 1: Parse RSS sources")
            logger.info("=" * 30)
            rss_parser = RSSParser(logger)
            categories = rss_parser.parse_opml(config.opml_path)

            # Step 2: Fetch articles
            logger.info("=" * 30)
            logger.info("Step 2: Fetch articles")
            logger.info("=" * 30)
            category_articles = rss_parser.fetch_all_articles(categories, start_date)

            # Step 3: Deduplicate
            logger.info("=" * 30)
            logger.info("Step 3: Deduplicate articles")
            logger.info("=" * 30)
            deduplicator = Deduplicator(logger)
            category_articles = deduplicator.deduplicate_all(category_articles)

            # Save to cache
            logger.info("=" * 30)
            logger.info("Step 4: Save articles to cache")
            logger.info("=" * 30)
            cache_file = cache.save_articles(category_articles, start_date)
            logger.info(f"Articles saved to: {cache_file}")
        else:
            # Load from cache
            logger.info("=" * 30)
            logger.info("Step 1-3: Load articles from cache")
            logger.info("=" * 30)
            category_articles = cache.load_articles(start_date)
            total = sum(len(arts) for arts in category_articles.values())
            logger.info(f"Loaded {total} articles from cache")

        # Step 5: Process with Claude
        logger.info("=" * 30)
        logger.info("Step 5: Generate summaries with Claude")
        logger.info("=" * 30)
        claude_client = ClaudeClient(logger, config)
        category_articles = claude_client.process_category_articles(category_articles)

        # Step 6: Render template
        logger.info("=" * 30)
        logger.info("Step 6: Render template")
        logger.info("=" * 30)
        renderer = TemplateRenderer(logger, config)
        content = renderer.render(args.template, category_articles, args.week_number)

        # Step 7: Save output
        logger.info("=" * 30)
        logger.info("Step 7: Save weekly report")
        logger.info("=" * 30)
        output_file = renderer.save_output(content, config.output_dir, args.week_number)

        # Step 8: Git push
        if not args.skip_git:
            logger.info("=" * 30)
            logger.info("Step 8: Push to GitHub")
            logger.info("=" * 30)
            publisher = GitPublisher(logger, config)
            success = publisher.commit_and_push(output_file)

            if success:
                logger.info("Git push successful!")
            else:
                logger.warning("Git push failed, please handle manually")

        # Summary
        logger.info("=" * 30)
        logger.info("Done!")
        logger.info("=" * 30)

        total_articles = sum(len(arts) for arts in category_articles.values())
        summary = {
            "Start Date": start_date.strftime('%Y-%m-%d'),
            "Output File": output_file,
            "Total Articles": total_articles,
            "Categories": len(category_articles),
            "Data Source": "Cache" if use_cache else "RSS Fetch"
        }
        logger.log_summary(summary)

        logger.log_end()

    except Exception as e:
        logger.error(f"Program error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    main()
