"""Configuration management module."""
import os
import yaml
from pathlib import Path
from datetime import datetime, timedelta


class Config:
    """Configuration loader and manager."""

    def __init__(self, config_path: str = "./config/config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @property
    def claude_command(self) -> str:
        """Get Claude CLI command."""
        return self.config.get('claude', {}).get('command', 'claude-sonnet')

    @property
    def claude_model(self) -> str:
        """Get Claude model name."""
        return self.config.get('claude', {}).get('model', 'claude-sonnet-4-6')

    @property
    def github_repo_url(self) -> str:
        """Get GitHub repository URL."""
        return self.config.get('github', {}).get('repo_url', '')

    @property
    def github_branch(self) -> str:
        """Get GitHub branch."""
        return self.config.get('github', {}).get('branch', 'main')

    @property
    def opml_path(self) -> str:
        """Get OPML file path."""
        return self.config.get('rss', {}).get('opml_path', './ReadSource.opml')

    @property
    def start_date(self) -> str:
        """Get start date for filtering."""
        return self.config.get('rss', {}).get('start_date', 'this_week')

    @property
    def output_dir(self) -> str:
        """Get output directory."""
        return self.config.get('output', {}).get('output_dir', './output')

    @property
    def download_dir(self) -> str:
        """Get download directory."""
        return self.config.get('output', {}).get('download_dir', './download')

    @property
    def log_dir(self) -> str:
        """Get log directory."""
        return self.config.get('output', {}).get('log_dir', './logs')

    def get_start_date_as_datetime(self) -> datetime:
        """Get start date as datetime object."""
        if self.start_date == 'this_week':
            # Get Monday of current week
            today = datetime.now()
            monday = today - timedelta(days=today.weekday())
            return monday.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            return datetime.strptime(self.start_date, '%Y-%m-%d')

    def ensure_directories(self):
        """Ensure all required directories exist."""
        for dir_path in [self.output_dir, self.download_dir, self.log_dir]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
