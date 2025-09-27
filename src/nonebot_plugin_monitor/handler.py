from nonebot import on_command
from nonebot.adapters import Bot, Event
from nonebot_plugin_uninfo import Uninfo

from .manager import subscription_manager
from .scheduler import scheduler_instance

# 订阅相关命令处理器
subscribe_cmd = on_command("订阅", priority=5)
unsubscribe_cmd = on_command("取消订阅", priority=5)
list_subscriptions_cmd = on_command("订阅列表", priority=5)


@subscribe_cmd.handle()
async def handle_subscribe(bot: Bot, event: Event, uninfo: Uninfo):
    """处理订阅命令"""
    # Extract site name from command arguments (remove command itself)
    message = str(event.get_message()).strip()
    if message.startswith("/订阅 "):
        args = message[4:].strip()  # Remove "/订阅 " prefix (including space)
    elif message == "/订阅":
        args = ""
    else:
        args = message

    if not args:
        await subscribe_cmd.finish("请指定要订阅的网站名称")
        return

    # 获取用户/群组ID
    is_group = False
    if hasattr(event, "group_id") and event.group_id:
        target_id = str(event.group_id)
        is_group = True
        target_type = "群组"
    else:
        target_id = str(event.get_user_id())
        target_type = "用户"

    # Convert display name to internal site name
    site_name = scheduler_instance.get_site_name_by_display_name(args)

    # 订阅站点
    success = subscription_manager.subscribe(target_id, site_name, is_group)

    if success:
        await subscribe_cmd.finish(f"{target_type} {target_id} 已订阅 {args}")
    else:
        await subscribe_cmd.finish(f"{target_type} {target_id} 订阅 {args} 失败")


@unsubscribe_cmd.handle()
async def handle_unsubscribe(bot: Bot, event: Event, uninfo: Uninfo):
    """处理取消订阅命令"""
    # Extract site name from command arguments (remove command itself)
    message = str(event.get_message()).strip()
    if message.startswith("/取消订阅 "):
        args = message[6:].strip()  # Remove "/取消订阅 " prefix (including space)
    elif message == "/取消订阅":
        args = ""
    else:
        args = message

    if not args:
        await unsubscribe_cmd.finish("请指定要取消订阅的网站名称")
        return

    # 获取用户/群组ID
    is_group = False
    if hasattr(event, "group_id") and event.group_id:
        target_id = str(event.group_id)
        is_group = True
        target_type = "群组"
    else:
        target_id = str(event.get_user_id())
        target_type = "用户"

    # Convert display name to internal site name
    site_name = scheduler_instance.get_site_name_by_display_name(args)

    # 取消订阅站点
    success = subscription_manager.unsubscribe(target_id, site_name, is_group)

    if success:
        await unsubscribe_cmd.finish(f"{target_type} {target_id} 已取消订阅 {args}")
    else:
        await unsubscribe_cmd.finish(f"{target_type} {target_id} 未订阅 {args} 或取消订阅失败")


@list_subscriptions_cmd.handle()
async def handle_list_subscriptions(bot: Bot, event: Event, uninfo: Uninfo):
    """处理列出订阅命令"""
    # 获取用户/群组ID
    is_group = False
    if hasattr(event, "group_id") and event.group_id:
        target_id = str(event.group_id)
        is_group = True
    else:
        target_id = str(event.get_user_id())

    # 获取用户的订阅
    user_subscriptions = subscription_manager.get_subscriptions(target_id, is_group)

    # 获取所有可用的站点
    available_sites = list(scheduler_instance.site_configs.keys())

    # 创建消息
    if not available_sites:
        message = "暂无可用的订阅源"
    else:
        message = "订阅列表:\n"

        # 显示已订阅的站点
        if user_subscriptions:
            message += "已订阅:\n"
            for site in user_subscriptions:
                if site in scheduler_instance.site_configs:
                    display_name = scheduler_instance.site_configs[site].display_name()
                    description = scheduler_instance.site_configs[site].description()
                    message += f"✓ {display_name} - {description}\n"
                else:
                    message += f"✓ {site} - (描述不可用)\n"
            message += "\n"

        # 显示未订阅的站点
        unsubscribed_sites = [site for site in available_sites if site not in user_subscriptions]
        if unsubscribed_sites:
            message += "未订阅:\n"
            for site in unsubscribed_sites:
                if site in scheduler_instance.site_configs:
                    display_name = scheduler_instance.site_configs[site].display_name()
                    description = scheduler_instance.site_configs[site].description()
                    message += f"○ {display_name} - {description}\n"
                else:
                    message += f"○ {site} - (描述不可用)\n"

    await list_subscriptions_cmd.finish(message)
