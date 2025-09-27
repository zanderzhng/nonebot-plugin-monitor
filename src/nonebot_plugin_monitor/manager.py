import json

from nonebot import logger

from .config import plugin_config


class SubscriptionManager:
    """Manage user/group subscriptions to websites"""

    def __init__(self):
        """Initialize subscription manager"""
        self.data_file = plugin_config.subscriptions_data_file
        self.subscriptions: dict[str, list[str]] = {}  # {user/group id: [site names]}

    async def initialize(self):
        """Initialize subscription manager"""
        self.load_subscriptions()
        logger.info("订阅管理器初始化完成")

    def load_subscriptions(self):
        """Load subscriptions from file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, encoding="utf-8") as f:
                    self.subscriptions = json.load(f)
                logger.info(f"已加载 {len(self.subscriptions)} 个订阅")
            else:
                self.subscriptions = {}
                self.save_subscriptions()
                logger.info("创建新的订阅数据文件")
        except Exception as e:
            logger.error(f"加载订阅数据失败: {e}")
            self.subscriptions = {}

    def save_subscriptions(self):
        """Save subscriptions to file"""
        try:
            # Ensure directory exists
            self.data_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.subscriptions, f, ensure_ascii=False, indent=2)
            logger.debug("订阅数据已保存")
        except Exception as e:
            logger.error(f"保存订阅数据失败: {e}")

    def subscribe(self, user_id: str, site_name: str) -> bool:
        """
        Subscribe user/group to a site
        Args:
            user_id: User or group ID
            site_name: Site name to subscribe to
        Returns:
            True if successful, False otherwise
        """
        try:
            if user_id not in self.subscriptions:
                self.subscriptions[user_id] = []

            if site_name not in self.subscriptions[user_id]:
                self.subscriptions[user_id].append(site_name)
                self.save_subscriptions()
                logger.info(f"用户/群组 {user_id} 订阅了 {site_name}")
                return True
            else:
                logger.info(f"用户/群组 {user_id} 已经订阅了 {site_name}")
                return False
        except Exception as e:
            logger.error(f"订阅失败: {e}")
            return False

    def unsubscribe(self, user_id: str, site_name: str) -> bool:
        """
        Unsubscribe user/group from a site
        Args:
            user_id: User or group ID
            site_name: Site name to unsubscribe from
        Returns:
            True if successful, False otherwise
        """
        try:
            if user_id in self.subscriptions and site_name in self.subscriptions[user_id]:
                self.subscriptions[user_id].remove(site_name)

                # Clean up empty subscriptions
                if not self.subscriptions[user_id]:
                    del self.subscriptions[user_id]

                self.save_subscriptions()
                logger.info(f"用户/群组 {user_id} 取消订阅了 {site_name}")
                return True
            else:
                logger.info(f"用户/群组 {user_id} 未订阅 {site_name}")
                return False
        except Exception as e:
            logger.error(f"取消订阅失败: {e}")
            return False

    def get_subscriptions(self, user_id: str) -> list[str]:
        """
        Get user/group subscriptions
        Args:
            user_id: User or group ID
        Returns:
            List of subscribed site names
        """
        return self.subscriptions.get(user_id, [])

    def get_subscribers(self, site_name: str) -> list[str]:
        """
        Get all subscribers for a site
        Args:
            site_name: Site name
        Returns:
            List of user/group IDs subscribed to the site
        """
        subscribers = []
        for user_id, sites in self.subscriptions.items():
            if site_name in sites:
                subscribers.append(user_id)
        return subscribers

    def get_all_subscriptions(self) -> dict[str, list[str]]:
        """
        Get all subscriptions
        Returns:
            Dictionary of all subscriptions
        """
        return self.subscriptions


# Create global subscription manager instance
subscription_manager = SubscriptionManager()
