"""Git publisher module for pushing weekly reports to GitHub."""
import os
import subprocess
from datetime import datetime
from pathlib import Path
import shutil


class GitPublisher:
    """Git publisher for weekly reports."""

    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.repo_url = config.github_repo_url
        self.branch = config.github_branch

    def _run_command(self, cmd: list, cwd: str = None) -> tuple:
        """Run shell command.

        Args:
            cmd: Command list
            cwd: Working directory

        Returns:
            (returncode, stdout, stderr)
        """
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timeout"
        except Exception as e:
            return -1, "", str(e)

    def _is_git_repo(self, path: str) -> bool:
        """Check if path is a git repository.

        Args:
            path: Path to check

        Returns:
            True if it's a git repository
        """
        git_dir = Path(path) / '.git'
        return git_dir.exists()

    def _ensure_repo(self, work_dir: str):
        """Ensure git repository exists.

        Args:
            work_dir: Working directory
        """
        work_path = Path(work_dir)

        if self._is_git_repo(work_dir):
            self.logger.info(f"Git repository already exists: {work_dir}")
            return

        # Clone repository
        self.logger.info(f"Cloning Git repository: {self.repo_url}")

        returncode, stdout, stderr = self._run_command(
            ['git', 'clone', self.repo_url, work_dir]
        )

        if returncode != 0:
            self.logger.error(f"Failed to clone repository: {stderr}")
            raise Exception(f"Failed to clone repository: {stderr}")

        self.logger.info("Repository cloned successfully")

    def commit_and_push(self, file_path: str, work_dir: str = "./output", message: str = None) -> bool:
        """Commit and push file to GitHub.

        Args:
            file_path: Path to file to commit
            work_dir: Working directory
            message: Commit message (auto-generate if not provided)

        Returns:
            True if successful
        """
        self.logger.info("Starting to push to GitHub...")

        # Ensure repo exists
        self._ensure_repo(work_dir)

        # Generate commit message if not provided
        if message is None:
            today = datetime.now()
            message = f"Update weekly report {today.strftime('%Y-%m-%d')}"

        # Copy file to work directory if it's not already there
        src_file = Path(file_path)
        dst_file = Path(work_dir) / src_file.name

        if str(src_file.absolute()) != str(dst_file.absolute()):
            shutil.copy2(src_file, dst_file)
            self.logger.info(f"Copied file to: {dst_file}")

        # Git add
        self.logger.info("Running git add...")
        returncode, stdout, stderr = self._run_command(
            ['git', 'add', src_file.name],
            cwd=work_dir
        )

        if returncode != 0:
            self.logger.error(f"git add failed: {stderr}")
            return False

        # Git commit
        self.logger.info(f"Running git commit: {message}")
        returncode, stdout, stderr = self._run_command(
            ['git', 'commit', '-m', message],
            cwd=work_dir
        )

        if returncode != 0:
            if "nothing to commit" in stderr or "nothing to commit" in stdout:
                self.logger.info("Nothing to commit")
                return True
            self.logger.error(f"git commit failed: {stderr}")
            return False

        self.logger.info("Commit successful")

        # Git push
        self.logger.info("Running git push...")
        returncode, stdout, stderr = self._run_command(
            ['git', 'push', 'origin', self.branch],
            cwd=work_dir
        )

        if returncode != 0:
            self.logger.error(f"git push failed: {stderr}")
            return False

        self.logger.info("Push successful!")
        return True

    def commit_and_push_multiple(self, file_paths: list, work_dir: str = "./output",
                                   message: str = None) -> bool:
        """Commit and push multiple files to GitHub.

        Args:
            file_paths: List of file paths to commit
            work_dir: Working directory
            message: Commit message

        Returns:
            True if successful
        """
        self.logger.info(f"Starting to push {len(file_paths)} files to GitHub...")

        # Ensure repo exists
        self._ensure_repo(work_dir)

        # Generate commit message if not provided
        if message is None:
            today = datetime.now()
            message = f"Update weekly report {today.strftime('%Y-%m-%d')}"

        # Copy files to work directory
        for file_path in file_paths:
            src_file = Path(file_path)
            dst_file = Path(work_dir) / src_file.name

            if str(src_file.absolute()) != str(dst_file.absolute()):
                shutil.copy2(src_file, dst_file)
                self.logger.info(f"Copied file to: {dst_file}")

        # Git add all files
        self.logger.info("Running git add...")
        returncode, stdout, stderr = self._run_command(
            ['git', 'add', '.'],
            cwd=work_dir
        )

        if returncode != 0:
            self.logger.error(f"git add failed: {stderr}")
            return False

        # Git commit
        self.logger.info(f"Running git commit: {message}")
        returncode, stdout, stderr = self._run_command(
            ['git', 'commit', '-m', message],
            cwd=work_dir
        )

        if returncode != 0:
            if "nothing to commit" in stderr or "nothing to commit" in stdout:
                self.logger.info("Nothing to commit")
                return True
            self.logger.error(f"git commit failed: {stderr}")
            return False

        self.logger.info("Commit successful")

        # Git push
        self.logger.info("Running git push...")
        returncode, stdout, stderr = self._run_command(
            ['git', 'push', 'origin', self.branch],
            cwd=work_dir
        )

        if returncode != 0:
            self.logger.error(f"git push failed: {stderr}")
            return False

        self.logger.info("Push successful!")
        return True
