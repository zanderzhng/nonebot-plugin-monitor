import importlib
import inspect
from pathlib import Path

from nonebot import get_bot, logger, require

from .sites.base import BaseSite
from .manager import subscription_manager

# 导入 nonebot 的调度器
scheduler = require("nonebot_plugin_apscheduler").scheduler


class Scheduler:
    def __init__(self):
        """初始化 Scheduler 类
        - 管理网站订阅检查任务
        """
        self.site_modules: dict[str, BaseSite] = {}  # {site_name: site_instance}

    def load_site_modules(self):
        """Load all site subscription modules"""
        sites_dir = Path(__file__).parent / "sites"
        loaded_sites = []

        # Get all Python files in sites directory except template.py and base files
        for file_path in sites_dir.glob("*.py"):
            if file_path.name in ["__init__.py", "base.py", "template.py"]:
                continue

            site_name = file_path.stem
            try:
                # Import the site module using relative import that works in different plugin directories
                module = importlib.import_module(f".sites.{site_name}", package=__package__)
                logger.debug(f"成功导入站点模块: {site_name}")

                # Find the site class (should be the only class that inherits from BaseSite)
                site_class = None
                logger.debug(f"检查模块 {module.__name__} 中的类")

                # Get only classes defined in this module (not imported ones)
                import inspect
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Check if it's a class defined in this module that inherits from BaseSite but is not BaseSite itself
                    if obj.__module__ == module.__name__ and issubclass(obj, BaseSite) and obj != BaseSite:
                        logger.debug(f"找到站点类: {name}")
                        # Validate that all required methods are implemented (not abstract)
                        required_methods = ['fetch_latest', 'has_updates', 'format_notification', 'get_description', 'get_schedule']
                        all_methods_implemented = True

                        for method_name in required_methods:
                            if not hasattr(obj, method_name):
                                logger.debug(f"类 {name} 缺少方法 {method_name}")
                                all_methods_implemented = False
                                break

                            # Check if method is abstract (raises NotImplementedError)
                            method = getattr(obj, method_name)
                            if hasattr(method, '__isabstractmethod__') and method.__isabstractmethod__:
                                logger.debug(f"类 {name} 的方法 {method_name} 是抽象方法")
                                all_methods_implemented = False
                                break

                        if all_methods_implemented:
                            site_class = obj
                            logger.debug(f"类 {name} 继承自 BaseSite 且实现了所有必需方法")
                            break
                        else:
                            logger.debug(f"类 {name} 未实现所有必需方法")

                if site_class:
                    # Create instance of the site class
                    site_instance = site_class()

                    # Register with scheduler
                    self.site_modules[site_name] = site_instance

                    # Start scheduling for this site
                    self.start_site_scheduling(site_name)

                    loaded_sites.append(site_name)
                    logger.info(f"成功加载站点模块: {site_name}")
                else:
                    logger.warning(f"站点模块 {site_name} 中未找到有效的站点类")

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
        if site_name not in self.site_modules:
            logger.error(f"站点 {site_name} 未注册")
            return

        site_instance = self.site_modules[site_name]
        try:
            # Get schedule from site
            schedule = site_instance.get_schedule()

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
        Check for updates from a specific site
        Args:
            site_name: Name of the site to check
        """
        if site_name not in self.site_modules:
            logger.error(f"站点 {site_name} 未注册")
            return

        site_instance = self.site_modules[site_name]
        try:
            logger.debug(f"开始检查站点 {site_name} 的更新")

            # Load cached data
            cached_data = site_instance.load_cache()

            # Fetch latest data
            latest_data = await site_instance.fetch_latest()

            # Check for updates
            if site_instance.has_updates(cached_data, latest_data):
                logger.info(f"站点 {site_name} 检测到更新")

                # Format notification
                notification = site_instance.format_notification(latest_data)

                # Get subscribers
                subscribers = subscription_manager.get_subscribers(site_name)

                # Send notifications to all subscribers
                if subscribers:
                    await self._send_notifications(subscribers, notification)
                else:
                    logger.debug(f"站点 {site_name} 没有订阅者")

                # Save new data to cache
                site_instance.save_cache(latest_data)
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
