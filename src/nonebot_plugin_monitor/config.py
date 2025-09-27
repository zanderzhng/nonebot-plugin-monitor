from pathlib import Path

from nonebot import get_driver
from nonebot.compat import model_dump

# Import localstore for subscription data paths
from nonebot_plugin_localstore import get_plugin_cache_dir, get_plugin_data_file
from pydantic import BaseModel, ConfigDict, Field


class Config(BaseModel):
    """Plugin configuration for subscription functionality"""

    # 订阅数据存储路径 (using localstore)
    subscriptions_data_file: Path = Field(default_factory=lambda: get_plugin_data_file("subscriptions.json"))

    # 缓存目录路径 (using localstore)
    cache_dir: Path = Field(default_factory=get_plugin_cache_dir)

    model_config = ConfigDict(extra="ignore")


driver = get_driver()
global_config = model_dump(driver.config) if hasattr(driver.config, "__dict__") else {}
plugin_config = Config.model_validate(global_config)
