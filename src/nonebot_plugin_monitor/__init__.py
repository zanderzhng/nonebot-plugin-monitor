from nonebot import get_driver, logger
from nonebot.plugin import PluginMetadata

from . import handler as handler  # Import handler to register command handlers
from .manager import subscription_manager
from .scheduler import scheduler_instance

__plugin_meta__ = PluginMetadata(
    name="网站订阅插件",
    description="订阅不同网站的更新并推送给用户",
    usage="""
    订阅命令：
    - /订阅列表: 查看可订阅的网站列表
    - /订阅 <网站名>: 订阅指定网站
    - /取消订阅 <网站名>: 取消订阅指定网站
    """,
    type="application",
    homepage="https://github.com/zanderzhng/nonebot-plugin-monitor",
    supported_adapters=None,
)

# 获取驱动以访问全局配置
driver = get_driver()


@driver.on_startup
async def plugin_init():
    """
    插件初始化函数
    执行必要的初始化检查和配置
    """

    logger.info("网站订阅插件正在初始化...")

    # 初始化订阅管理器
    try:
        await subscription_manager.initialize()
        logger.success("订阅管理器初始化完成")
    except Exception as e:
        logger.error(f"订阅管理器初始化失败: {e}")

    # 加载网站订阅模块
    try:
        loaded_sites = scheduler_instance.load_site_modules()
        logger.success(f"网站订阅模块加载完成，共加载 {len(loaded_sites)} 个站点")
    except Exception as e:
        logger.error(f"网站订阅模块加载失败: {e}")

    logger.success("网站订阅插件初始化完成")


@driver.on_shutdown
async def plugin_shutdown():
    """
    插件关闭函数
    执行必要的清理工作
    """
    logger.info("网站订阅插件正在关闭...")
    logger.info("网站订阅插件已关闭")


# Bot连接和断开连接的处理
@driver.on_bot_connect
async def handle_connect(bot):
    logger.success(f"Bot {bot.self_id} 已连接")


@driver.on_bot_disconnect
async def handle_disconnect(bot):
    logger.warning(f"Bot {bot.self_id} 已断开连接")
