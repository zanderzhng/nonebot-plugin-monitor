"""
Template file for creating new site subscription modules.
This file is NOT loaded by the plugin and serves as a copy-paste template.

To create a new site subscription:
1. Copy this file and rename it (e.g., github.py, bilibili.py, etc.)
2. Implement the required functions
3. Create a SiteConfig instance with your functions
4. Restart the bot to load the new site
"""

from typing import Any

import httpx

from . import SiteConfig


async def fetch_template_data():
    """
    Fetch latest content from the source
    Returns:
        Latest data from the source (e.g., dict, list, etc.)
    """
    # Example implementation - replace with your site's logic
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.example.com/latest")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise Exception(f"Failed to fetch from source: {e}")


def compare_template_data(cached_data: Any, latest_data: Any) -> bool:
    """
    Compare cached data with latest data to determine if there are updates
    Args:
        cached_data: Previously cached data
        latest_data: Latest data fetched from source
    Returns:
        True if there are updates, False otherwise
    """
    # Example implementation - replace with your comparison logic
    if cached_data is None:
        return True  # No cached data, consider it an update

    # Compare relevant fields
    return cached_data != latest_data


def format_template_notification(latest_data: Any) -> str:
    """
    Format the latest data into a notification message
    Args:
        latest_data: Latest data to format
    Returns:
        Formatted notification message
    """
    # Example implementation - replace with your formatting logic
    return f"检测到新更新：{latest_data.get('title', 'Unknown')}"


def template_description() -> str:
    """
    Get site description for user display
    Returns:
        Site description
    """
    return "网站描述 - 请替换为实际描述"


def template_schedule() -> str:
    """
    Get the site's custom fetch schedule (cron format)
    Returns:
        Cron schedule string (e.g., "*/30 * * * *" for every 30 minutes)
    """
    # Example: Check every 30 minutes
    return "*/30 * * * *"


# Register the site using the functional configuration
site = SiteConfig(
    name="template",
    fetch_func=fetch_template_data,
    compare_func=compare_template_data,
    format_func=format_template_notification,
    description_func=template_description,
    schedule_func=template_schedule,
)


# This is a template file and is NOT loaded by the plugin
# It's meant to be copied and customized for actual site implementations
