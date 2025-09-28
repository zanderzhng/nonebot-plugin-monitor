"""Test for the '全部' (all) subscription functionality"""

from nonebug import App
import pytest


@pytest.mark.asyncio
async def test_all_subscription_functionality(app: App):
    """Test that the subscription manager properly handles 'all' subscriptions"""
    from nonebot_plugin_monitor.manager import SubscriptionManager

    # Create a temporary subscription manager
    manager = SubscriptionManager()
    manager.subscriptions = {}

    # Test subscribing to "全部"
    result = manager.subscribe("test_user_1", "全部", False)
    assert result is True, "Should be able to subscribe to 全部"

    # Check that the subscription was recorded correctly
    assert "all" in manager.subscriptions, "Should have 'all' key in subscriptions"
    assert "test_user_1" in manager.subscriptions["all"]["users"], "User should be in all users list"

    # Test that get_subscriptions converts "all" back to "全部"
    subscriptions = manager.get_subscriptions("test_user_1", False)
    assert "全部" in subscriptions, "Should show 全部 in user subscriptions"

    # Test that get_subscribers includes "all" subscribers when getting subscribers for any site
    subscribers = manager.get_subscribers("example")
    assert "test_user_1" in subscribers, "User subscribed to all should receive notifications for example site"

    # Test unsubscribing from "全部"
    result = manager.unsubscribe("test_user_1", "全部", False)
    assert result is True, "Should be able to unsubscribe from 全部"

    # Check that the subscription was removed
    if "all" in manager.subscriptions:
        assert "test_user_1" not in manager.subscriptions["all"]["users"], "User should be removed from all users list"
