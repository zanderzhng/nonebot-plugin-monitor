import importlib
from pathlib import Path

from nonebot import get_bot, logger, require

from .cache import load_cache, save_cache
from .manager import subscription_manager
from .sites import SiteConfig

# 导入 nonebot 的调度器
scheduler = require("nonebot_plugin_apscheduler").scheduler


class Scheduler:
    def __init__(self):
        """初始化 Scheduler 类
        - 管理网站订阅检查任务
        """
        self.site_configs: dict[str, SiteConfig] = {}  # {site_name: site_config}

    def load_site_modules(self):
        """Load all site subscription modules using functional approach"""
        sites_dir = Path(__file__).parent / "sites"
        loaded_sites = []

        # Get all Python files in sites directory except template.py and __init__.py
        for file_path in sites_dir.glob("*.py"):
            if file_path.name in ["__init__.py", "template.py"]:
                continue

            site_name = file_path.stem
            try:
                # Import the site module using relative import that works in different plugin directories
                module = importlib.import_module(f".sites.{site_name}", package=__package__)
                logger.debug(f"成功导入站点模块: {site_name}")

                # Look for the 'site' attribute which should be a SiteConfig
                if hasattr(module, "site") and isinstance(module.site, SiteConfig):
                    # Register with scheduler
                    self.site_configs[site_name] = module.site

                    # Start scheduling for this site
                    self.start_site_scheduling(site_name)

                    loaded_sites.append(site_name)
                    logger.info(f"成功加载站点模块: {site_name}")
                else:
                    logger.warning(f"站点模块 {site_name} 中未找到有效的 SiteConfig")

            except Exception as e:
                logger.error(f"加载站点模块 {site_name} 失败: {e}")

        logger.info(f"已加载 {len(loaded_sites)} 个站点模块: {', '.join(loaded_sites) if loaded_sites else '无'}")
        return loaded_sites

    def start_site_scheduling(self, site_name: str):
        """
        Start scheduling for a specific site
        Args:
            site_name: Name of the site to schedule
        """
        if site_name not in self.site_configs:
            logger.error(f"站点 {site_name} 未注册")
            return

        site_config = self.site_configs[site_name]
        try:
            # Get schedule from site
            schedule = site_config.schedule()

            # Create job ID
            job_id = f"site_check_{site_name}"

            # Check if schedule is a special debug interval (starts with "interval:")
            if schedule.startswith("interval:"):
                # Parse interval (e.g., "interval:10" for 10 seconds)
                interval_seconds = int(schedule.split(":")[1])

                # Add interval job to scheduler
                scheduler.add_job(
                    self.check_site_updates,
                    "interval",
                    id=job_id,
                    seconds=interval_seconds,
                    args=[site_name],
                )

                logger.info(f"已为站点 {site_name} 启动调试任务: 每 {interval_seconds} 秒")
            else:
                # Parse cron expression
                cron_parts = schedule.split()
                if len(cron_parts) != 5:
                    logger.error(f"站点 {site_name} 的调度表达式格式错误: {schedule}")
                    return

                minute, hour, day, month, day_of_week = cron_parts

                # Add job to scheduler
                scheduler.add_job(
                    self.check_site_updates,
                    "cron",
                    id=job_id,
                    minute=minute,
                    hour=hour,
                    day=day,
                    month=month,
                    day_of_week=day_of_week,
                    args=[site_name],
                )

                logger.info(f"已为站点 {site_name} 启动定时任务: {schedule}")
        except Exception as e:
            logger.error(f"为站点 {site_name} 启动定时任务失败: {e}")

    async def check_site_updates(self, site_name: str):
        """
        Check for updates from a specific site using functional approach
        Args:
            site_name: Name of the site to check
        """
        if site_name not in self.site_configs:
            logger.error(f"站点 {site_name} 未注册")
            return

        site_config = self.site_configs[site_name]
        try:
            logger.debug(f"开始检查站点 {site_name} 的更新")

            # Load cached data using cache module
            cached_data = load_cache(site_name)

            # Fetch latest data using site's fetch function
            latest_data = await site_config.fetch()

            # Check for updates using site's compare function
            if site_config.compare(cached_data, latest_data):
                logger.info(f"站点 {site_name} 检测到更新")

                # Format notification using site's format function
                notification = site_config.format(latest_data)

                # Get subscribers
                subscribers = subscription_manager.get_subscribers(site_name)

                # Send notifications to all subscribers
                if subscribers:
                    await self._send_notifications(subscribers, notification)
                else:
                    logger.debug(f"站点 {site_name} 没有订阅者")

                # Save new data to cache using cache module
                save_cache(site_name, latest_data)
            else:
                logger.debug(f"站点 {site_name} 无更新")

        except Exception as e:
            logger.error(f"检查站点 {site_name} 更新时出错: {e}")

    async def _send_notifications(self, subscribers: list[str], message: str):
        """
        Send notifications to subscribers
        Args:
            subscribers: List of subscriber IDs
            message: Notification message
        """
        try:
            bot = get_bot()
            for subscriber_id in subscribers:
                try:
                    # Try to send as group message first
                    await bot.send_group_msg(group_id=int(subscriber_id), message=message)
                    logger.debug(f"已向群组 {subscriber_id} 发送通知")
                except ValueError:
                    # If not a valid group ID, try as private message
                    try:
                        await bot.send_private_msg(user_id=int(subscriber_id), message=message)
                        logger.debug(f"已向用户 {subscriber_id} 发送通知")
                    except Exception as e:
                        logger.error(f"向订阅者 {subscriber_id} 发送通知失败: {e}")
                except Exception as e:
                    logger.error(f"向订阅者 {subscriber_id} 发送通知失败: {e}")
        except Exception as e:
            logger.error(f"发送通知时出错: {e}")


# 创建 Scheduler 实例
scheduler_instance = Scheduler()
