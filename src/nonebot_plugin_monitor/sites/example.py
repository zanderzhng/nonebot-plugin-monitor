"""
Example site subscription module for testing.
This demonstrates how to create a site subscription module.
"""

import time
from typing import Any

from .base import BaseSite


class ExampleSite(BaseSite):
    """Example site implementation for testing"""

    def __init__(self):
        """Initialize the example site"""
        super().__init__()
        self.last_check = None

    async def fetch_latest(self) -> Any:
        """
        Fetch latest content from the source (simulated)
        Returns:
            Latest data from the source
        """
        # Load current update count from cache
        cached_data = self.load_cache()
        current_count = cached_data.get("update_count", 0) if cached_data else 0

        # Simulate fetching data - always increment for testing
        self.last_check = time.time()
        new_count = current_count + 1

        # Return simulated data
        return {
            "timestamp": self.last_check,
            "update_count": new_count,
            "title": f"Example Update #{new_count}",
            "content": f"This is example content for update #{new_count}",
        }

    def has_updates(self, cached_data: Any, latest_data: Any) -> bool:
        """
        Compare cached data with latest data to determine if there are updates
        Args:
            cached_data: Previously cached data
            latest_data: Latest data fetched from source
        Returns:
            True if there are updates, False otherwise
        """
        if cached_data is None:
            return True  # No cached data, consider it an update

        # Compare update counts
        cached_count = cached_data.get("update_count", 0)
        latest_count = latest_data.get("update_count", 0)

        return latest_count > cached_count

    def format_notification(self, latest_data: Any) -> str:
        """
        Format the latest data into a notification message
        Args:
            latest_data: Latest data to format
        Returns:
            Formatted notification message
        """
        title = latest_data.get("title", "Unknown Update")
        content = latest_data.get("content", "")
        return f"【示例网站更新】\n{title}\n{content}"

    def get_description(self) -> str:
        """
        Get site description for user display
        Returns:
            Site description
        """
        return "示例网站 - 每10秒更新一次用于测试"

    def get_schedule(self) -> str:
        """
        Get the site's custom fetch schedule (interval format for debugging)
        Returns:
            Interval schedule string (every 10 seconds)
        """
        # Check every 10 seconds for debugging
        return "interval:10"
