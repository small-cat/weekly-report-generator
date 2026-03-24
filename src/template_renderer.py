"""Template renderer module for generating weekly reports."""
from datetime import datetime
from typing import Dict, List
import re


class TemplateRenderer:
    """Template renderer for weekly reports."""

    # Mapping from OPML categories to template sections (Chinese keys to match OPML)
    CATEGORY_MAPPING = {
        'AI-related': 'Industry News',
        'Hot News': 'Industry News',
        'Tech Blogs': 'Tech Blogs',
        'Personal Blogs': 'Featured Articles',
        'Tech Weekly': 'Tech Weekly',
        'Open Source': 'Open Source',
        'Resources': 'Resources',
        'Community': 'Community Picks',
        'Tools': 'Tools',
    }

    # OPML category names (Chinese) to template section mapping
    SECTION_MAPPING = {
        'AI相关': 'Industry News',
        '热点资讯': 'Industry News',
        '技术博客': 'Tech Blogs',
        '个人博客': 'Featured Articles',
        '技术周刊': 'Tech Weekly',
        '开源项目': 'Open Source',
        '资源': 'Resources',
        '社区': 'Community Picks',
        '工具': 'Tools',
    }

    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

    def _get_template_section(self, category: str) -> str:
        """Map OPML category to template section.

        Args:
            category: OPML category name

        Returns:
            Template section name
        """
        return self.SECTION_MAPPING.get(category, 'Featured Articles')

    def _generate_article_content(self, article: Dict) -> str:
        """Generate article content for template.

        Args:
            article: Article dictionary

        Returns:
            Formatted article content
        """
        summary = article.get('claude_summary', article.get('summary', ''))
        url = article.get('url', '')
        title = article.get('title', '')

        # Clean up summary - remove HTML tags if any
        summary = re.sub(r'<[^>]+>', '', summary)

        content = f"### [{title}]({url})\n\n"
        content += f">{summary}\n\n"

        return content

    def _generate_section_content(self, articles: List[Dict]) -> str:
        """Generate content for a section.

        Args:
            articles: List of articles

        Returns:
            Section content
        """
        if not articles:
            return ""

        content = ""
        for article in articles:
            content += self._generate_article_content(article)

        return content

    def _calculate_week_number(self, date: datetime) -> int:
        """Calculate week number of the year.

        Args:
            date: Date object

        Returns:
            Week number
        """
        return date.isocalendar()[1]

    def render(self, template_path: str, category_articles: Dict[str, List[Dict]],
               week_number: int = None) -> str:
        """Render template with articles.

        Args:
            template_path: Path to template file
            category_articles: Dictionary mapping category to article list
            week_number: Week number (auto-calculate if not provided)

        Returns:
            Rendered content
        """
        self.logger.info("Starting template rendering...")

        # Read template
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        # Get current date and week number
        today = datetime.now()
        if week_number is None:
            week_number = self._calculate_week_number(today)

        date_str = today.strftime('%Y-%m-%d')

        # Replace date and week number in template
        template = template.replace('2026-XX-XX', date_str)
        template = template.replace('Week XX', f'Week {week_number}')

        # Group articles by template sections
        sections = {
            'Industry News': [],
            'Featured Articles': [],
            'Tech Blogs': [],
            'Tech Weekly': [],
            'Open Source': [],
            'Tools': [],
            'Resources': [],
            'Community Picks': [],
        }

        for category, articles in category_articles.items():
            section = self._get_template_section(category)
            if section in sections:
                sections[section].extend(articles)

        # Log section statistics
        for section, articles in sections.items():
            if articles:
                self.logger.info(f"  {section}: {len(articles)} articles")

        # Build content for each section
        content = ""

        # Industry News
        if sections['Industry News']:
            content += "## Industry News\n\n"
            content += self._generate_section_content(sections['Industry News'])

        # Featured Articles
        if sections['Featured Articles']:
            content += "## Featured Articles\n\n"
            content += self._generate_section_content(sections['Featured Articles'])

        # Tech Blogs
        if sections['Tech Blogs']:
            content += "## Tech Blogs\n\n"
            content += self._generate_section_content(sections['Tech Blogs'])

        # Tech Weekly
        if sections['Tech Weekly']:
            content += "## Tech Weekly\n\n"
            content += self._generate_section_content(sections['Tech Weekly'])

        # Open Source
        if sections['Open Source']:
            content += "## Open Source\n\n"
            content += self._generate_section_content(sections['Open Source'])

        # Tools
        if sections['Tools']:
            content += "## Tools\n\n"
            content += self._generate_section_content(sections['Tools'])

        # Resources
        if sections['Resources']:
            content += "## Resources\n\n"
            content += self._generate_section_content(sections['Resources'])

        # Community Picks
        if sections['Community Picks']:
            content += "## Community Picks\n\n"
            content += self._generate_section_content(sections['Community Picks'])

        # Replace content placeholder (XXXX in template)
        template = template.replace('XXXX', content.strip())

        # Count total articles
        total = sum(len(arts) for arts in sections.values())
        self.logger.info(f"Template rendering done: {total} articles")

        return template

    def save_output(self, content: str, output_dir: str, week_number: int = None) -> str:
        """Save rendered content to file.

        Args:
            content: Rendered content
            output_dir: Output directory
            week_number: Week number

        Returns:
            Output file path
        """
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        today = datetime.now()
        if week_number is None:
            week_number = self._calculate_week_number(today)

        filename = f"weekly-report-{today.strftime('%Y-%m-%d')}-w{week_number}.md"
        filepath = output_path / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        self.logger.info(f"Report saved to: {filepath}")

        return str(filepath)
