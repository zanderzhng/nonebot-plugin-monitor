from abc import ABC
import json
from typing import Any

from nonebot_plugin_localstore import get_plugin_cache_dir


class BaseSite(ABC):
    """Base class for site implementations"""

    def __init__(self):
        """Initialize base site"""
        self.site_name = self.__class__.__name__.lower()
        # Use localstore for cache directory
        cache_dir = get_plugin_cache_dir()
        self.cache_file = cache_dir / f"{self.site_name}_subscription.json"

    async def fetch_latest(self) -> Any:
        """
        Fetch latest content from the source
        Returns:
            Latest data from the source
        """
        raise NotImplementedError("Subclasses must implement fetch_latest method")

    def has_updates(self, cached_data: Any, latest_data: Any) -> bool:
        """
        Compare cached data with latest data to determine if there are updates
        Args:
            cached_data: Previously cached data
            latest_data: Latest data fetched from source
        Returns:
            True if there are updates, False otherwise
        """
        raise NotImplementedError("Subclasses must implement has_updates method")

    def format_notification(self, latest_data: Any) -> str:
        """
        Format the latest data into a notification message
        Args:
            latest_data: Latest data to format
        Returns:
            Formatted notification message
        """
        raise NotImplementedError("Subclasses must implement format_notification method")

    def get_description(self) -> str:
        """
        Get site description for user display
        Returns:
            Site description
        """
        raise NotImplementedError("Subclasses must implement get_description method")

    def get_schedule(self) -> str:
        """
        Get the site's custom fetch schedule (cron format)
        Returns:
            Cron schedule string (e.g., "*/30 * * * *" for every 30 minutes)
        """
        raise NotImplementedError("Subclasses must implement get_schedule method")

    def get_name(self) -> str:
        """
        Get site name
        Returns:
            Site name
        """
        return self.site_name

    def load_cache(self) -> Any:
        """
        Load cached data from file
        Returns:
            Cached data or None if not found
        """
        try:
            if self.cache_file.exists():
                with open(self.cache_file, encoding="utf-8") as f:
                    return json.load(f)
            return None
        except Exception:
            return None

    def save_cache(self, data: Any) -> bool:
        """
        Save data to cache file
        Args:
            data: Data to cache
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
