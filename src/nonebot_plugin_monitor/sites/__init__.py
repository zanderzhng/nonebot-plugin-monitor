from abc import ABC, abstractmethod
from typing import Any


class BaseSite(ABC):
    """Base class for all site modules"""

    @abstractmethod
    async def fetch_latest(self) -> Any:
        """
        Fetch latest content from the source
        Returns:
            Latest data from the source
        """
        pass

    @abstractmethod
    def has_updates(self, cached_data: Any, latest_data: Any) -> bool:
        """
        Compare cached data with latest data to determine if there are updates
        Args:
            cached_data: Previously cached data
            latest_data: Latest data fetched from source
        Returns:
            True if there are updates, False otherwise
        """
        pass

    @abstractmethod
    def format_notification(self, latest_data: Any) -> str:
        """
        Format the latest data into a notification message
        Args:
            latest_data: Latest data to format
        Returns:
            Formatted notification message
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """
        Get site description for user display
        Returns:
            Site description
        """
        pass

    @abstractmethod
    def get_schedule(self) -> str:
        """
        Get the site's custom fetch schedule (cron format)
        Returns:
            Cron schedule string (e.g., "*/30 * * * *" for every 30 minutes)
        """
        pass

    def get_name(self) -> str:
        """
        Get site name (default implementation)
        Returns:
            Site module name
        """
        return self.__class__.__module__.split(".")[-1]


# Site interface definition
Site = BaseSite
